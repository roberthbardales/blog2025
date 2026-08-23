import json

from django import forms
from django.forms import inlineformset_factory

from .models import Opcion, Pregunta, Tema

TW = 'w-full rounded-xl border border-slate-300 bg-slate-50 px-3 py-2 text-sm text-slate-700 transition focus:border-blue-500 focus:ring-2 focus:ring-blue-100 focus:outline-none'
TW_CHECK = 'w-4 h-4 accent-blue-500 cursor-pointer'


class TemaForm(forms.ModelForm):
    class Meta:
        model = Tema
        fields = ['nombre', 'descripcion']
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': TW,
                'placeholder': 'Ej: Django',
            }),
            'descripcion': forms.Textarea(attrs={
                'class': TW,
                'placeholder': 'Descripción del banco de preguntas (opcional)...',
                'rows': 3,
            }),
        }


class PreguntaForm(forms.ModelForm):
    class Meta:
        model = Pregunta
        fields = ['texto', 'nivel', 'explicacion']
        widgets = {
            'texto': forms.Textarea(attrs={
                'class': TW,
                'placeholder': 'Escribe aquí la pregunta...',
                'rows': 3,
            }),
            'nivel': forms.Select(attrs={'class': TW}),
            'explicacion': forms.Textarea(attrs={
                'class': TW,
                'placeholder': 'Explicación de la respuesta correcta (opcional)...',
                'rows': 2,
            }),
        }


class OpcionForm(forms.ModelForm):
    class Meta:
        model = Opcion
        fields = ['texto', 'es_correcta']
        widgets = {
            'texto': forms.TextInput(attrs={
                'class': TW,
                'placeholder': 'Texto de la opción...',
            }),
            'es_correcta': forms.CheckboxInput(attrs={'class': TW_CHECK}),
        }

    def clean(self):
        cleaned_data = super().clean()
        texto = cleaned_data.get('texto')
        if texto and not texto.strip():
            self.add_error('texto', 'El texto de la opción no puede estar vacío')
        return cleaned_data


OpcionFormSet = inlineformset_factory(
    Pregunta,
    Opcion,
    form=OpcionForm,
    extra=4,
    min_num=2,
    validate_min=True,
)


class ConfigurarEvaluacionForm(forms.Form):
    """Configuración runtime de la evaluación"""

    TODOS = 'todos'
    EXAMEN = 'examen'
    PRACTICA = 'practica'

    MODO_CHOICES = (
        (EXAMEN, 'Examen (corrección al final)'),
        (PRACTICA, 'Práctica (corrección al instante)'),
    )

    nivel = forms.ChoiceField(
        label='Nivel',
        choices=[],
        required=False,
        widget=forms.Select(attrs={'class': TW}),
    )
    cantidad = forms.IntegerField(
        label='Cantidad de preguntas',
        min_value=1,
        initial=10,
        widget=forms.NumberInput(attrs={'class': TW}),
    )
    modo = forms.ChoiceField(
        label='Modo',
        choices=MODO_CHOICES,
        initial=EXAMEN,
        widget=forms.Select(attrs={'class': TW}),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        niveles = [('', 'Todos los niveles')] + list(Pregunta.NIVEL_CHOICES)
        self.fields['nivel'].choices = niveles


class ImportarJSONForm(forms.Form):
    """Upload de preguntas en formato JSON"""

    archivo = forms.FileField(
        label='Archivo JSON',
        widget=forms.ClearableFileInput(attrs={
            'class': 'w-full rounded-xl border border-slate-300 bg-slate-50 px-3 py-2 '
                     'text-sm text-slate-700 file:mr-3 file:rounded-lg file:border-0 '
                     'file:bg-blue-600 file:px-4 file:py-2 file:text-sm file:font-medium '
                     'file:text-white hover:file:bg-blue-700 transition cursor-pointer'
        })
    )

    def clean_archivo(self):
        archivo = self.cleaned_data['archivo']
        if not archivo.name.lower().endswith('.json'):
            raise forms.ValidationError('El archivo debe tener extensión .json')

        try:
            contenido = json.loads(archivo.read().decode('utf-8'))
        except (UnicodeDecodeError, json.JSONDecodeError):
            raise forms.ValidationError('El archivo no contiene un JSON válido')

        if isinstance(contenido, dict):
            contenido = contenido.get('preguntas', [])

        if not isinstance(contenido, list) or not contenido:
            raise forms.ValidationError(
                'El JSON debe ser una lista de preguntas no vacía '
                '(o un objeto con la clave "preguntas")'
            )

        self.cleaned_data['datos'] = contenido
        return archivo
