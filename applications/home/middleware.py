# middleware.py
import requests
from .models import VisitorLog, IPLocation

PRIVATE_IPS = ('127.', '192.168.', '10.', '172.16.', '::1', 'localhost')

class VisitorLogMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path != '/':
            return self.get_response(request)

        ip = self.get_client_ip(request)

        ip_location, created = IPLocation.objects.get_or_create(
            ip_address=ip,
            defaults={
                'country': '', 'city': '',
                'region': '', 'latitude': None, 'longitude': None
            }
        )

        # ⭐ Si no tiene coordenadas (nunca se geolocalizo bien), volver a intentar
        if ip_location.latitude is None or ip_location.longitude is None:
            location_data = self.get_location(ip)
            if location_data:
                ip_location.country  = location_data['country']
                ip_location.city     = location_data['city']
                ip_location.region   = location_data['region']
                ip_location.latitude = location_data['latitude']
                ip_location.longitude= location_data['longitude']
                ip_location.save()

        VisitorLog.objects.create(
            ip_location=ip_location,
            user_agent=request.META.get('HTTP_USER_AGENT', '')[:500],
            path=request.path[:500]
        )

        return self.get_response(request)

    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0].strip()
        return request.META.get('REMOTE_ADDR')

    def get_location(self, ip):
        """Consulta ip-api.com y devuelve dict con coordenadas."""
        if any(ip.startswith(p) for p in PRIVATE_IPS):
            return {
                'country': 'Local', 'city': 'Localhost',
                'region': 'Development', 'latitude': 0.0, 'longitude': 0.0
            }

        try:
            resp = requests.get(
                f'http://ip-api.com/json/{ip}',
                params={'fields': 'status,message,country,city,regionName,lat,lon'},
                timeout=5
            )
            data = resp.json()

            if data.get('status') == 'success':
                return {
                    'country':   data.get('country', ''),
                    'city':      data.get('city', ''),
                    'region':    data.get('regionName', ''),  # ⭐ regionName, no region
                    'latitude':  data.get('lat'),             # ⭐ lat, no latitude
                    'longitude': data.get('lon'),             # ⭐ lon, no longitude
                }
            else:
                print(f"[GEO] Fallo para {ip}: {data.get('message')}")

        except requests.RequestException as e:
            print(f"[GEO] Error de red para {ip}: {e}")

        return {}