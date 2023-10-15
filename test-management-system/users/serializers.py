from rest_framework import serializers
from django.contrib.auth import get_user_model, authenticate
from django.contrib.auth.password_validation import (
    validate_password,
    NumericPasswordValidator,
    CommonPasswordValidator,
    MinimumLengthValidator,
)
from django.core.exceptions import ValidationError

UserModel = get_user_model()


class UserRegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserModel
        fields = "__all__"
        extra_kwargs = {
            "email": {
                "error_messages": {
                    "invalid": "Некорректный адрес",
                }
            },
            "full_name": {
                "error_messages": {
                    "blank": "Не может быть пустым",
                }
            },
        }

    def validate_password(self, password):
        errors = []
        min_len = 8
        if len(password) < min_len:
            errors.append(f"Пароль не может быть короче {min_len} символов")
        if password.isdigit():
            errors.append("Пароль не может состоять только из цифр")

        if errors:
            raise ValidationError(errors)

    def create(self, clean_data):
        user = UserModel.objects.create_user(
            email=clean_data["email"],
            password=clean_data["password"],
            full_name=clean_data["full_name"],
        )

        return user


class UserLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()

    def check_user(self, clean_data):
        email = clean_data["email"]
        password = clean_data["password"]

        if not UserModel.objects.filter(email=email):
            raise serializers.ValidationError({"email": "No such user"})

        user = authenticate(username=email, password=password)

        if not user:
            raise serializers.ValidationError({"password": "Wrong password"})

        return user


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserModel
        fields = ("email", "full_name")
