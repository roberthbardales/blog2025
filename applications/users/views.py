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
from .serializers import FirebaseAuthSerializer, UserSerializer
from django.contrib.auth import authenticate, login


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

# --- Endpoint API: login con Firebase (usa serializer) ---
class FirebaseLoginAPI(APIView):
    """
    POST JSON { "idToken": "..." }
    Valida token con Firebase, crea o vincula usuario y devuelve datos del usuario.
    Además inicia sesión en Django (cookie) si es llamado desde web.
    """
    permission_classes = []  # permitido a todos
    authentication_classes = []  # no usar auth previa

    def post(self, request, *args, **kwargs):
        serializer = FirebaseAuthSerializer(data=request.data, context={'request': request})
        if not serializer.is_valid():
            return Response({'ok': False, 'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

        user = serializer.create_or_get_user()

        # Opcional: iniciar sesión con cookie de Django (útil para web)
        # Si prefieres usar JWT para APIs, aquí emitirías token JWT en su lugar.
        login(request, user)

        user_data = UserSerializer(user).data
        return Response({'ok': True, 'user': user_data}, status=status.HTTP_200_OK)

#probar firebase

# def firebase_login(request):
#     return render(request, "users/firebase_login.html")


# from rest_framework.views import APIView
# from rest_framework.response import Response
# from rest_framework.permissions import AllowAny
# from .authentication import FirebaseAuthentication

