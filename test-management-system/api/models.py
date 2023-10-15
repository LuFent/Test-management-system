from django.db import models
from django.db.models import Count
from django.contrib.auth import get_user_model
from django.conf import settings
import ntpath
import os
from django.db.models import Q


UserModel = get_user_model()


class Project(models.Model):
    name = models.CharField(
        max_length=100, verbose_name="Project name", unique=True
    )

    creation_date = models.DateField("Creation date")

    creator = models.ForeignKey(
        UserModel, on_delete=models.SET_NULL, related_name="created_projects", null=True
    )

    repo_url = models.CharField(max_length=150, verbose_name="Repository link")

    files_folder = models.CharField(
        max_length=150, blank=True, null=True, verbose_name="Folder with .feature files"
    )

    smart_mode = models.BooleanField(default=False)

    common_autotests_folder = models.CharField(
        max_length=150, blank=True, null=True, verbose_name="Common autotests folder"
    )

    git_access_key = models.CharField(
        max_length=100, null=True, blank=True, verbose_name="Git access token"
    )

    git_username = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        verbose_name="Git username",
        default="user",
    )

    def __str__(self):
        return f"{self.name}"


class ProjectVersion(models.Model):
    version_label = models.CharField(max_length=100, verbose_name="Version label")

    branch = models.CharField(
        max_length=100, verbose_name="Repoository branch", default="main"
    )

    commit_hash = models.CharField(
        max_length=100, verbose_name="Commit hash", blank=True, null=True
    )

    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name="versions",
        verbose_name="Project",
    )

    error_message = models.TextField(
        verbose_name="Error message",
        blank=True,
        null=True,
    )

    is_valid = models.BooleanField(
        default=True,
        verbose_name="Is version valid",
    )

    class Meta:
        unique_together = (
            "project",
            "version_label",
        )

    def __str__(self):
        return f"{self.project.name} -- {self.version_label}"


class TestFile(models.Model):
    class Meta:
        unique_together = (
            "file_path",
            "project_version",
        )

    file_path = models.FilePathField(
        path=settings.DOT_FEATURE_FILES_DIR,
        match=".*?.feature",
        recursive=True,
        allow_folders=False,
        max_length=512,
    )

    project_version = models.ForeignKey(
        ProjectVersion,
        on_delete=models.CASCADE,
        related_name="test_files",
        verbose_name="Project Version",
    )

    manually_created = models.BooleanField(
        default=False
    )
    @property
    def file_name(self):
        return os.path.splitext(ntpath.basename(self.file_path))[0]


    class Meta:
        unique_together = (
            "project_version",
            "file_path",
        )

    def __str__(self):
        return f"{self.project_version} | {self.file_name}"


class ProjectTest(models.Model):
    class Status(models.TextChoices):
        PASS = "1", "PASSED"
        FAIL = "2", "FAILED"
        UNDEFINED = "3", "UNDEFINED"

    status = models.CharField(
        max_length=20,
        verbose_name="Test status",
        choices=Status.choices,
        default=Status.UNDEFINED,
    )

    text = models.TextField(
        max_length=20000, verbose_name="Test comment", blank=True, null=True
    )

    test_name = models.CharField(max_length=200, verbose_name="Test name")

    file = models.ForeignKey(
        TestFile, on_delete=models.CASCADE, related_name="tests", verbose_name="File"
    )

    def __str__(self):
        return f"Test {self.test_name}"


class TestStep(models.Model):
    class Keyword(models.TextChoices):
        OUTCOME = "1", "Outcome"
        CONJUNCTION = "2", "Conjunction"
        UNKNOWN = "3", "Unknown"
        ACTION = "4", "Action"
        CONTEXT = "5", "Context"

    keyword = models.CharField(
        max_length=20,
        verbose_name="Step type",
        choices=Keyword.choices,
        default=Keyword.UNKNOWN,
    )

    project_test = models.ForeignKey(
        ProjectTest,
        on_delete=models.CASCADE,
        related_name="steps",
        verbose_name="Feature step",
    )

    text = models.TextField(
        max_length=300, verbose_name="Test text", blank=True, null=True
    )

    has_auto_test = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.project_test} -- {self.text}"
