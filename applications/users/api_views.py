from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from .serializers import UserRegisterSerializer, UserProfileSerializer
from .permissions import EsAdministrador
from .models import User  # ← faltaba esto


class UserRegisterAPIView(generics.CreateAPIView):
    serializer_class = UserRegisterSerializer
    permission_classes = [AllowAny]


class UserProfileAPIView(generics.RetrieveUpdateAPIView):
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user


class UserListAPIView(generics.ListAPIView):
    serializer_class = UserProfileSerializer
    permission_classes = [EsAdministrador]

    def get_queryset(self):
        return User.objects.usuarios_sistema()