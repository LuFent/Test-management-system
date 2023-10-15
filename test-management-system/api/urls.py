from django.contrib import admin
from django.urls import path
from .views import *

urlpatterns = [
    path("create_project/", CreateProject.as_view(), name="create_project"),
    path("create_version/", CreateVersion.as_view(), name="create_version"),
    path("pull_version/", UpdateVersion.as_view(), name="pull_version"),
    path("projects/<id>/", GetProject.as_view(), name="get_project"),
    path("project_versions/<id>/", GetVersion.as_view(), name="get_version"),
    path(
        "project_versions_with_coverage/<version_id>/",
        GetVersionWithCoverage.as_view(),
        name="get_version_with_coverage",
    ),
    path(
        "projects_with_last_version/<project_id>/",
        GetProjectWithLastVersion.as_view(),
        name="projects_with_last_version",
    ),
    path("update_test/", UpdateProjectTest.as_view(), name="update_test"),
    path("delete_version/<id>/", DeleteVersion.as_view(), name="delete_version"),
    path("create_file/", CreateFile.as_view(), name="create_file"),
    path("push_files/", PushFiles.as_view(), name="push_files")
]
