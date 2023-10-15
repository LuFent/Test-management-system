from rest_framework.exceptions import NotAuthenticated
from rest_framework.views import exception_handler
from django.shortcuts import redirect


def redirect_to_log(exec, data):
    if isinstance(exec, NotAuthenticated):
        return redirect("frontend:login")
    return exception_handler(exec, data)
