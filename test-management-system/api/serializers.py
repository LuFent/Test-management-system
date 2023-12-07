from rest_framework.serializers import (
    ModelSerializer,
    ValidationError,
    IntegerField,
    CharField,
    Serializer,
)
from .models import *
from django.core.validators import URLValidator
from pathvalidate import sanitize_filename
import os
from .tools import get_repo_path, get_features_from_file

url_validator = URLValidator()


class TestStepSerializer(ModelSerializer):
    class Meta:
        model = TestStep
        fields = "__all__"


class ProjectTestSerializer(ModelSerializer):
    steps = TestStepSerializer(many=True, read_only=True)

    steps_amount = IntegerField()
    covered_steps_amount = IntegerField()
    outcome_steps_amount = IntegerField()
    covered_outcome_steps_amount = IntegerField()

    class Meta:
        model = ProjectTest
        fields = [
            "id",
            "steps",
            "status",
            "comment",
            "test_name",
            "steps_amount",
            "covered_steps_amount",
            "outcome_steps_amount",
            "covered_outcome_steps_amount",
            "start_line",
            "last_line",
            "needs_expanded_view",
        ]


class TestFileSerializer(ModelSerializer):
    tests = ProjectTestSerializer(many=True, read_only=True)

    class Meta:
        model = TestFile
        fields = ["file_name", "tests", "manually_created", "id"]


class BigVersionSerializer(ModelSerializer):
    test_files = TestFileSerializer(many=True, read_only=True)

    class Meta:
        model = ProjectVersion
        fields = [
            "id",
            "version_label",
            "commit_hash",
            "branch",
            "test_files",
            "error_message",
            "is_valid",
        ]


class SmallVersionSerializer(ModelSerializer):
    class Meta:
        model = ProjectVersion
        fields = ["id", "version_label"]


class GetProjectSerializer(ModelSerializer):
    versions = SmallVersionSerializer(many=True, read_only=True)

    class Meta:
        model = Project
        fields = ["id", "name", "versions"]

    def validate_repo_url(self, value):
        url_validator(value)
        return value


class CreateProjectSerializer(ModelSerializer):
    class Meta:
        model = Project
        fields = "__all__"

    def validate_repo_url(self, value):
        url_validator(value)
        return value

    def validate(self, attrs):
        if attrs["smart_mode"] and not attrs["files_folder"]:
            raise ValidationError(
                {"files_folder": "Cant be smart mode without files folder"}
            )

        if not attrs["smart_mode"] and attrs["common_autotests_folder"]:
            raise ValidationError(
                {
                    "common_autotests_folder": "Common auto tests folder is intended for smart mode"
                }
            )

        if not attrs.get("git_username", None):
            attrs["git_username"] = attrs["git_access_key"]

        return attrs


class VersionSerializer(ModelSerializer):
    class Meta:
        model = ProjectVersion
        fields = ["project", "version_label", "branch", "commit_hash"]


class ProjectTestStatusSerializer(ModelSerializer):
    class Meta:
        model = ProjectTest
        fields = ["id", "comment", "status"]


class NewFileSerializer(ModelSerializer):
    file_name = CharField()
    file_text = CharField(style={"base_template": "textarea.html"})
    extension_delimiter = "."
    features_extension = extension_delimiter + "feature"

    def validate_file_name(self, value):
        if (
            value != sanitize_filename(value)
            or value.count(self.extension_delimiter) > 1
        ):
            raise ValidationError("Invalid file name")
        return value

    def validate(self, data):
        filename = data["file_name"]
        _, file_extension = os.path.splitext(data["file_name"])

        if not file_extension:
            filename += self.features_extension
            data["file_name"] = filename
        elif file_extension != self.features_extension:
            raise ValidationError({"file_name": "Invalid file extension"})

        version = data["project_version"]
        project = version.project

        repo_path = get_repo_path(project.id, version.id)
        file_path = os.path.join(repo_path, project.files_folder, filename)

        if version.test_files.filter(file_path=file_path).exists():
            raise ValidationError(
                {"file_name": "File with such name already exists in this version"}
            )

        data["file_path"] = file_path
        data["repo_path"] = repo_path

        return data

    class Meta:
        model = TestFile
        fields = ["project_version", "file_text", "file_name"]


class FileNameAndTextSerializer(Serializer):
    file_name = CharField(required=False)
    file_text = CharField(required=False, style={"base_template": "textarea.html"})
    extension_delimiter = "."
    features_extension = extension_delimiter + "feature"

    def validate_file_name(self, value):
        if (
            value != sanitize_filename(value)
            or value.count(self.extension_delimiter) > 1
        ):
            raise ValidationError("Invalid file name")

        _, file_extension = os.path.splitext(value)
        if not file_extension:
            value += self.features_extension
        elif file_extension != self.features_extension:
            raise ValidationError("Invalid file extension")

        return value


class AutoTestStepSerializer(ModelSerializer):
    class Meta:
        model = AutoTestStep
        fields = ["keyword_label", "text"]


class FileNameSerializer(ModelSerializer):
    class Meta:
        model = TestFile
        fields = ["file_name_with_ext"]