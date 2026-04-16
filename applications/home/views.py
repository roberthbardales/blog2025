import json
import datetime

from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.mail import send_mail
from django.db.models import Count, Q
from django.http import JsonResponse
from django.shortcuts import render
from django.urls import reverse_lazy, reverse
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import TemplateView, CreateView
from datetime import timedelta

from .models import Home, VisitorLog, IPLocation
from .forms import SuscribersForm, ContactForm, ContactForm2
from applications.entrada.models import Entry
from applications.users.mixins import AdministradorPermisoMixin


class HomePageView(TemplateView):
    template_name = "home/index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['home'] = Home.objects.latest('created')
        context['portada'] = Entry.objects.entrada_en_portada()
        context['entradas_home'] = Entry.objects.entradas_en_home()
        context['entradas_recientes'] = Entry.objects.entradas_recientes()
        context['form'] = SuscribersForm
        return context


class AboutMe(TemplateView):
    template_name = "home/about_me.html"


class SuscriberCreateView(CreateView):
    form_class = SuscribersForm
    success_url = "."

    def form_valid(self, form):
        self.object = form.save()
        correo = form.cleaned_data['email']
        link = self.request.build_absolute_uri('/register/')
        send_mail(
            "Registrate en el siguiente link ✅",
            f"Ingresa los datos requeridos.\n\nCompleta tu registro aquí: {link}",
            settings.DEFAULT_FROM_EMAIL,
            [correo],
            fail_silently=False,
        )
        return super().form_valid(form)


class ContactCreateView(CreateView):
    form_class = ContactForm
    success_url = '.'


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
        return super().form_valid(form)


class VisitorLogsView(AdministradorPermisoMixin, TemplateView):
    template_name = 'home/visitor_logs.html'

    def get_peru_filter(self):
        """Filtro reutilizable para capturar 'peru' y 'perú'."""
        countries = ['peru', 'perú']
        query = Q()
        for c in countries:
            query |= Q(ip_location__country__iexact=c)
        return query

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        peru_filter = self.get_peru_filter()
        peru_logs = VisitorLog.objects.select_related('ip_location').filter(peru_filter)

        now = timezone.now()

        # Top países y ciudades usan un filtro equivalente sobre IPLocation
        ip_peru_filter = Q()
        for c in ['peru', 'perú']:
            ip_peru_filter |= Q(country__iexact=c)

        top_countries = (
            IPLocation.objects
            .filter(ip_peru_filter)
            .values('country')
            .annotate(count=Count('visits'))
            .order_by('-count')[:10]
        )

        top_cities = (
            IPLocation.objects
            .filter(ip_peru_filter)
            .exclude(city='')
            .values('city')
            .annotate(count=Count('visits'))
            .order_by('-count')[:10]
        )

        context.update({
            'logs': peru_logs[:200],
            'total_visits': peru_logs.count(),
            'unique_ips': IPLocation.objects.filter(ip_peru_filter).count(),
            'visits_24h': peru_logs.filter(timestamp__gte=now - timedelta(hours=24)).count(),
            'visits_week': peru_logs.filter(timestamp__gte=now - timedelta(days=7)).count(),
            'top_countries': top_countries,
            'top_cities': top_cities,
        })

        return context


@method_decorator(csrf_exempt, name='dispatch')
class VisitorCreateView(View):
    """Endpoint público para registrar visitas vía fetch/AJAX."""

    def post(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'JSON inválido'}, status=400)

        ip = request.META.get('REMOTE_ADDR')
        # VisitorLog.objects.create(ip=ip, ...)

        return JsonResponse({'ok': True})


# home/views.py — agrega esta vista
class PortafolioView(TemplateView):
    template_name = "home/portafolio.html"


class InicioView(TemplateView):
    template_name = "home/inicio2.html"