from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework import generics
from rest_framework.permissions import AllowAny
from .serializer import SingUpSerializer, CodeVerifySerializer, EditUserSerializer
from rest_framework.response import Response
from .models import User, AuthStatus, AuthType
from .permissions import (
    IsRegistrationPermissions,
    IsVerifyCodePermission,
    IsEditUserPermissions,
)
from .authentication import RegistrationTokenAuthentication
from .tokens import RegistrationToken
from rest_framework.exceptions import ValidationError
from django.utils import timezone
from rest_framework import status
from shared.utils import send_email


class SingUpView(generics.CreateAPIView):
    permission_classes = [AllowAny]
    queryset = User.objects.all()
    serializer_class = SingUpSerializer


class CodeVerifyView(APIView):
    permission_classes = [IsRegistrationPermissions, IsVerifyCodePermission]
    authentication_classes = [RegistrationTokenAuthentication]

    def post(self, request, *args, **kwargs):
        user = self.request.user
        serializer = CodeVerifySerializer(
            data=request.data, context={"user": self.request.user}
        )
        if serializer.is_valid(raise_exception=True):
            user.auth_status = AuthStatus.DONE
            user.save()
            return Response(
                {
                    "success": True,
                    "message": "Muvaffaqiyatli verifikatsiyadan o'tingiz",
                    "registration_token": str(RegistrationToken.for_user(user)),
                    "auth_status": user.auth_status,
                }
            )
        else:
            raise ValidationError({"success": False, "message": str(serializer.errors)})


class CodeVerifyRestView(APIView):
    permission_classes = [IsRegistrationPermissions, IsVerifyCodePermission]
    authentication_classes = [RegistrationTokenAuthentication]

    def get(self, request, *args, **kwargs):
        user = self.request.user

        if user is None:
            return Response(
                {"success": False, "message": "Siz ro'yhatdan o'tmagansiz"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        self.check_code(user)

        if user.auth_type == AuthType.VIA_EMAIL:
            user_code = user.code_verify(AuthType.VIA_EMAIL)
            send_email(user.email, user_code)
        elif user.auth_type == AuthType.VIA_PHONE:
            user_code = user.code_verify(AuthType.VIA_PHONE)
            send_email(to_email="suvonovjavohir625@gmail.com", code=user_code)

        return Response(
            {
                "success": True,
                "message": "Code yuborildi",
                "registration_token": str(RegistrationToken.for_user(user)),
            },
            status=status.HTTP_200_OK,
        )

    @staticmethod
    def check_code(user):
        verify = user.verify_codes.filter(
            expiration_time__gte=timezone.now(), is_confirmed=False
        )
        if verify.exists():
            raise ValidationError(
                {
                    "success": False,
                    "message": "siz hozirda yaroqli kod bor biroz kuting",
                }
            )


class EditUserView(APIView):

    permission_classes = [IsRegistrationPermissions, IsEditUserPermissions]
    authentication_classes = [RegistrationTokenAuthentication]

    def put(self, request, *args, **kwargs):
        serializer = EditUserSerializer(instance=self.request.user, data=request.data)

        if serializer.is_valid(raise_exception=True):
            serializer.save()

            token = self.request.user.token()

            return Response(
                {
                    "success": True,
                    "message": "Muvafiqiyatli o'zgartrildi",
                    "access_token": token.get("access_token"),
                    "refresh": token.get("refresh"),
                }
            )


# Create your views here.
