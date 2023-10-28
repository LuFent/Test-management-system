from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser
from rest_framework.views import APIView
from .serializers import (
    CreateProjectSerializer,
    BigVersionSerializer,
    GetProjectSerializer,
    VersionSerializer,
    ProjectTestSerializer,
    ProjectTestStatusSerializer,
    SmallVersionSerializer,
    NewFileSerializer,
    FileNameAndTextSerializer,
)
from datetime import date
from .models import Project, ProjectVersion, TestFile, ProjectTest, TestStep
from rest_framework.generics import (
    RetrieveAPIView,
    UpdateAPIView,
    DestroyAPIView,
    CreateAPIView,
)
from django.db import connection, reset_queries
from django.db.models import Count, Q, Sum, F, ExpressionWrapper, DecimalField
from django.db.models import Prefetch
from .tasks import create_version, update_version, push_test_files
from django.conf import settings
from pprint import pprint
import os
from rest_framework import status
from django.shortcuts import get_object_or_404, HttpResponse
from .tools import (
    get_repo_path,
    get_features_from_file,
    get_new_tests_objects,
    get_common_folder_path,
    rename_file_hard,
    get_updated_tests_objcts,
    get_deleted_tests_objects_from_file,
    bulk_delete,
    check_for_similar_test_names,
)


class CreateProject(APIView):
    permission_classes = [
        IsAdminUser,
    ]

    def post(self, request):
        creation_date = date.today()
        data = request.data
        data["creation_date"] = creation_date
        serializer = CreateProjectSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.validated_data, status=status.HTTP_201_CREATED)


class CreateVersion(APIView):
    def post(self, request):
        data = request.data

        branch = data.get("branch")
        if not branch:
            data["branch"] = "main"

        commit_hash = data.get("commit_hash")
        data["commit_hash"] = commit_hash

        serializer = VersionSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        version = serializer.save()

        project = version.project
        branch = version.branch
        commit = version.commit_hash

        repo_url = project.repo_url
        username = project.git_username
        token = project.git_access_key
        repo_path = get_repo_path(project.id, version.id)
        try:
            create_version.delay(
                repo_path=repo_path,
                username=username,
                token=token,
                branch=branch,
                commit=commit,
                repo_url=repo_url,
                version_id=version.id,
            )
        except Exception as e:
            return Response(
                {"message": "Something went wrong"}, status=status.HTTP_400_BAD_REQUEST
            )

        return Response({"message": "accepted"})


class UpdateVersion(APIView):
    def post(self, request):
        data = request.data

        version_id = data.get("version_id")
        if not version_id:
            return Response("No version_id specified")

        version = get_object_or_404(ProjectVersion, id=version_id)

        project = version.project
        repo_url = project.repo_url
        username = project.git_username
        token = project.git_access_key
        branch = version.branch

        repo_path = get_repo_path(project.id, version.id)

        try:
            update_version.delay(
                repo_path=repo_path,
                username=username,
                token=token,
                branch=branch,
                repo_url=repo_url,
                version_id=version.id,
            )
        except Exception as e:
            return Response(
                {"message": "Something went wrong"}, status=status.HTTP_400_BAD_REQUEST
            )

        return Response({"message": "accepted"})


class PushFiles(APIView):
    def post(self, request):
        data = request.data

        version_id = data.get("version_id")
        if not version_id:
            return Response("No version_id specified")
        version = get_object_or_404(ProjectVersion, id=version_id)
        project = version.project
        username = project.git_username
        token = project.git_access_key
        branch = version.branch
        repo_url = project.repo_url

        repo_path = get_repo_path(project.id, version.id)

        try:
            push_test_files.delay(
                repo_path=repo_path,
                username=username,
                token=token,
                branch=branch,
                repo_url=repo_url,
                version_id=version.id,
            )
        except Exception as e:
            return Response(
                {"message": "Something went wrong"}, status=status.HTTP_400_BAD_REQUEST
            )

        return Response({"message": "accepted"})


class GetProject(RetrieveAPIView):
    serializer_class = GetProjectSerializer
    lookup_field = "id"
    queryset = Project.objects.all()


class GetFileText(APIView):
    def get(self, request, file_id):
        file = get_object_or_404(TestFile, id=file_id)
        file_text = open(file.file_path, "rb").read()
        reponse = HttpResponse(file_text, content_type="text/plain; charset=UTF-8")
        return reponse


class GetVersion(RetrieveAPIView):
    serializer_class = BigVersionSerializer
    lookup_field = "id"
    queryset = ProjectVersion.objects.all()


