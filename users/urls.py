from django.urls import path
from .views import CreateEmailView
urlpatterns = [
    path("singup/" , CreateEmailView.as_view())
]