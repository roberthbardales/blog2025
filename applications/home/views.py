import datetime
#
from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy, reverse


from django.core.mail import send_mail  #envio de correos
from django.conf import settings


from django.views.generic import (
    TemplateView,
    CreateView,
)

#apps de entrada
from applications.entrada.models import Entry

from .models import Home
from .forms import SuscribersForm,ContactForm,ContactForm2


class HomePageView(TemplateView):
    template_name = "home/index.html"

    def get_context_data(self, **kwargs):
        context = super(HomePageView, self).get_context_data(**kwargs)
        #cargamos el home
        context['home']=Home.objects.latest('created')
        #contexto de portada
        context['portada']=Entry.objects.entrada_en_portada()
        #contexto para los articulos de home
        context['entradas_home']=Entry.objects.entradas_en_home()
        #entradas recientes
        context['entradas_recientes']=Entry.objects.entradas_recientes()
        #enviamos formulario de suscripcion
        context['form']=SuscribersForm

        return context


# class SuscriberCreateView(CreateView):
#     form_class=SuscribersForm
#     success_url= '.'


class AboutMe(TemplateView):
    template_name = "home/about_me.html"


class SuscriberCreateView(CreateView):
    form_class = SuscribersForm
    success_url = "."  # puedes cambiarlo a otra URL

    def form_valid(self, form):
        # Guardar el suscriptor en la BD
        self.object = form.save()

        # Obtener el correo ingresado
        correo = form.cleaned_data['email']
        link = self.request.build_absolute_uri('/register/')
        # Enviar correo de confirmación
        send_mail(
            "Registrate en el siguiente link ✅",
            f"Ingresa los datos requeridos.\n\n"
            f"Completa tu registro aquí: {link}",
            settings.DEFAULT_FROM_EMAIL,   # tu correo Gmail configurado en settings
            [correo],                      # destinatario
            fail_silently=False,
        )

        return super().form_valid(form)


class ContactCreateView(CreateView):
    form_class=ContactForm
    success_url= '.'


class ContactCreateView2(CreateView):
    form_class = ContactForm2
    success_url = '.'

    def form_valid(self, form):
        self.object = form.save()

        nombre = form.cleaned_data['full_name']
        correo = form.cleaned_data['email']
        mensaje = form.cleaned_data['messagge']

        send_mail(
            f"Nuevo mensaje de {nombre}",
            f"De: {nombre} <{correo}>\n\nMensaje:\n{mensaje}",
            settings.DEFAULT_FROM_EMAIL,
            ["roberthbardales@gmail.com"],
            fail_silently=False,
        )

        return super().form_valid(form)  # en lugar de redirect()

# como en los  viejos tiempos en la u


from django.views import View
from django.http import JsonResponse
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
import os
from datetime import datetime
import json


@method_decorator(csrf_exempt, name='dispatch')
class VisitaView(View):
    """
    Vista para capturar datos (POST) y visualizar registros (GET)
    """
    archivo_path = 'visitas_pc.txt'

    def get(self, request):
        """Muestra todos los registros guardados"""
        registros = []

        # Leer el archivo si existe
        if os.path.exists(self.archivo_path):
            try:
                with open(self.archivo_path, 'r', encoding='utf-8') as archivo:
                    contenido = archivo.read()
                    # Dividir por separadores
                    registros_raw = contenido.split('='*80)
                    # Limpiar y filtrar registros vacíos
                    registros = [r.strip() for r in registros_raw if r.strip()]
            except Exception as e:
                registros = [f"Error al leer archivo: {str(e)}"]
        else:
            registros = ["No hay registros aún."]

        return render(request, 'home/visita.html', {
            'registros': registros,
            'total': len(registros)
        })

    def post(self, request):
        """Recibe y guarda los datos capturados por JavaScript"""
        try:
            # Datos enviados desde el navegador
            datos_cliente = json.loads(request.body)

            # Combinar con datos del servidor
            datos_completos = {
                'servidor': self._obtener_datos_servidor(request),
                'cliente': datos_cliente
            }

            # Formatear y guardar
            registro = self._formatear_registro(datos_completos)
            self._guardar_en_archivo(registro)

            return JsonResponse({
                'status': 'success',
                'mensaje': 'Datos registrados correctamente'
            })
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'mensaje': f'Error: {str(e)}'
            }, status=500)

    def _obtener_datos_servidor(self, request):
        """Datos que Django puede obtener del servidor"""
        return {
            'ip': self._obtener_ip_cliente(request),
            'user_agent': request.META.get('HTTP_USER_AGENT', 'Desconocido'),
            'idioma': request.META.get('HTTP_ACCEPT_LANGUAGE', 'Desconocido'),
            'encoding': request.META.get('HTTP_ACCEPT_ENCODING', 'Desconocido'),
            'referer': request.META.get('HTTP_REFERER', 'Directo'),
            'metodo': request.method,
            'ruta': request.path,
            'host': request.META.get('HTTP_HOST', 'Desconocido'),
            'protocolo': request.scheme,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        }

    def _obtener_ip_cliente(self, request):
        """Obtiene la IP real del cliente"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR', 'Desconocida')
        return ip

    def _formatear_registro(self, datos):
        """Formatea los datos en un registro legible"""
        s = datos['servidor']
        c = datos['cliente']

        # Generar ID único basado en timestamp
        timestamp_id = datetime.now().strftime('%Y%m%d%H%M%S%f')[:-3]

        return f"""
{'='*80}
REGISTRO #{timestamp_id}
{'='*80}

