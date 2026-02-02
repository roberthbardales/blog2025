from django import forms

from .models import Entry, Comment
from applications.users.models import User

class EntradaForm(forms.ModelForm):
    # Definir category explícitamente para quitar el "-------"
    category = forms.ModelChoiceField(
        queryset=None,  # Se establece en __init__
        empty_label=None,
        widget=forms.Select(
            attrs={
                'class': 'form-control form-control-sm',
            }
        )
    )

    class Meta:
        model = Entry
        fields = (
            'category',
            'tag',
            'title',
            'resume',
            'content',
            'public',
            'image',
            'portada',
            'in_home',
        )
        widgets = {
            'user': forms.Select(
                attrs={
                    'class': 'form-control form-control-sm',
                }
            ),
            'public': forms.CheckboxInput(
                attrs={
                    'checked': '',
                }
            ),
            'in_home': forms.CheckboxInput(
                attrs={
                    'checked': '',
                }
            ),
            'title': forms.TextInput(
                attrs={
                    'class': 'form-control form-control-sm',
                }
            ),
            'tag': forms.SelectMultiple(
                attrs={
                    'class': 'form-control form-control-sm w-85',
                    'size': '3',
                }
            ),
            'resume': forms.Textarea(
                attrs={
                    'class': 'form-control form-control-md',
                    'rows': '2',
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Establecer el queryset para category
        from applications.entrada.models import Category  # Ajusta el import según tu estructura
        self.fields['category'].queryset = Category.objects.all()

        # Seleccionar el primer tag por defecto en posts nuevos
        if not self.instance.pk and self.fields['tag'].queryset.exists():
            self.initial['tag'] = [self.fields['tag'].queryset.first().pk]


class CommentForm(forms.ModelForm):
    # Campo oculto para saber si es respuesta a otro comentario
    parent_id = forms.IntegerField(widget=forms.HiddenInput(), required=False)

    class Meta:
        model = Comment
        fields = ('content', 'parent_id')
        widgets = {
            'content': forms.Textarea(
                attrs={
                    'class': 'form-control form-control-sm w-100',
                    'rows': 3,
                    'placeholder': 'Escribe tu comentario...'
                }
            )
        }