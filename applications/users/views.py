from django.shortcuts import render
from django.core.mail import send_mail
from django.urls import reverse_lazy, reverse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect

# DRF imports
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.auth import authenticate, login


from django.views.generic import (
    View,
    TemplateView,
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


from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from firebase_admin import auth as firebase_auth
from django.contrib.auth import get_user_model, login
from .permissions import EsUsuario

User = get_user_model()


class FirebaseLoginView(APIView):
    """
    🔐 Autenticación con Firebase (Google)
    - Verifica el token de Firebase.
    - Crea el usuario si no existe.
    - Marca is_active, is_staff y ocupation en true/'Usuario'.
    - Inicia sesión en Django.
    """
    # No agregamos permission_classes aquí porque el usuario aún no está logueado

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
        if not email:
            return Response({"error": "El token no contiene email válido"}, status=status.HTTP_400_BAD_REQUEST)

        user, created = User.objects.get_or_create(
            email=email,
            defaults={
                "full_name": name or "",
                "ocupation": User.USUARIO,
                "is_active": True,
                "is_staff": True,
            }
        )

        if not user.is_superuser:
            user.is_active = True
            user.is_staff = True
            user.ocupation = User.USUARIO
            user.set_unusable_password()
            user.save()

        login(request, user, backend='applications.users.backends.FirebaseBackend')
        # login(request, user, backend='applications.users.backends.FirebaseAuthentication')


        return Response({
            "message": "✅ Autenticado correctamente",
            "email": user.email,
            "nuevo_usuario": created,
            "superusuario": user.is_superuser
        }, status=status.HTTP_200_OK)




def login_google_view(request):
    return render(request, "users/login_google.html")


from rest_framework.views import APIView
from rest_framework.response import Response
from .permissions import EsUsuario

class MiVistaProtegida(APIView):
    permission_classes = [EsUsuario]

    def get(self, request):
        return Response({"message": f"Hola {request.user.full_name}, acceso permitido"})



def firebase_datos_view(request):
    return render(request, "users/firebase_datos.html")



#pruebas API

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .permissions import EsUsuario

class SobreMiAPIView(APIView):
    permission_classes = [EsUsuario]

    def get(self, request):
        user = request.user
        data = {
            "nombre": user.full_name,
            "email": user.email,
            "rol": user.get_ocupation_display(),
        }
        return Response(data, status=status.HTTP_200_OK)
