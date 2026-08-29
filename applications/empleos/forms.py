from django import forms

SENIORITY_OPCIONES = [
    ("1", "Prácticas"),
    ("2", "Junior"),
    ("3", "Semi Senior"),
    ("4", "Senior"),
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
