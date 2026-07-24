from django import forms
from django.contrib.auth import authenticate
#
from .models import User

TW = 'w-full rounded-xl border border-slate-300 bg-slate-50 px-3 py-2 text-sm text-slate-700 transition focus:border-blue-500 focus:ring-2 focus:ring-blue-100 focus:outline-none'


class UserRegisterForm(forms.ModelForm):

    password1 = forms.CharField(
        label='Contraseña',
        required=True,
        widget=forms.PasswordInput(attrs={'placeholder': 'Contraseña', 'class': TW})
    )
    password2 = forms.CharField(
        label='Contraseña',
        required=True,
        widget=forms.PasswordInput(attrs={'placeholder': 'Repetir Contraseña', 'class': TW})
    )

    class Meta:
        model = User
        fields = (
            'email',
            'full_name',
            'ocupation',
            'genero',
            'date_birth',
            'avatar',
        )
        widgets = {
            'email': forms.EmailInput(attrs={'placeholder': 'Correo Electronico ...', 'class': TW}),
            'full_name': forms.TextInput(attrs={'placeholder': 'nombres ...', 'class': TW}),
            'ocupation': forms.Select(attrs={'class': TW}),
            'genero': forms.Select(attrs={'class': TW}),
            'date_birth': forms.DateInput(attrs={'type': 'date', 'class': TW}),
            'avatar': forms.FileInput(attrs={'accept': 'image/*'}),
        }

    def clean_password2(self):
        if self.cleaned_data['password1'] != self.cleaned_data['password2']:
            self.add_error('password2', 'Las contraseñas no son iguales')


class LoginForm(forms.Form):
    email = forms.CharField(
        required=True,
        widget=forms.TextInput(attrs={'placeholder': 'Correo Electronico', 'class': TW})
    )
    password = forms.CharField(
        required=True,
        widget=forms.PasswordInput(attrs={'placeholder': 'contraseña', 'class': TW})
    )

    def clean(self):
        cleaned_data = super(LoginForm, self).clean()
        email = self.cleaned_data['email']
        password = self.cleaned_data['password']

        if not authenticate(email=email, password=password):
            raise forms.ValidationError('Los datos de usuario no son correctos')

        return self.cleaned_data


class UpdatePasswordForm(forms.Form):

    current_password = forms.CharField(
        label='Contraseña Actual',
        required=True,
        widget=forms.PasswordInput(attrs={'placeholder': ' ', 'class': TW})
    )
    new_password = forms.CharField(
        label='Contraseña Nueva',
        required=True,
        widget=forms.PasswordInput(attrs={'placeholder': ' ', 'class': TW})
    )
