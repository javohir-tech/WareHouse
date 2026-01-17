from rest_framework_simplejwt.tokens import Token
from datetime import timedelta
from .models import User , AuthType , AuthStatus

class RegistrationToken(Token):
    
    token_type = 'registration'
    lifetime = timedelta(minutes=15)
    
    @classmethod
    def for_user(cls , user):
        
        token = cls()
        
        token['user_id'] = str(user.id)
        token['token_type'] = "registration"
        token['auth_status'] = user.auth_status
        token['auth_type'] = user.auth_type
        
        if user.auth_type == AuthType.VIA_EMAIL:
            token['email'] = user.email
        elif user.auth_tyep == AuthType.VIA_PHONE:
            token["phone_number"] = user.phone_number
            
        return token
    
    @classmethod
    def get_user_from_token(cls , token_str):
        token = cls(token_str)
        
        user_id = token.get('user_id')
        
        user = User.objects.get(id=user_id)
        
        return user