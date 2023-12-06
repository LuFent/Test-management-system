from test_management_system.celery import app
from .models import ProjectVersion, TestFile, ProjectTest, TestStep, AutoTestStep
import os
from django.db import connection
from shutil import rmtree
from .tools import (
    clone_features,
    get_features,
    get_updated_tests_objects,
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
    del_reserve_repo,
    fetch_version_files_with_auto_test,
    fetch_file_with_autotests,
    get_autotest_updated_steps,
    STEP_TYPES_CODES,
    sync_features_with_file,
    fetch_with_autotests,
    split_common_autotests_folder_filed

)
from django.conf import settings
from os.path import join
from django.db.models import Prefetch
from django.core.exceptions import ObjectDoesNotExist
from .auto_test_plugins import CypressCucumberPreprocessorPlugin
from pathlib import Path

ccp_plugin = CypressCucumberPreprocessorPlugin()

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
    common_autotests_folders = project.common_autotests_folders

    if smart_mode and particular_dir and common_autotests_folders:
        common_autotests_folders = [get_common_folder_path(
            repo_path, particular_dir, common_autotests_folder
        ) for common_autotests_folder in split_common_autotests_folder_filed(common_autotests_folders)]

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
        features = get_features(repo_path)
        new_test_files, new_project_tests, new_test_steps = get_new_tests_objects(
            features, version
        )
    except Exception as e:
        version.error_message = get_version_creation_error("Something went wrong")
        version.save()
        return
    files = TestFile.objects.bulk_create(new_test_files)
    tests = ProjectTest.objects.bulk_create(new_project_tests)
    steps = TestStep.objects.bulk_create(new_test_steps)

    if smart_mode:
        fetch_with_autotests(common_autotests_folders, files, repo_path, version)

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
    common_autotests_folders = project.common_autotests_folders

    if smart_mode and particular_dir and common_autotests_folders:
        common_autotests_folders = [get_common_folder_path(
            repo_path, particular_dir, common_autotests_folder
        ) for common_autotests_folder in split_common_autotests_folder_filed(common_autotests_folders)]

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
        features = get_features(repo_path)
    except Exception as e:
        version.error_message = get_version_update_error(str(e))
        version.save()
        unreserve_repo(repo_path)
        return

    files = []
    cursor = connection.cursor()
    for feature in features:
        try:
            test_file = sync_features_with_file(feature, version_id, cursor)
            files.append(test_file)
        except Exception:
            pass

    if smart_mode:
        version.auto_test_steps.all().delete()
        fetch_with_autotests(common_autotests_folders, files, repo_path, version)
        for test_file in files:
            fetch_file_with_autotests(test_file)
            steps = get_autotest_updated_steps(test_file)
            TestStep.objects.bulk_update(steps, ["has_auto_test"])

    version.error_message = None
    version.save()
    del_reserve_repo(repo_path)


@app.task
def push_test_files(repo_path,
                    username,
                    token,
                    branch,
                    repo_url,
                    version_id,
                    commit_email,
                    commit_username):
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
    status, data = push_files(repo_path, commit_message, commit_email, commit_username)
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
