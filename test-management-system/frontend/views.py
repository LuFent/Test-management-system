from django.shortcuts import render, get_object_or_404
from rest_framework.permissions import IsAuthenticated, AllowAny
from users.permissions import RegistrationTokenPermission
from rest_framework.views import APIView
from api import models
from rest_framework.exceptions import NotAuthenticated
from django.shortcuts import redirect
from django.urls import reverse


class IndexView(APIView):
    def get(self, request, format=None):
        projects = models.Project.objects.all()
        contex = {"projects": projects}
        return render(request, "index.html", contex)


class LoginForm(APIView):
    permission_classes = [
        AllowAny,
    ]

    def get(self, request, format=None):
        return render(request, "login_form.html")


class RegisterForm(APIView):
    permission_classes = [
        RegistrationTokenPermission,
    ]

    def get(self, request, format=None):
        return render(request, "register_form.html")


class ProjectReactBase(APIView):
    def get(self, request, project_id):
        project = get_object_or_404(models.Project, id=project_id)
        return render(request, "react/project_page.html")


class AccessTokens(APIView):
    def get(self, request):
        tokens = models.GitAccessToken.objects.all()
