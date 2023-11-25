from rest_framework import serializers
from django.contrib.auth import get_user_model, authenticate
import django.contrib.auth.password_validation as validators
from django.core.exceptions import ValidationError

UserModel = get_user_model()


class UserRegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserModel
        fields = "__all__"

    def validate(self, data):

        password = data.get('password')

        errors = dict()
        try:
            validators.validate_password(password=password)

        except ValidationError as e:
            errors['password'] = list(e.messages)[0]

        if errors:
            raise serializers.ValidationError(errors)

        return super(UserRegisterSerializer, self).validate(data)

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
