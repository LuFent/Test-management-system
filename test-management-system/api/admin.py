from django.contrib import admin
from .models import *


@admin.register(Project)
class AdminProject(admin.ModelAdmin):
    pass


@admin.register(ProjectVersion)
class AdminProjectVersion(admin.ModelAdmin):
    pass


@admin.register(ProjectTest)
class AdminProjectTest(admin.ModelAdmin):
    pass


@admin.register(TestFile)
class AdminTestFile(admin.ModelAdmin):
    pass


@admin.register(TestStep)
class AdminTestStep(admin.ModelAdmin):
    list_filter = ["has_auto_test", "keyword"]
