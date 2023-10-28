from django.contrib import admin
from .models import *


class StepsInline(admin.TabularInline):
    model = TestStep


class TestsInline(admin.TabularInline):
    model = ProjectTest


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
