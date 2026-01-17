from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework import generics
from rest_framework.permissions import AllowAny
from .serializer import SingUpSerializer , CodeVerifySerializer
from rest_framework.response import Response
from .models import User


class SingUpView(generics.CreateAPIView):
    permission_classes = [AllowAny]
    queryset = User.objects.all()
    serializer_class = SingUpSerializer
    
class CodeVerifyView(APIView):
    
    def post(self , request , *args , **kwargs ):
        serializer = CodeVerifySerializer(request.data)
        


# Create your views here.
