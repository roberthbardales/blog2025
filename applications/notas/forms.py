from django import forms
from .models import Nota

TW = 'w-full rounded-xl border border-slate-300 bg-slate-50 px-3 py-2 text-sm text-slate-700 transition focus:border-blue-500 focus:ring-2 focus:ring-blue-100 focus:outline-none'
TW_CHECK = 'w-4 h-4 accent-blue-500 cursor-pointer'


class NotaForm(forms.ModelForm):
    class Meta:
        model = Nota
        fields = ['titulo', 'contenido', 'color', 'es_importante']
        widgets = {
            'titulo': forms.TextInput(attrs={
                'class': TW,
                'placeholder': 'Título de la nota...',
                'maxlength': '100'
            }),
            'contenido': forms.Textarea(attrs={
                'class': TW,
                'placeholder': 'Escribe aquí el contenido de tu nota...',
                'rows': 6
            }),
            'color': forms.Select(attrs={'class': TW}),
            'es_importante': forms.CheckboxInput(attrs={'class': TW_CHECK})
        }
        labels = {
            'titulo': 'Título',
            'contenido': 'Contenido',
            'color': 'Color de la nota',
            'es_importante': 'Marcar como importante'
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['color'].empty_label = None