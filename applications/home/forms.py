
from logging import PlaceHolder
from django import forms

# models
from .models import Contact, Suscribers

TW = 'w-full rounded-xl border border-slate-300 bg-slate-50 px-3 py-2 text-sm text-slate-700 transition focus:border-blue-500 focus:ring-2 focus:ring-blue-100 focus:outline-none'


class SuscribersForm(forms.ModelForm):
    class Meta:
        model= Suscribers
        fields=(
            'email',

        )
        widgets={
            'email':forms.EmailInput(
                attrs={
                    'placeHolder':'Correo Electronico ...',
                    'class': TW,
                }
            )
        }

class ContactForm(forms.ModelForm):
    class Meta:
        model = Contact
        fields = ['full_name', 'email', 'messagge']

