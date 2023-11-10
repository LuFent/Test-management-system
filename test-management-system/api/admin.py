from django.contrib import admin
from .models import *
from frontend.widgets import TextInput

class StepsInline(admin.TabularInline):
    model = TestStep


class TestsInline(admin.TabularInline):
    model = ProjectTest


class TestFilesInline(admin.TabularInline):
    model = TestFile


@admin.register(Project)
class AdminProject(admin.ModelAdmin):
    pass


@admin.register(ProjectVersion)
class AdminProjectVersion(admin.ModelAdmin):
    pass


@admin.register(TestFile)
class AdminTestFile(admin.ModelAdmin):
    inlines = [TestsInline]


@admin.register(ProjectTest)
class AdminProjectTest(admin.ModelAdmin):
    inlines = [StepsInline]


@admin.register(TestStep)
class AdminTestStep(admin.ModelAdmin):
    list_filter = ["has_auto_test", "keyword"]


@admin.register(AutoTestStep)
class AdminAutoTestStep(admin.ModelAdmin):
    formfield_overrides = {
        models.CharField: {"widget": TextInput},
    }

    pass