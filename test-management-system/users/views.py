from django.contrib.auth import get_user_model, login, logout
from rest_framework.authentication import SessionAuthentication
from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import UserRegisterSerializer, UserLoginSerializer, UserSerializer
from rest_framework import permissions, status
from django.core.signing import Signer
import datetime
from .models import RegistrationToken
from .permissions import RegistrationTokenPermission
from django.urls import reverse


signer = Signer()


class RegisterTokenGenerator(APIView):
    permission_classes = (permissions.IsAdminUser,)
    expire_time = datetime.timedelta(days=1)
    # expire_time = datetime.timedelta(seconds=5)
    datetime_format = "%m/%d/%Y, %H:%M:%S"

    def get(self, request):
        created_at = datetime.datetime.now()
        expired_at = created_at + self.expire_time
        user = request.user
        user.tokens_created += 1
        user.save()
        token_data = {
            "created_at": created_at.strftime(self.datetime_format),
            "expire_at": expired_at.strftime(self.datetime_format),
            "created_by": user.email,
            "number": user.tokens_created,
        }
        token = signer.sign_object(token_data)
        RegistrationToken.objects.create(token=token, expired_at=expired_at)
        url = (
            f"{request.build_absolute_uri(reverse('frontend:register'))}?token={token}"
        )

        return Response({"token": token, "url": url})


class UserRegister(APIView):
    permission_classes = (RegistrationTokenPermission,)

    def post(self, request):
        data = request.data
        serializer = UserRegisterSerializer(data=data)
        if serializer.is_valid(raise_exception=True):
            user = serializer.create(request.data)
            if user:
                token = request.query_params.get("token")
                token = RegistrationToken.objects.get(token=token)
                token.delete()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(status=status.HTTP_400_BAD_REQUEST)


class UserLogin(APIView):
    permission_classes = (permissions.AllowAny,)
    authentication_classes = (SessionAuthentication,)

    def post(self, request):
        data = request.data
        serializer = UserLoginSerializer(data=data)
        if serializer.is_valid(raise_exception=True):
            user = serializer.check_user(data)
            login(request, user)
            return Response(serializer.data, status=status.HTTP_200_OK)


class UserLogout(APIView):
    permission_classes = (permissions.AllowAny,)
    authentication_classes = ()

    def post(self, request):
        logout(request)
        return Response(status=status.HTTP_200_OK)


class UserView(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    authentication_classes = (SessionAuthentication,)

    ##
    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response({"user": serializer.data}, status=status.HTTP_200_OK)
