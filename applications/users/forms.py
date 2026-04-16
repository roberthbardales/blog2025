from django import forms
from django.contrib.auth import authenticate
#
from .models import User

class UserRegisterForm(forms.ModelForm):

    password1 = forms.CharField(
        label='Contraseña',
        required=True,
        widget=forms.PasswordInput(
            attrs={
                'placeholder': 'Contraseña',
                'class':'form-control rounded'
            }
        )
    )
    password2 = forms.CharField(
        label='Contraseña',
        required=True,
        widget=forms.PasswordInput(
            attrs={
                'placeholder': 'Repetir Contraseña',
                'class':'form-control rounded',
            }
        )
    )

    class Meta:
        """Meta definition for Userform."""

        model = User
        fields = (
            'email',
            'full_name',
            'ocupation',
            'genero',
            'date_birth',
            'avatar',  # ✅ Campo avatar agregado
        )
        widgets = {
            'email': forms.EmailInput(
                attrs={
                    'placeholder': 'Correo Electronico ...',
                    'class':'form-control rounded'
                }
            ),
            'full_name': forms.TextInput(
                attrs={
                    'placeholder': 'nombres ...',
                    'class':'form-control rounded'
                }
            ),
            'ocupation': forms.Select(
                attrs={
                    'class':'form-control rounded',

                }
            ),
            'genero': forms.Select(
                attrs={
                    'placeholder': 'Genero ...',
                    'class':'form-control rounded',
                }
            ),
            'date_birth': forms.DateInput(
                attrs={
                    'type': 'date',
                    'class':'form-control rounded'
                },
            ),
            'avatar': forms.FileInput(
                attrs={
                    'accept': 'image/*'  # Solo acepta imágenes
                }
            ),
        }

    def clean_password2(self):
        if self.cleaned_data['password1'] != self.cleaned_data['password2']:
            self.add_error('password2', 'Las contraseñas no son iguales')


class LoginForm(forms.Form):
    email = forms.CharField(
        required=True,
        widget=forms.TextInput(
            attrs={
                'placeholder': 'Correo Electronico',
                'class':'form-control rounded',
            }
        )
    )
    password = forms.CharField(
        required=True,
        widget=forms.PasswordInput(
            attrs={
                'placeholder': 'contraseña',
                'class':'form-control rounded',
            }
        )
    )

    def clean(self):
        cleaned_data = super(LoginForm, self).clean()
        email = self.cleaned_data['email']
        password = self.cleaned_data['password']

        if not authenticate(email=email, password=password):
            raise forms.ValidationError('Los datos de usuario no son correctos')

        return self.cleaned_data


class UpdatePasswordForm(forms.Form):

    password1 = forms.CharField(
        label='Contraseña Actual',
        required=True,
        widget=forms.PasswordInput(
            attrs={
                'placeholder': ' ',
                'class':'form-control mr-sm-2',
            }
        )
    )
    password2 = forms.CharField(
        label='Contraseña Nueva',
        required=True,
        widget=forms.PasswordInput(
            attrs={
                'placeholder': ' ',
                'class':'form-control mr-sm-2',
            }
        )
    )
