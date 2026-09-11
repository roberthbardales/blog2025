from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import ListView

from .models import Notification
from .services import marcar_todas_leidas


class NotificacionesListView(LoginRequiredMixin, ListView):
    model = Notification
    template_name = 'notificaciones/lista.html'
    context_object_name = 'notificaciones'
    paginate_by = 30
    login_url = reverse_lazy('users_app:user-login')

    def get_queryset(self):
        return Notification.objects.filter(
            recipient=self.request.user
        ).select_related('actor')

    def get(self, request, *args, **kwargs):
        response = super().get(request, *args, **kwargs)
        marcar_todas_leidas(request.user)
        return response


class MarcarLeidasView(LoginRequiredMixin, View):
    login_url = reverse_lazy('users_app:user-login')

    def post(self, request, *args, **kwargs):
        marcar_todas_leidas(request.user)
        return JsonResponse({'ok': True})