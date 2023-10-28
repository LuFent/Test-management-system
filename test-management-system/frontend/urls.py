from django.contrib import admin
from django.urls import path
from django.views.generic.base import RedirectView
from .views import *
from django.templatetags.static import static


urlpatterns = [
    path("", IndexView.as_view(), name="index"),
    path("login/", LoginForm.as_view(), name="login"),
    path("register/", RegisterForm.as_view(), name="register"),
    path("projects/<int:project_id>/", ProjectReactBase.as_view(), name="project_page"),
]

urlpatterns += [
    path("favicon.ico", RedirectView.as_view(url=static("favicon.ico"), permanent=True))
]