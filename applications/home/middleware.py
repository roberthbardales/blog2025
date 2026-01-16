# middleware.py
import requests
import time
from .models import VisitorLog, IPLocation

class VisitorLogMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.last_request_time = 0
        self.min_interval = 1.5

    def __call__(self, request):
        # ⭐ SOLO registrar la página de inicio
        if request.path != '/':
            return self.get_response(request)

        # Obtener la IP del visitante
        ip = self.get_client_ip(request)

        # Buscar o crear la ubicación de esta IP
        ip_location, created = IPLocation.objects.get_or_create(
            ip_address=ip,
            defaults={
                'country': '',
                'city': '',
                'region': '',
                'latitude': None,
                'longitude': None
            }
        )

        # Si es una IP nueva o no tiene datos, consultar la API
        if created or not ip_location.city:
            location_data = self.get_location_with_rate_limit(ip)
            if location_data:
                ip_location.country = location_data.get('country', '')
                ip_location.city = location_data.get('city', '')
                ip_location.region = location_data.get('region', '')
                ip_location.latitude = location_data.get('latitude')
                ip_location.longitude = location_data.get('longitude')
                ip_location.save()

        # Registrar la visita a la página de inicio
        VisitorLog.objects.create(
            ip_location=ip_location,
            user_agent=request.META.get('HTTP_USER_AGENT', '')[:500],
            path=request.path[:500]
        )

        response = self.get_response(request)
        return response

    def get_client_ip(self, request):
        """Obtiene la IP real del cliente"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip

    def get_location_with_rate_limit(self, ip):
        """Obtiene la ubicación usando ip-api.com respetando rate limits"""

        # No consultar IPs locales
        if ip in ['127.0.0.1', 'localhost', '::1']:
            return {
                'country': 'Local',
                'city': 'Localhost',
                'region': 'Development',
                'latitude': 0.0,
                'longitude': 0.0
            }

        # Respetar el rate limit (45 req/min)
        current_time = time.time()
        time_since_last = current_time - self.last_request_time

        if time_since_last < self.min_interval:
            time.sleep(self.min_interval - time_since_last)

        try:
            # Consultar ip-api.com
            response = requests.get(
                f'http://ip-api.com/json/{ip}?fields=status,country,city,regionName,lat,lon',
                timeout=5
            )
            self.last_request_time = time.time()

            if response.status_code == 200:
                data = response.json()

                if data.get('status') == 'success':
                    return {
                        'country': data.get('country', ''),
                        'city': data.get('city', ''),
                        'region': data.get('regionName', ''),
                        'latitude': data.get('lat'),
                        'longitude': data.get('lon')
                    }
                else:
                    print(f"IP API error para {ip}: {data.get('message', 'Unknown')}")

        except requests.RequestException as e:
            print(f"Error de red obteniendo ubicación para {ip}: {e}")
        except Exception as e:
            print(f"Error inesperado para {ip}: {e}")

        return {}