class GetVersionWithCoverage(APIView):
    def get(self, request, version_id):
        version = ProjectVersion.objects.filter(id=version_id)
        if not version:
            return Response({"message": "Not Found"}, status=status.HTTP_404_NOT_FOUND)
        project_tests = ProjectTest.objects.prefetch_related("steps")
        project_tests = project_tests.annotate(steps_amount=Count("steps"))
        outcome_status = "1"
        project_tests = (
            (
                project_tests.annotate(steps_amount=Count("steps")).annotate(
                    covered_steps_amount=Count(
                        "steps", filter=Q(steps__has_auto_test=True)
                    )
                )
            ).annotate(
                outcome_steps_amount=Count(
                    "steps", filter=Q(steps__keyword=outcome_status)
                )
            )
        ).annotate(
            covered_outcome_steps_amount=Count(
                "steps",
                filter=Q(steps__has_auto_test=True, steps__keyword=outcome_status),
            )
        )

        version = version.prefetch_related(
            Prefetch(
                "test_files",
                queryset=TestFile.objects.prefetch_related(
                    Prefetch("tests", queryset=project_tests)
                ),
            )
        ).first()
        version_data = BigVersionSerializer(instance=version).data
        return Response(version_data)


class GetProjectWithLastVersion(APIView):
    def get(self, request, project_id):
        project = Project.objects.filter(id=project_id).prefetch_related("versions")
        project = project.first()
        if not project:
            return Response({"message": "Not Found"}, status=status.HTTP_404_NOT_FOUND)

        project_data = GetProjectSerializer(instance=project).data
        if not project_data["versions"]:
            return Response(project_data)

        last_version_id = project.versions.last().id
        outcome_status = "1"
        project_tests = ProjectTest.objects.prefetch_related("steps")
        project_tests = (
            project_tests.annotate(steps_amount=Count("steps"))
            .annotate(
                covered_steps_amount=Count("steps", filter=Q(steps__has_auto_test=True))
            )
            .annotate(
                outcome_steps_amount=Count(
                    "steps", filter=Q(steps__keyword=outcome_status)
                )
            )
            .annotate(
                covered_outcome_steps_amount=Count(
                    "steps",
                    filter=Q(steps__has_auto_test=True, steps__keyword=outcome_status),
                )
            )
        )

        version = (
            ProjectVersion.objects.filter(id=last_version_id)
            .prefetch_related(
                Prefetch(
                    "test_files",
                    queryset=TestFile.objects.prefetch_related(
                        Prefetch("tests", queryset=project_tests)
                    ),
                )
            )
            .first()
        )
        version_data = BigVersionSerializer(instance=version).data
        versions = sorted(project_data["versions"], key=lambda v: v["id"])
        versions.pop(-1)
        versions.append(version_data)
        project_data["versions"] = versions
        return Response(project_data)


class UpdateProjectTest(UpdateAPIView):
    queryset = ProjectTest.objects.all()
    serializer_class = ProjectTestSerializer

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.status = request.data.get("status")
        instance.comment = request.data.get("comment")
        instance.save()

        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        return Response(serializer.validated_data)


class UpdateProjectTest(APIView):
    def post(self, request):
        data = request.data

        if not data:
            return Response({"message": "empty data"})

        serializer = ProjectTestStatusSerializer(data=data, many=True)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data
        ids = [test["id"] for test in data]

        tests = sorted(
            list(ProjectTest.objects.filter(id__in=ids)),
            key=lambda test: ids.index(test.id),
        )

        for test, test_data in zip(tests, validated_data):
            test.status = test_data["status"]
            test.comment = test_data["comment"]

        ProjectTest.objects.bulk_update(tests, ["status", "comment"])
        return Response({"message": "ok"})


class DeleteVersion(DestroyAPIView):
    serializer_class = SmallVersionSerializer
    queryset = ProjectVersion.objects.all()
    lookup_field = "id"


class CreateFile(CreateAPIView):
    serializer_class = NewFileSerializer
    queryset = TestFile.objects.all()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        version = data["project_version"]
        project = version.project
        smart_mode = project.smart_mode
        particular_dir = project.files_folder
        common_autotests_folder = project.common_autotests_folder

        file_path = data["file_path"]
        file_text = data["file_text"]
        repo_path = data["repo_path"]
        file_name = data["file_name"]

        if smart_mode and particular_dir and common_autotests_folder:
            common_autotests_folder = get_common_folder_path(
                repo_path, particular_dir, common_autotests_folder
            )

        if os.path.isdir(file_path):
            os.remove(file_path)

        try:
            with open(file_path, "w") as file:
                file.write(file_text)

        except Exception:
            os.remove(file_path)
            return Response(
                {"message": "Unable to create file"}, status=status.HTTP_400_BAD_REQUEST
            )

        try:
            features = get_features_from_file(
                repo_path, file_name, project.smart_mode, common_autotests_folder
            )
        except Exception:
            os.remove(file_path)
            return Response(
                {"file_text": "Invalid file text"}, status=status.HTTP_400_BAD_REQUEST
            )

        if not features:
            os.remove(file_path)
            return Response(
                {"file_text": "Invalid file text"}, status=status.HTTP_400_BAD_REQUEST
            )

        duplicated_test_names = check_for_similar_test_names(features[0])
        if duplicated_test_names:
            exception_text = f"It's can't be identical tests names: {duplicated_test_names[0]}"
            os.remove(file_path)
            return Response(
                {"file_text": exception_text}, status=status.HTTP_400_BAD_REQUEST
            )

        try:
            (
                new_test_files,
                new_project_tests,
                new_test_steps,
            ) = get_new_tests_objects(features, version)
            new_test_file = new_test_files[0]
            new_test_file.manually_created = True
            TestFile.objects.bulk_create(new_test_files)
            ProjectTest.objects.bulk_create(new_project_tests)
            TestStep.objects.bulk_create(new_test_steps)
        except Exception:
            os.remove(file_path)
            return Response(
                {"file_text": "Invalid file text"}, status=status.HTTP_400_BAD_REQUEST
            )

        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data, status=status.HTTP_201_CREATED, headers=headers
        )


