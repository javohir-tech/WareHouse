from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework import generics
from rest_framework.permissions import AllowAny
from .serializer import SingUpSerializer, CodeVerifySerializer
from rest_framework.response import Response
from .models import User, AuthStatus
from .permissions import IsRegistrationPermissions, IsVerifyCodePermission
from .authentication import RegistrationTokenAuthentication
from .tokens import RegistrationToken
from rest_framework.exceptions import ValidationError


class SingUpView(generics.CreateAPIView):
    permission_classes = [AllowAny]
    queryset = User.objects.all()
    serializer_class = SingUpSerializer


class CodeVerifyView(APIView):
    permission_classes = [IsRegistrationPermissions, IsVerifyCodePermission]
    authentication_classes = [RegistrationTokenAuthentication]

    def post(self, request, *args, **kwargs):
        user = self.request.user
        serializer = CodeVerifySerializer(data=request.data, context={"user": self.request.user})
        if serializer.is_valid(raise_exception=True):
            user.auth_status = AuthStatus.DONE
            return Response(
                {
                    "success": True,
                    "message": "Muvaffaqiyatli verifikatsiyadan o'tingiz",
                    "registration_token": str(RegistrationToken.for_user(user)),
                    "auth_status": user.auth_status,
                }
            )
        else:
            raise ValidationError(
                {
                    "success" : False,  
                    "message" : str(serializer.errors)
                }
            )


# Create your views here.
