import re
from rest_framework import serializers
from .models import User
from shared.utils import check_auth_type, send_email
from .models import User, AuthType, AuthStatus, UserConfirmation
from rest_framework.validators import ValidationError
from .tokens import RegistrationToken
from django.utils import timezone
from django.contrib.auth.password_validation import validate_password


class SingUpSerializer(serializers.ModelSerializer):
    user_input = serializers.CharField(max_length=31, write_only=True)

    class Meta:
        model = User
        fields = ["id", "auth_type", "auth_status", "user_input"]
        extra_kwargs = {
            "auth_type": {"write_only": True, "required": False},
            "auth_status": {"write_only": True, "required": False},
        }
        read_only_fields = ["id"]

    def create(self, validated_data):
        user = User(**validated_data)
        user.auth_status = AuthStatus.CODE_VERIFY
        user.save()
        auth_type = validated_data.get("auth_type")

        code = user.code_verify(auth_type)
        if auth_type == AuthType.VIA_EMAIL:
            email = validated_data.get("email")
            send_email(email, code)
        elif auth_type == AuthType.VIA_PHONE:
            phone = validated_data.get("phone")
            send_email(to_email="suvonovjavohir625@gmail.com", code=code)
        return user

    def validate(self, data):
        data = self.auth_validate(data)
        data = self.check_user_exists(data)
        data.pop("user_input", None)
        return data

    @staticmethod
    def auth_validate(data):
        user_input = data.get("user_input")
        auth_type = check_auth_type(user_input)
        if auth_type == AuthType.VIA_EMAIL:
            data = {"email": user_input, "auth_type": AuthType.VIA_EMAIL}
        elif auth_type == AuthType.VIA_PHONE:
            data = {"phone_number": user_input, "auth_type": AuthType.VIA_PHONE}
        else:
            raise ValidationError("Siz kiritgan email yoki telefon raqam hato")

        return data

    @staticmethod
    def check_user_exists(data):
        auth_type = data.get("auth_type")

        if auth_type == AuthType.VIA_EMAIL:
            user_email = data["email"]
            user = User.objects.filter(email=user_email)
            if user.exists():
                raise ValidationError("Bu emmaildan oldin ro'yhatdan o'tilgan")
        if auth_type == AuthType.VIA_PHONE:
            user_phone = data["phone_number"]
            user = User.objects.filter(phone_number=user_phone)
            if user.exists():
                raise ValidationError("BU telefon raqamdan oldin ro'yhatdan o'tilgan")

        return data

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data["auth_status"] = AuthStatus.CODE_VERIFY
        data["registration_token"] = str(RegistrationToken.for_user(instance))

        return data


class CodeVerifySerializer(serializers.Serializer):
    code = serializers.CharField(max_length=4, write_only=True)

    def validate(self, data):

        user = self.context.get("user")
        code = data.get("code")
        if user is None:
            raise ValidationError("user topilmadi")

        user_confirmation_code = user.verify_codes.filter(
            expiration_time__gte=timezone.now(), code=code, is_confirmed=False
        ).first()

        if user_confirmation_code is None:
            raise ValidationError("Kod yaroqsiz")

        user_confirmation_code.is_confirmed = True
        user_confirmation_code.save()

        return data


class EditUserSerializer(serializers.Serializer):
    first_name = serializers.CharField(write_only=True)
    last_name = serializers.CharField(write_only=True)
    username = serializers.CharField(write_only=True)
    password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)

    def validate(self, data):
        username = data.get("username")
        password = data.get("password")
        confirm_password = data.get("confirm_password")
        username_regex = r"^[a-z0-9_-]{3,15}$"

        if not re.fullmatch(username_regex, username):
            raise ValidationError(
                {
                    "succeess": False,
                    "message": "Username belgilar va raqamlardan iborat bo;lishi kerak .Uzunligi 3 va 15 orasida bo'lishi kerak ",
                }
            )

        self.check_password(password)

        if password != confirm_password:
            raise ValidationError(
                {"success": False, "message": "Tastiqlash paroli parololga teng emas"}
            )

        return data

    @staticmethod
    def check_password(password):
        try:
            validate_password(password)
        except Exception as e:
            raise ValidationError({"success": False, "message": f"Parol mos emas {e}"})

    def update(self, instance, validated_data):
        instance.username= validated_data.get("username")
        instance.first_name = validated_data.get("first_name")
        instance.last_name = validated_data.get("last_name")

        if validated_data.get("password"):
            instance.set_password(validated_data.get("password"))
        if instance.auth_status == AuthStatus.DONE:
            instance.auth_status = AuthStatus.PHOTO_DONE

        instance.save()

        return instance
