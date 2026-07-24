from django import forms

from .models import Entry, Comment
from applications.users.models import User

TW_INPUT = 'w-full rounded-xl border border-slate-300 bg-slate-50 px-3 py-2 text-sm text-slate-700 transition focus:border-blue-500 focus:ring-2 focus:ring-blue-100 focus:outline-none'
TW_CHECKBOX = 'w-4 h-4 accent-blue-500 cursor-pointer'


class EntradaForm(forms.ModelForm):
    category = forms.ModelChoiceField(
        queryset=None,
        empty_label=None,
        widget=forms.Select(attrs={'class': TW_INPUT})
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
            'user': forms.Select(attrs={'class': TW_INPUT}),
            'public': forms.CheckboxInput(attrs={'class': TW_CHECKBOX, 'checked': ''}),
            'in_home': forms.CheckboxInput(attrs={'class': TW_CHECKBOX, 'checked': ''}),
            'title': forms.TextInput(attrs={'class': TW_INPUT}),
            'tag': forms.SelectMultiple(attrs={'class': TW_INPUT, 'size': '3'}),
            'resume': forms.Textarea(attrs={'class': TW_INPUT, 'rows': '2'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from applications.entrada.models import Category
        self.fields['category'].queryset = Category.objects.all()

        if not self.instance.pk and self.fields['tag'].queryset.exists():
            self.initial['tag'] = [self.fields['tag'].queryset.first().pk]


class CommentForm(forms.ModelForm):
    parent_id = forms.IntegerField(widget=forms.HiddenInput(), required=False)

    class Meta:
        model = Comment
        fields = ('content', 'parent_id')
        widgets = {
            'content': forms.Textarea(attrs={
                'class': TW_INPUT,
                'rows': 3,
                'placeholder': 'Escribe tu comentario...'
            })
        }