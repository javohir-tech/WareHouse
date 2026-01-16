import datetime
import random
import uuid
from django.db import models
from shared.models import BaseModel
from django.utils import timezone
from django.contrib.auth.hashers import identify_hasher
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.models import AbstractUser


class UserRole(models.TextChoices):
    ORDINARY_USER = "ordinary_user", "Ordinary User"
    ADMIN = "admin", "Admin"
    MANAGER = "manager", "Manager"


class AuthType(models.TextChoices):
    VIA_EMAIL = "via_email", "Via Email"
    VIA_PHONE = "via_phone", "Via Phone"


class AuthStatus(models.TextChoices):
    NEW = "new", "New"
    CODE_VERIFY = "code_verify", "Code Verify"
    DONE = "done", "Done"
    PHOTO_DONE = "photo_done", "Photo done"


class User(BaseModel, AbstractUser):

    user_role = models.CharField(
        max_length=31, choices=UserRole.choices, default=UserRole.ORDINARY_USER
    )
    auth_type = models.CharField(max_length=31, choices=AuthType.choices)
    auth_status = models.CharField(
        max_length=31, choices=AuthStatus.choices, default=AuthStatus.NEW
    )
    email = models.EmailField(max_length=254, unique=True, blank=True, null=True)
    phone_number = models.CharField(max_length=16, unique=True, blank=True, null=True)

    def code_verify(self, auth_type):
        code = "".join([str(random.randint(1, 10000) % 10) for _ in range(4)])
        UserConfirmation.objects.create(code=code, auth_type=auth_type, user=self)
        return code

    def check_username(self):
        temp_username = f"warehouse-{uuid.uuid4().__str__().split("-")[-1]}"

        while User.objects.filter(username=temp_username).exists():
            temp_username = f"{temp_username}{random.randint(1, 9)}"

        self.username = temp_username

    @staticmethod
    def is_hashing(password):
        try:
            identify_hasher(password)
            return True
        except ValueError:
            return False

    def check_user_password(self):
        temp_password = f"password-{uuid.uuid4().__str__().split("-")[-1]}"

        if not self.password:
            self.password = temp_password

    def hashing_password(self):
        if self.password:
            if not self.is_hashing(self.password):
                self.set_password(self.password)

    def check_email(self):
        if self.email:
            normalize = self.email.lower().strip()
            self.email = normalize

    def token(self):
        refresh = RefreshToken.for_user(self)

        return {"access_token": str(refresh.access_token), "refresh": str(refresh)}

    def clean(self):
        self.check_email()
        self.check_username()
        self.check_user_password()
        self.hashing_password()

    def save(self, *args, **kwargs):
        if self._state.adding:
            self.clean()

        super().save(*args, **kwargs)


EXPIRE_EMAIL = 5
EXPIRE_PHONE = 2


class UserConfirmation(BaseModel):
    code = models.CharField(max_length=4)
    auth_type = models.CharField(max_length=31, choices=AuthType.choices)
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="verify_codes"
    )
    expiration_time = models.DateTimeField(null=True, blank=True)
    is_confirmed = models.BooleanField(default=False)

    def is_expired(self):
        if self.expiretion_time is None:
            return False
        return self.expiretion_time < timezone.now()

    def can_verify(self):
        if self.is_expire():
            return False
        if self.is_confirmed:
            return False
        return True

    def save(self, *args, **kwargs):
        if self._state.adding:
            if self.auth_type == AuthType.VIA_EMAIL:
                self.expiretion_time = (
                    datetime.timedelta(minutes=EXPIRE_EMAIL) + timezone.now()
                )
            if self.auth_type == AuthType.VIA_PHONE:
                self.expiretion_time = (
                    datetime.timedelta(minutes=EXPIRE_PHONE) + timezone.now()
                )

        super().save(*args, **kwargs)
