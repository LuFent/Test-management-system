from django.contrib import admin
from .models import AppUser, RegistrationToken

# Register your models here.


@admin.register(AppUser)
class AdminAppUser(admin.ModelAdmin):
    pass


@admin.register(RegistrationToken)
class AdminRegistrationToken(admin.ModelAdmin):
    pass
