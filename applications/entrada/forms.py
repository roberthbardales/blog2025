

from django  import forms

from .models import Entry,Comment
from applications.users.models import User

class EntradaForm(forms.ModelForm):

    class Meta:
        model = Entry
        #fields =(__all_)
        fields =(
        # 'user',
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
        widgets={

            'user':forms.Select(
                attrs={
                'class':'form-control form-control-sm',

                }
            ),
            'category':forms.Select(
                attrs={
                'class':'form-control form-control-sm',
                }
            ),
            'public':forms.CheckboxInput(
                attrs={
                    'checked':'',
                }
            ),
            'in_home':forms.CheckboxInput(
                attrs={
                    'checked':'',
                }
            ),
            'title':forms.TextInput(
                attrs={
                    'class':'form-control form-control-sm',
                }
            ),
            'tag':forms.SelectMultiple(
                attrs={

                    'class':'form-control form-control-sm w-85',
                }
            ),
            'resume':forms.Textarea(
                attrs={
                    'class':'form-control form-control-md',
                    'rows':'2',
                }
            ),

        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Quitar el "---------" del select
        self.fields['category'].empty_label = None


class CommentForm(forms.ModelForm):
    # Campo oculto para saber si es respuesta a otro comentario
    parent_id = forms.IntegerField(widget=forms.HiddenInput(), required=False)

    class Meta:
        model = Comment
        fields = ('content', 'parent_id')  # agregamos parent_id
        widgets = {
            'content': forms.Textarea(
                attrs={
                    'class': 'form-control form-control-sm w-100',
                    'rows': 3,
                    'placeholder': 'Escribe tu comentario...'
                }
            )
        }

