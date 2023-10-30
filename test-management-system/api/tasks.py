from test_management_system.celery import app
from .models import ProjectVersion, TestFile, ProjectTest, TestStep
import os
from shutil import rmtree
from .tools import (
    clone_features,
    get_features,
    get_updated_tests_objcts,
    get_new_tests_objects,
    reserve_repo,
    unreserve_repo,
    get_version_creation_error,
    get_version_update_error,
    get_files_push_error,
    get_pushing_repo_path,
    copy_files_to_dir,
    push_files,
    remove_repo,
    get_common_folder_path,
    get_commit_message,
)
from django.conf import settings
from os.path import join
from django.db.models import Prefetch
from django.core.exceptions import ObjectDoesNotExist


@app.task
def create_version(repo_path, username, token, branch, commit, repo_url, version_id):
    try:
        version = ProjectVersion.objects.get(id=version_id)
    except ObjectDoesNotExist:
        return
    project = version.project

    if os.path.isdir(repo_path):
        rmtree(repo_path)

    smart_mode = project.smart_mode
    particular_dir = project.files_folder
    common_autotests_folder = project.common_autotests_folder

    if smart_mode and particular_dir and common_autotests_folder:
        common_autotests_folder = get_common_folder_path(
            repo_path, particular_dir, common_autotests_folder
        )
    try:
        status, data = clone_features(
            repo_url=repo_url,
            username=username,
            token=token,
            repo_path=repo_path,
            branch=branch,
            commit=commit,
            particular_dir=particular_dir,
            smart_mode=smart_mode,
        )

        if not status:
            version.error_message = get_version_creation_error(data)
            version.save()
            return

    except Exception as e:
        version.error_message = get_version_creation_error("Something went wrong")
        version.save()
        return

    commit_hash = data

    if not commit:
        version.commit_hash = commit_hash
        version.save()
    try:
        features = get_features(repo_path, smart_mode, common_autotests_folder)
        new_test_files, new_project_tests, new_test_steps = get_new_tests_objects(
            features, version
        )
    except Exception as e:
        version.error_message = get_version_creation_error("Something went wrong")
        version.save()
        return
    TestFile.objects.bulk_create(new_test_files)
    ProjectTest.objects.bulk_create(new_project_tests)
    TestStep.objects.bulk_create(new_test_steps)
    version.error_message = None
    version.save()


@app.task
def update_version(repo_path, username, token, branch, repo_url, version_id):
    version = (
        ProjectVersion.objects.filter(id=version_id)
        .select_related("project")
        .prefetch_related(
            Prefetch(
                "test_files",
                queryset=TestFile.objects.prefetch_related(
                    Prefetch(
                        "tests",
                        queryset=ProjectTest.objects.prefetch_related(
                            Prefetch("steps", queryset=TestStep.objects.all())
                        ),
                    )
                ),
            )
        )
        .first()
    )
    reserve_repo(repo_path)
    project = version.project
    smart_mode = project.smart_mode
    particular_dir = project.files_folder
    common_autotests_folder = project.common_autotests_folder

    if smart_mode and particular_dir and common_autotests_folder:
        common_autotests_folder = join(
            repo_path,
            particular_dir,
            common_autotests_folder,
        )
    try:
        status, data = clone_features(
            repo_url=repo_url,
            username=username,
            token=token,
            repo_path=repo_path,
            branch=branch,
            particular_dir=particular_dir,
            smart_mode=smart_mode,
        )

        if not status:
            version.error_message = get_version_update_error(data)
            version.save()
            unreserve_repo(repo_path)
            return

    except Exception as e:
        version.error_message = get_version_update_error("Something went wrong")
        version.save()
        unreserve_repo(repo_path)
        return

    commit_hash = data
    version.commit_hash = commit_hash
    version.save()

    try:
        features = get_features(repo_path, smart_mode, common_autotests_folder)
        (
            updated_test_files,
            new_project_tests,
            updated_project_tests,
            updated_test_steps,
        ) = get_updated_tests_objcts(features, version)
    except Exception as e:
        version.error_message = get_version_update_error("Something went wrong")
        version.save()
        unreserve_repo(repo_path)
        return

    TestFile.objects.bulk_create(updated_test_files)
    ProjectTest.objects.bulk_create(new_project_tests)
    ProjectTest.objects.bulk_update(updated_project_tests, ["last_line", "start_line"])
    TestStep.objects.bulk_create(updated_test_steps)
    version.error_message = None
    version.save()


@app.task
def push_test_files(repo_path, username, token, branch, repo_url, version_id):
    try:
        version = ProjectVersion.objects.get(id=version_id)
    except ObjectDoesNotExist:
        return

    files_to_push = version.test_files.filter(manually_created=True)
    if not files_to_push.exists():
        version.error_message = None
        version.save()
        return

    commit_message = get_commit_message(files_to_push)
    repo_path = get_pushing_repo_path(repo_path)
    project = version.project

    remove_repo(repo_path)

    particular_dir = project.files_folder

    try:
        status, data = clone_features(
            repo_url=repo_url,
            username=username,
            token=token,
            repo_path=repo_path,
            branch=branch,
            commit=None,
            particular_dir=particular_dir,
            smart_mode=False,
        )

        if not status:
            version.error_message = get_files_push_error(data)
            version.save()
            remove_repo(repo_path)
            return

    except Exception as e:
        version.error_message = get_files_push_error("Something went wrong")
        version.save()
        remove_repo(repo_path)
        return

    copy_files_to_dir(files_to_push, os.path.join(repo_path, particular_dir))
    status, data = push_files(repo_path, commit_message)
    if not status:
        version.error_message = get_files_push_error(data)
        version.save()
        remove_repo(repo_path)
        return

    for file in files_to_push:
        file.manually_created = False

    TestFile.objects.bulk_update(files_to_push, ["manually_created"])
    version.error_message = None
    version.save()
    remove_repo(repo_path)
