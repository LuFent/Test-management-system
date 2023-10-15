from django.urls import path
from . import views


urlpatterns = [
    path(
        "generate_register_token/",
        views.RegisterTokenGenerator.as_view(),
        name="generate_register_token",
    ),
    path("register/", views.UserRegister.as_view(), name="register"),
    path("login/", views.UserLogin.as_view(), name="login"),
    path("logout/", views.UserLogout.as_view(), name="logout"),
    path("me/", views.UserView.as_view(), name="user"),
]
