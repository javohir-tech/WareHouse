from rest_framework.permissions import BasePermission
from .models import AuthStatus

class IsRegistrationPermissions(BasePermission):
    
    def has_permission(self, request, view):
        
        if not hasattr(request , "auth") or request.auth is None :
            return False
        
        token_type = request.auth.get("token_type")
        
        return token_type == "registration"
    
class IsVerifyCodePermission(BasePermission):
    
    def has_permission(self, request, view):
        
        if not hasattr(request , 'auth') or request.auth  is None:
            return False
        
        current_step = request.auth.get("auth_status")
        
        return current_step == AuthStatus.CODE_VERIFY