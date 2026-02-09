# applications/home/processors.py
import requests
from applications.home.models import Home

def home_contact(request):
    try:
        home = Home.objects.latest('created')
        phone = home.phone
        correo = home.contact_email
    except Home.DoesNotExist:
        phone = ''
        correo = ''

    return {
        'phone': phone,
        'correo': correo,
    }

# ip y clima

from django.conf import settings

def obtener_ip(request):
    """Context processor para obtener la IP"""

    context = {
        "mi_ip": request.META.get("REMOTE_ADDR", "No disponible"),
        "ciudad": "Lima",
        "pais": "PE",
    }

    # ❌ NO llamar ipapi en desarrollo
    if settings.DEBUG:
        return context

    try:
        url_ip = "https://ipapi.co/json/"
        response_ip = requests.get(url_ip, timeout=5)
        response_ip.raise_for_status()
        data_ip = response_ip.json()

        context["mi_ip"] = data_ip.get("ip", context["mi_ip"])
        context["ciudad"] = data_ip.get("city", "Lima")
        context["pais"] = data_ip.get("country_code", "PE")

    except requests.RequestException:
        pass  # no imprimir nada

    return context



def obtener_clima(request):
    """Context processor para obtener el clima actual"""

    context = {
        "temperatura": "N/A",
        "viento": "N/A",
        "direccion_viento": "N/A",
    }

    try:
        url_clima = (
            "https://api.open-meteo.com/v1/forecast"
            "?latitude=-12.0464"
            "&longitude=-77.0428"
            "&current_weather=true"
        )
        response_clima = requests.get(url_clima, timeout=5)
        response_clima.raise_for_status()
        data_clima = response_clima.json()

        clima_actual = data_clima.get("current_weather", {})

        context["temperatura"] = clima_actual.get("temperature", "N/A")
        context["viento"] = clima_actual.get("windspeed", "N/A")
        context["direccion_viento"] = clima_actual.get("winddirection", "N/A")

    except requests.RequestException as e:
        print(f"Error obteniendo clima: {e}")

    return context