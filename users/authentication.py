from rest_framework_simplejwt.authentication import JWTAuthentication
from .tokens import RegistrationToken
from rest_framework.exceptions import AuthenticationFailed
from users.models import User


class RegistrationTokenAuthentication(JWTAuthentication):

    def get_validated_token(self, raw_token):
        try:
            return RegistrationToken(raw_token)
        except Exception as e:
            raise AuthenticationFailed(f"token yaroqsiz {e}")

    def get_user(self, validated_token):

        try:
            user_id = validated_token.get("user_id")

            if user_id is None:
                raise AuthenticationFailed(f"token ichida user_id yo'q")

            user = User.objects.get(id=user_id)

            if user.auth_status != validated_token.get("auth_status"):
                raise AuthenticationFailed("token yaroqsiz yoki eskirgan")

            return user
        except User.DoesNotExist:
            raise AuthenticationFailed("user topilmadi")
        except Exception as e:
            raise AuthenticationFailed(f"authenticated xatosi {e}")
