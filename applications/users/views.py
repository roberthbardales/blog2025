from django.shortcuts import render
from django.core.mail import send_mail
from django.urls import reverse_lazy, reverse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect

from django.views.generic import (
    View,
    CreateView,
    ListView,
)

from django.views.generic.edit import (
    FormView
)

from .forms import (
    UserRegisterForm,
    LoginForm,
    UpdatePasswordForm,
)
#
from .models import User
#

from django.contrib.auth import get_user_model, login
from rest_framework.authentication import BaseAuthentication
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from firebase_admin import auth as firebase_auth
from rest_framework import exceptions

User = get_user_model()

class FirebaseGoogleLoginAPIView(APIView):
    def post(self, request):
        id_token = request.data.get('id_token')
        if not id_token:
            return Response({'error': 'Falta el token.'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            decoded = firebase_auth.verify_id_token(id_token)
            email = decoded.get('email')
            name = decoded.get('name', '')

            # Buscar o crear usuario
            user, created = User.objects.get_or_create(email=email, defaults={
                'full_name': name,
                'is_active': True
            })

            # Autenticar en Django
            login(request, user)

            return Response({
                'message': '✅ Usuario autenticado con Google correctamente.',
                'email': email,
                'nombre': name,
            })
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class FirebaseAuthentication(BaseAuthentication):
    def authenticate(self, request):
        id_token = request.headers.get('Authorization')
        if not id_token:
            return None
        try:
            decoded = firebase_auth.verify_id_token(id_token)
            email = decoded.get('email')
            if not email:
                raise exceptions.AuthenticationFailed('Email no encontrado en token')
            user, _ = User.objects.get_or_create(email=email)
            return (user, None)
        except Exception:
            raise exceptions.AuthenticationFailed('Token inválido')


class UserRegisterView(FormView):
    template_name = 'users/register.html'
    form_class = UserRegisterForm
    success_url = reverse_lazy('users_app:user-login')

    def form_valid(self, form):
        #
        User.objects.create_user(
            form.cleaned_data['email'],
            form.cleaned_data['password1'],
            full_name=form.cleaned_data['full_name'],
            ocupation=form.cleaned_data['ocupation'],
            genero=form.cleaned_data['genero'],
            date_birth=form.cleaned_data['date_birth'],
        )
        # enviar el codigo al email del user
        return super(UserRegisterView, self).form_valid(form)



class LoginUser(FormView):
    template_name = 'users/login.html'
    form_class = LoginForm
    success_url = reverse_lazy('favoritos_app:perfil')

    def form_valid(self, form):
        user = authenticate(
            email=form.cleaned_data['email'],
            password=form.cleaned_data['password']
        )
        login(self.request, user)
        return super(LoginUser, self).form_valid(form)


class LogoutView(View):

    def get(self, request, *args, **kargs):
        logout(request)
        return HttpResponseRedirect(
            reverse(
                'users_app:user-login'
            )
        )

class UpdatePasswordView(LoginRequiredMixin, FormView):
    template_name = 'users/cambiar_contraseña.html'
    form_class = UpdatePasswordForm
    success_url = reverse_lazy('users_app:user-login')
    login_url = reverse_lazy('users_app:user-login')

    def form_valid(self, form):
        usuario = self.request.user
        user = authenticate(
            email=usuario.email,
            password=form.cleaned_data['password1']

        )

        if user:
            new_password = form.cleaned_data['password2']
            usuario.set_password(new_password)
            usuario.save()

        logout(self.request)
        return super(UpdatePasswordView, self).form_valid(form)

class UserListView(LoginRequiredMixin,ListView):
    template_name = "users/lista_usuarios.html"
    context_object_name = 'usuarios'
    success_url = reverse_lazy('entrada_app:entry-lista')
    login_url = reverse_lazy('entrada_app:entry-lista')

    def get_queryset(self):
        return User.objects.usuarios_sistema()

# ============================
# 🔥 probar FIREBASE
# ============================

# from rest_framework.views import APIView
# from rest_framework.response import Response
# from rest_framework.permissions import IsAuthenticated
# from .authentication import FirebaseAuthentication

# #probar endpoint con postman, primero ejecuta get_token
# class PerfilUsuario(APIView):
#     authentication_classes = [FirebaseAuthentication]
#     permission_classes = [IsAuthenticated]

#     def get(self, request):
#         user = request.user
#         return Response({
#             "mensaje": f"Bienvenido {user.full_name or user.email}",
#             "email": user.email,
#         })

