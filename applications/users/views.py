from django.shortcuts import render
from django.core.mail import send_mail
from django.urls import reverse_lazy, reverse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

# DRF imports
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.auth import authenticate, login, get_user_model
from firebase_admin import auth as firebase_auth
from .mixins import UsuarioAPIMixin, AdministradorAPIMixin

from django.views.generic import (
    View,
    TemplateView,
    CreateView,
    ListView,
)
from django.views.generic.edit import FormView

from .forms import (
    UserRegisterForm,
    LoginForm,
    UpdatePasswordForm,
)
from .models import User
from django.contrib.auth import get_user_model, login


class UserRegisterView(FormView):
    template_name = 'users/register.html'
    form_class = UserRegisterForm
    success_url = reverse_lazy('users_app:user-login')

    def form_valid(self, form):
        user = User.objects.create_user(
            form.cleaned_data['email'],
            form.cleaned_data['password1'],
            full_name=form.cleaned_data['full_name'],
            ocupation=form.cleaned_data['ocupation'],
            genero=form.cleaned_data['genero'],
            date_birth=form.cleaned_data['date_birth'],
            avatar=form.cleaned_data.get('avatar'),
        )
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
        return HttpResponseRedirect(reverse('users_app:user-login'))


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


class UserListView(LoginRequiredMixin, ListView):
    template_name = "users/lista_usuarios.html"
    context_object_name = 'usuarios'
    success_url = reverse_lazy('entrada_app:entry-lista')
    login_url = reverse_lazy('entrada_app:entry-lista')

    def get_queryset(self):
        return User.objects.usuarios_sistema()


@method_decorator(csrf_exempt, name='dispatch')
class FirebaseLoginView(APIView):
    authentication_classes = []  # ← DRF no intenta autenticar
    permission_classes = []      # ← sin restricciones de permiso

    def post(self, request):
        id_token = request.data.get("idToken")
        if not id_token:
            return Response({"error": "No se envió token"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            decoded = firebase_auth.verify_id_token(id_token)
        except Exception as e:
            return Response({"error": f"Token inválido: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)

        email = decoded.get("email")
        name = decoded.get("name", "")
        picture = decoded.get("picture")

        if not email:
            return Response({"error": "El token no contiene email válido"}, status=status.HTTP_400_BAD_REQUEST)

        user, created = User.objects.get_or_create(
            email=email,
            defaults={
                "full_name": name or "",
                "ocupation": User.USUARIO,
                "is_active": True,
                "is_staff": False,
                "avatar_url": picture or "",
            }
        )

        if not created:
            if not user.avatar and picture:
                user.avatar_url = picture
                user.save()
        else:
            user.set_unusable_password()
            user.save()

        login(request, user, backend='applications.users.backends.FirebaseBackend')

        return Response({
            "message": "✅ Autenticado correctamente",
            "nuevo_usuario": created,
            "email": user.email,
        }, status=status.HTTP_200_OK)


class FirebaseLogoutView(APIView):
    def post(self, request):
        logout(request)
        return Response({"message": "✅ Sesión cerrada correctamente"}, status=status.HTTP_200_OK)


def login_google_view(request):
    return render(request, "users/login_google.html")


def firebase_datos_view(request):
    return render(request, "users/firebase_datos.html")


class SobreMiAPIView(UsuarioAPIMixin, APIView):
    def get(self, request):
        user = request.user
        data = {
            "nombre": user.full_name,
            "email": user.email,
            "rol": user.get_ocupation_display(),
        }
        return Response(data, status=status.HTTP_200_OK)