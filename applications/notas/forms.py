from django import forms
from .models import Nota

class NotaForm(forms.ModelForm):
    class Meta:
        model = Nota
        fields = ['titulo', 'contenido', 'color', 'es_importante']
        widgets = {
            'titulo': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Título de la nota...',
                'maxlength': '100'
            }),
            'contenido': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Escribe aquí el contenido de tu nota...',
                'rows': 6
            }),
            'color': forms.Select(attrs={
                'class': 'form-select'  # ✅ Cambiado de form-control a form-select
            }),
            'es_importante': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }
        labels = {
            'titulo': 'Título',
            'contenido': 'Contenido',
            'color': 'Color de la nota',
            'es_importante': 'Marcar como importante'
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Opcional: personalizar el placeholder del select
        self.fields['color'].empty_label = None  # Elimina "--------"