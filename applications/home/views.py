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


from django.shortcuts import render
from django.db.models import Count
from datetime import timedelta
from django.utils import timezone

from .models import VisitorLog, IPLocation
from applications.users.mixins import AdministradorPermisoMixin  # Ajusta la ruta según tu estructura
from django.views.generic import TemplateView


#
from django.views import View
from django.http import JsonResponse
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
import os
from datetime import datetime
import json
#
#clima
import requests

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

#
# views.py


class VisitorLogsView(AdministradorPermisoMixin, TemplateView):
    """
    Vista para ver los logs de visitantes
    Solo accesible por ADMINISTRADORES
    """
    template_name = 'home/visitor_logs.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Obtener todas las visitas (últimas 200)
        logs = VisitorLog.objects.select_related('ip_location').all()[:50]

        # Estadísticas
        total_visits = VisitorLog.objects.count()
        unique_ips = IPLocation.objects.count()

        # Visitas de las últimas 24 horas
        last_24h = timezone.now() - timedelta(hours=24)
        visits_24h = VisitorLog.objects.filter(timestamp__gte=last_24h).count()

        # Visitas de la última semana
        last_week = timezone.now() - timedelta(days=7)
        visits_week = VisitorLog.objects.filter(timestamp__gte=last_week).count()

        # Top 10 países
        top_countries = (
            IPLocation.objects
            .values('country')
            .annotate(count=Count('visits'))
            .order_by('-count')[:10]
        )

        # Top 10 ciudades
        top_cities = (
            IPLocation.objects
            .exclude(city='')
            .values('city', 'country')
            .annotate(count=Count('visits'))
            .order_by('-count')[:10]
        )

        context.update({
            'logs': logs,
            'total_visits': total_visits,
            'unique_ips': unique_ips,
            'visits_24h': visits_24h,
            'visits_week': visits_week,
            'top_countries': top_countries,
            'top_cities': top_cities,
        })

        return context

