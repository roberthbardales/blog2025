# applications/processors.py
import requests
from django.core.cache import cache
from django.conf import settings
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


def solicitudes_pendientes(request):
    if not request.user.is_authenticated:
        return {}
    from applications.amigos.models import Friendship
    count = Friendship.objects.filter(
        receiver=request.user,
        status='pending'
    ).count()
    return {'solicitudes_pendientes': count}


def obtener_ip(request):
    """Context processor para obtener la IP del visitante.
    
    Caché: 24 horas por IP (para no repetir geolocalización).
    En DEBUG retorna valores hardcodeados sin llamar a la API.
    """
    raw_ip = request.META.get("REMOTE_ADDR", "No disponible")

    context = {
        "mi_ip": raw_ip,
        "ciudad": "Lima",
        "pais": "PE",
    }

    # En desarrollo no llamar a la API externa
    if settings.DEBUG:
        return context

    # Intentar obtener de caché primero
    cache_key = f"ip_location_{raw_ip}"
    cached = cache.get(cache_key)
    if cached:
        context.update(cached)
        return context

    try:
        url_ip = "https://ipapi.co/json/"
        response_ip = requests.get(url_ip, timeout=5)
        response_ip.raise_for_status()
        data_ip = response_ip.json()

        result = {
            "mi_ip": data_ip.get("ip", raw_ip),
            "ciudad": data_ip.get("city", "Lima"),
            "pais": data_ip.get("country_code", "PE"),
        }
        context.update(result)

        # Guardar en caché por 24 horas
        cache.set(cache_key, result, timeout=86400)

    except requests.RequestException:
        pass  # Mantener valores por defecto

    return context


def obtener_clima(request):
    """Context processor para obtener el clima actual de Lima.
    
    Caché: 30 minutos (el clima no cambia tan rápido).
    """
    context = {
        "temperatura": "N/A",
        "viento": "N/A",
        "direccion_viento": "N/A",
    }

    # Intentar obtener de caché primero
    cache_key = "clima_lima"
    cached = cache.get(cache_key)
    if cached:
        context.update(cached)
        return context

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

        result = {
            "temperatura": clima_actual.get("temperature", "N/A"),
            "viento": clima_actual.get("windspeed", "N/A"),
            "direccion_viento": clima_actual.get("winddirection", "N/A"),
        }
        context.update(result)

        # Guardar en caché por 30 minutos
        cache.set(cache_key, result, timeout=1800)

    except requests.RequestException as e:
        print(f"Error obteniendo clima: {e}")

    return context
