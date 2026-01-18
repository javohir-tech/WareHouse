from django.urls import path
from .views import SingUpView, CodeVerifyView , CodeVerifyRestView

urlpatterns = [
    path("singup/", SingUpView.as_view()),
    path("code_verify/", CodeVerifyView.as_view()),
    path("code_rest/" , CodeVerifyRestView.as_view())
]
