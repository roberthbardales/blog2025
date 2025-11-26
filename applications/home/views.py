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

import json
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.shortcuts import render
from django.http import JsonResponse
from datetime import datetime

# Lista global para almacenar visitas en memoria
VISITAS = []

@method_decorator(csrf_exempt, name='dispatch')
class VisitaView(View):

    def get(self, request, *args, **kwargs):
        return self.registrar_visita(request)

    def post(self, request, *args, **kwargs):
        return self.registrar_visita(request)

    def registrar_visita(self, request):
        visited_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ip = request.META.get("REMOTE_ADDR", "Desconocida")

        # Leer datos enviados por JS
        if request.method == "POST":
            try:
                data = json.loads(request.body)
            except json.JSONDecodeError:
                data = {}
        else:
            data = {}

        # Datos del visitante
        visita = {
            "Fecha": visited_at,
            "IP": ip,
            "UserAgent": data.get("user_agent", request.META.get("HTTP_USER_AGENT", "")),
            "Language": data.get("language", request.META.get("HTTP_ACCEPT_LANGUAGE", "")),
            "Platform": data.get("platform", ""),
            "Screen": f"{data.get('screen_width','')}x{data.get('screen_height','')}",
            "Inner": f"{data.get('inner_width','')}x{data.get('inner_height','')}",
            "MemoryGB": data.get("device_memory", ""),
            "CPUcores": data.get("cpu_cores", ""),
            "Mobile": data.get("is_mobile", ""),
            "TouchPoints": data.get("touch_points", ""),
            "Online": data.get("online", ""),
            "URL": data.get("url", request.build_absolute_uri()),
            "Referer": data.get("referer", request.META.get("HTTP_REFERER", ""))
        }

        # Guardar en lista global
        VISITAS.append(visita)

        if request.method == "POST":
            return JsonResponse({"status": "ok"})

        # Mostrar visitas en el template
        return render(request, "home/visita.html", {"visitas": VISITAS})