--- FECHA Y HORA ---
Timestamp: {s['timestamp']}

--- DATOS DE RED ---
IP: {s['ip']}
Host: {s['host']}
Protocolo: {s['protocolo'].upper()}

--- SISTEMA OPERATIVO ---
Plataforma: {c.get('plataforma', 'N/A')}
User Agent: {s['user_agent']}

--- NAVEGADOR ---
Nombre: {c.get('navegador', {}).get('nombre', 'N/A')}
Versión: {c.get('navegador', {}).get('version', 'N/A')}
Motor: {c.get('navegador', {}).get('motor', 'N/A')}
Cookies Habilitadas: {c.get('cookies_habilitadas', 'N/A')}
Do Not Track: {c.get('do_not_track', 'N/A')}

--- PANTALLA ---
Resolución: {c.get('pantalla', {}).get('resolucion', 'N/A')}
Resolución Disponible: {c.get('pantalla', {}).get('resolucion_disponible', 'N/A')}
Profundidad de Color: {c.get('pantalla', {}).get('profundidad_color', 'N/A')} bits
Orientación: {c.get('pantalla', {}).get('orientacion', 'N/A')}
Relación de Píxeles: {c.get('pantalla', {}).get('pixel_ratio', 'N/A')}

--- VENTANA DEL NAVEGADOR ---
Tamaño de Ventana: {c.get('ventana', {}).get('tamanio', 'N/A')}
Viewport: {c.get('ventana', {}).get('viewport', 'N/A')}

--- HARDWARE ---
Núcleos de CPU: {c.get('hardware', {}).get('cpu_nucleos', 'N/A')}
Memoria RAM: {c.get('hardware', {}).get('memoria', 'N/A')}
GPU: {c.get('hardware', {}).get('gpu', 'N/A')}
Touchscreen: {c.get('hardware', {}).get('touchscreen', 'N/A')}
Conexión: {c.get('hardware', {}).get('tipo_conexion', 'N/A')}

--- UBICACIÓN Y ZONA HORARIA ---
Zona Horaria: {c.get('zona_horaria', 'N/A')}
Idioma del Sistema: {c.get('idioma_sistema', 'N/A')}
Idiomas Preferidos: {s['idioma']}

--- CARACTERÍSTICAS DEL NAVEGADOR ---
JavaScript: Habilitado
Local Storage: {c.get('almacenamiento', {}).get('localStorage', 'N/A')}
Session Storage: {c.get('almacenamiento', {}).get('sessionStorage', 'N/A')}
IndexedDB: {c.get('almacenamiento', {}).get('indexedDB', 'N/A')}

--- BATERÍA (si está disponible) ---
Nivel de Batería: {c.get('bateria', {}).get('nivel', 'N/A')}
Cargando: {c.get('bateria', {}).get('cargando', 'N/A')}

{'='*80}

"""

    def _guardar_en_archivo(self, registro):
        """Guarda el registro en el archivo"""
        with open(self.archivo_path, 'a', encoding='utf-8') as archivo:
            archivo.write(registro)