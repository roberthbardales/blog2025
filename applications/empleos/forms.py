from django import forms

from .models import FiltroEmpleo

SENIORITY_OPCIONES = [
    ("1", "Prácticas"),
    ("2", "Junior"),
    ("3", "Semi Senior"),
    ("4", "Senior"),
]

PAISES = [
    ("", "Elegir país…"),
    ("1", "Perú"),
    ("2", "México"),
    ("3", "Colombia"),
    ("4", "Chile"),
    ("5", "Argentina"),
    ("6", "España"),
]


class BusquedaForm(forms.Form):
    search = forms.CharField(required=False)
    country_id = forms.CharField(required=False)
    from_age = forms.CharField(required=False)
    max_pages = forms.IntegerField(required=False, min_value=1, max_value=10, initial=3)
    job_seniority = forms.MultipleChoiceField(
        choices=SENIORITY_OPCIONES,
        required=False,
    )


class FiltroEmpleoForm(forms.ModelForm):
    job_seniority = forms.MultipleChoiceField(
        choices=SENIORITY_OPCIONES,
        required=False,
        label='Niveles (seniority)',
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'mr-1'}),
    )
    country_id = forms.ChoiceField(
        choices=PAISES,
        required=False,
        label='País',
    )
    work_modality_id = forms.CharField(required=False, label='Modalidad (IDs)',
        widget=forms.TextInput(attrs={'class': 'w-full rounded-lg border border-slate-300 px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition', 'placeholder': 'IDs separados por coma, ej: 1,2'}))
    job_category_id = forms.CharField(required=False, label='Categoría (IDs)',
        widget=forms.TextInput(attrs={'class': 'w-full rounded-lg border border-slate-300 px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition', 'placeholder': 'IDs separados por coma'}))
    job_type_id = forms.CharField(required=False, label='Tipo de empleo (IDs)',
        widget=forms.TextInput(attrs={'class': 'w-full rounded-lg border border-slate-300 px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition', 'placeholder': 'IDs separados por coma'}))

    class Meta:
        model = FiltroEmpleo
        fields = [
            'nombre', 'activo', 'keywords', 'max_pages',
            'country_id', 'from_age',
            'job_seniority', 'work_modality_id', 'job_category_id', 'job_type_id',
            'salary_min', 'salary_max', 'currency_type', 'p_english_req',
            'email_destino', 'telegram_chat_id',
        ]
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'w-full rounded-lg border border-slate-300 px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition'}),
            'keywords': forms.TextInput(attrs={'class': 'w-full rounded-lg border border-slate-300 px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition', 'placeholder': 'python, django, linux'}),
            'max_pages': forms.NumberInput(attrs={'class': 'w-full rounded-lg border border-slate-300 px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition', 'min': 1, 'max': 10}),
            'from_age': forms.Select(choices=[('', 'Cualquier fecha'), ('1', 'Último día'), ('3', 'Últimos 3 días'), ('7', 'Última semana'), ('30', 'Último mes')], attrs={'class': 'w-full rounded-lg border border-slate-300 px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition'}),
            'salary_min': forms.NumberInput(attrs={'class': 'w-full rounded-lg border border-slate-300 px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition'}),
            'salary_max': forms.NumberInput(attrs={'class': 'w-full rounded-lg border border-slate-300 px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition'}),
            'currency_type': forms.TextInput(attrs={'class': 'w-full rounded-lg border border-slate-300 px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition', 'placeholder': 'p. ej. soles, usd'}),
            'email_destino': forms.EmailInput(attrs={'class': 'w-full rounded-lg border border-slate-300 px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition'}),
            'telegram_chat_id': forms.TextInput(attrs={'class': 'w-full rounded-lg border border-slate-300 px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition'}),
            'activo': forms.CheckboxInput(attrs={'class': 'w-4 h-4 rounded border-slate-300 text-blue-600 focus:ring-blue-500'}),
            'p_english_req': forms.Select(choices=[('', '—'), (1, 'Sí'), (0, 'No')], attrs={'class': 'w-full rounded-lg border border-slate-300 px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        instance = kwargs.get('instance')
        if instance and instance.pk:
            self.fields['job_seniority'].initial = [str(x) for x in (instance.job_seniority or [])]
            if instance.country_id:
                self.fields['country_id'].initial = str(instance.country_id)
            self.fields['currency_type'].widget.attrs['placeholder'] = 'p. ej. soles, usd'

    def clean_keywords(self):
        keywords = self.cleaned_data.get('keywords') or ''
        partes = [k.strip() for k in keywords.split(',') if k.strip()]
        return ', '.join(partes)

    def clean_country_id(self):
        value = self.cleaned_data.get('country_id') or None
        return int(value) if value else None

    def clean_work_modality_id(self):
        return self._clean_id_list(self.cleaned_data.get('work_modality_id'))

    def clean_job_category_id(self):
        return self._clean_id_list(self.cleaned_data.get('job_category_id'))

    def clean_job_type_id(self):
        return self._clean_id_list(self.cleaned_data.get('job_type_id'))

    def _clean_id_list(self, value):
        if not value:
            return []
        if isinstance(value, list):
            return [int(x) for x in value if x]
        return [int(x.strip()) for x in str(value).split(',') if x.strip()]

    def clean(self):
        cleaned = super().clean()
        cleaned['job_seniority'] = [int(x) for x in cleaned.get('job_seniority') or []]
        return cleaned
