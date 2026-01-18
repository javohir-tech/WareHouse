from django.urls import path
from .views import SingUpView, CodeVerifyView, CodeVerifyRestView, EditUserView

urlpatterns = [
    path("singup/", SingUpView.as_view()),
    path("code_verify/", CodeVerifyView.as_view()),
    path("code_rest/", CodeVerifyRestView.as_view()),
    path("edit_user/", EditUserView.as_view()),
]