class UpdateFile(APIView):
    def put(self, request, file_id, *args, **kwargs):
        data = request.data
        test_file = get_object_or_404(TestFile, id=file_id)
        serializer = FileNameAndTextSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        if not data:
            return Response(serializer.data, status=status.HTTP_200_OK)

        version_id = test_file.project_version.id
        version = (
            ProjectVersion.objects.filter(id=version_id)
            .prefetch_related(
                Prefetch(
                    "test_files",
                    queryset=TestFile.objects.prefetch_related(
                        Prefetch(
                            "tests",
                            queryset=ProjectTest.objects.prefetch_related("steps"),
                        )
                    ),
                )
            )
            .first()
        )

        project = version.project
        smart_mode = project.smart_mode
        particular_dir = project.files_folder
        common_autotests_folder = project.common_autotests_folder

        repo_path = get_repo_path(project.id, version.id)
        files_folder = os.path.join(repo_path, project.files_folder)
        old_path = None

        if "file_name" in data:
            new_file_path = os.path.join(files_folder, data["file_name"])
            if version.test_files.filter(file_path=new_file_path).exists():
                return Response(
                    {"file_name": "File with such name already exists in this version"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            old_path = test_file.file_path
            rename_file_hard(test_file.file_path, new_file_path)
            test_file.file_path = new_file_path
            test_file.save()

        if "file_text" in data:
            file_path = test_file.file_path
            if smart_mode and particular_dir and common_autotests_folder:
                common_autotests_folder = get_common_folder_path(
                    repo_path, particular_dir, common_autotests_folder
                )
            with open(file_path, "r") as f:
                old_text = f.read()

            with open(file_path, "w") as f:
                f.write(data["file_text"])

            exception_text = '"file_text": "Invalid file text"'
            try:
                file_name = test_file.file_name + ".feature"
                features = get_features_from_file(
                    repo_path, file_name, project.smart_mode, common_autotests_folder
                )
                duplicated_test_names = check_for_similar_test_names(features[0])
                if duplicated_test_names:
                    exception_text = f"It's can't be identical tests names: {duplicated_test_names[0]}"
                    raise Exception()
                (
                    updated_test_files,
                    new_project_tests,
                    updated_project_tests,
                    updated_test_steps,
                ) = get_updated_tests_objcts(features, version)

                (
                    deleted_project_tests,
                    deleted_test_steps,
                ) = get_deleted_tests_objects_from_file(features, test_file)

            except Exception as e:
                    with open(file_path, "w") as f:
                        f.write(old_text)
                    if old_path:
                        rename_file_hard(new_file_path, old_path)

                    return Response(
                        {"file_text": exception_text},
                        status=status.HTTP_400_BAD_REQUEST,
                   )

            if not features:
                with open(file_path, "w") as f:
                    f.write(old_text)
                if old_path:
                    rename_file_hard(new_file_path, old_path)
                return Response(
                    {"file_text": "Invalid file text"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            ProjectTest.objects.bulk_create(new_project_tests)
            ProjectTest.objects.bulk_update(updated_project_tests, ["last_line", "start_line"])
            TestStep.objects.bulk_create(updated_test_steps)
            if deleted_test_steps:
                bulk_delete(TestStep, deleted_test_steps)
            if deleted_project_tests:
                bulk_delete(ProjectTest, deleted_project_tests)

        test_file.save()
        return Response(serializer.data, status=status.HTTP_200_OK)


class GetTestText(APIView):
    def get(self, request, test_id):
        test = get_object_or_404(ProjectTest, id=test_id)
        file_path = test.file.file_path
        start_line, last_line = test.start_line, test.last_line
        test_text = ""
        with open(file_path, "r") as f:
            file_text = f.readlines()
            for line_number in range(start_line - 1, last_line + 1):
                test_text += file_text[line_number]

        data = {"text": test_text, "name": test.test_name}
        return Response(data, status=status.HTTP_200_OK)