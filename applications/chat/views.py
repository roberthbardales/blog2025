# applications/chat/views.py OPTIMIZADO
from django.shortcuts import get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, TemplateView
from django.http import JsonResponse
from django.utils import timezone
from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.dispatch import receiver
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from applications.users.models import User
from .models import Message, UserStatus

from datetime import timedelta


class ChatHomeView(LoginRequiredMixin, ListView):
    model = User
    template_name = 'chat/home.html'
    context_object_name = 'users'
    login_url = '/login/'

    def get_queryset(self):
        # Umbral: usuario online si hizo ping en los últimos 5 segundos
        online_threshold = timezone.now() - timedelta(seconds=5)

        users = User.objects.exclude(id=self.request.user.id)

        # Obtener todos los estados de una vez (más eficiente)
        status_dict = {
            s.user_id: s.last_seen
            for s in UserStatus.objects.select_related('user').all()
        }

        # Asignar estado online a cada usuario
        for user in users:
            last_seen = status_dict.get(user.id)
            user.is_online = last_seen and last_seen > online_threshold

        return users

    def render_to_response(self, context, **response_kwargs):
        # Si es petición AJAX, devolver JSON
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest' or self.request.GET.get('json') == '1':
            data = {user.id: user.is_online for user in context['users']}
            return JsonResponse(data)
        return super().render_to_response(context, **response_kwargs)


class ChatRoomView(LoginRequiredMixin, TemplateView):
    template_name = 'chat/room.html'
    login_url = '/login/'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_id = self.kwargs.get('user_id')
        other_user = get_object_or_404(User, id=user_id)

        # Verificar estado online del otro usuario
        online_threshold = timezone.now() - timedelta(seconds=5)
        try:
            status = UserStatus.objects.get(user=other_user)
            other_user.is_online = status.last_seen and status.last_seen > online_threshold
        except UserStatus.DoesNotExist:
            other_user.is_online = False

        # Obtener mensajes del chat
        messages = Message.objects.filter(
            sender__in=[self.request.user, other_user],
            recipient__in=[self.request.user, other_user]
        ).select_related('sender', 'recipient').order_by('created')

        messages_with_time = []
        for msg in messages:
            messages_with_time.append({
                'sender': msg.sender,
                'content': msg.content,
                'formatted_time': msg.created.strftime('%H:%M')
            })

        context['other_user'] = other_user
        context['messages'] = messages_with_time
        return context


# === ENDPOINTS PARA ESTADO ONLINE/OFFLINE ===

@csrf_exempt
@require_http_methods(["POST"])
def ping(request):
    """
    Endpoint que el frontend llama cada 2 segundos para mantener al usuario 'online'
    """
    if request.user.is_authenticated:
        status, created = UserStatus.objects.get_or_create(user=request.user)
        status.last_seen = timezone.now()
        status.is_online = True
        status.save(update_fields=['last_seen', 'is_online'])
        return JsonResponse({"ok": True, "timestamp": status.last_seen.isoformat()})
    return JsonResponse({"ok": False, "error": "Not authenticated"}, status=401)


@login_required
@require_http_methods(["GET"])
def user_status(request, user_id):
    """
    Endpoint para verificar si un usuario específico está online
    """
    try:
        user = User.objects.get(id=user_id)
        online_threshold = timezone.now() - timedelta(seconds=5)

        try:
            status = UserStatus.objects.get(user=user)
            is_online = status.last_seen and status.last_seen > online_threshold
            last_seen_iso = status.last_seen.isoformat() if status.last_seen else None
        except UserStatus.DoesNotExist:
            is_online = False
            last_seen_iso = None

        return JsonResponse({
            'is_online': is_online,
            'last_seen': last_seen_iso,
            'user_id': user_id
        })
    except User.DoesNotExist:
        return JsonResponse({'error': 'User not found'}, status=404)


@login_required
@require_http_methods(["GET"])
def bulk_user_status(request):
    """
    Endpoint para obtener el estado de múltiples usuarios de una vez (más eficiente)
    """
    user_ids = request.GET.get('user_ids', '').split(',')
    user_ids = [int(uid) for uid in user_ids if uid.isdigit()]

    if not user_ids:
        return JsonResponse({'error': 'No user IDs provided'}, status=400)

    online_threshold = timezone.now() - timedelta(seconds=5)

    # Obtener todos los estados de una vez
    statuses = UserStatus.objects.filter(user_id__in=user_ids)
    status_dict = {}

    for status in statuses:
        is_online = status.last_seen and status.last_seen > online_threshold
        status_dict[status.user_id] = {
            'is_online': is_online,
            'last_seen': status.last_seen.isoformat() if status.last_seen else None
        }

    # Asegurar que todos los IDs solicitados tengan una respuesta
    for uid in user_ids:
        if uid not in status_dict:
            status_dict[uid] = {'is_online': False, 'last_seen': None}

    return JsonResponse(status_dict)


# === SIGNALS PARA LOGIN/LOGOUT ===

@receiver(user_logged_in)
def set_user_online(sender, user, request, **kwargs):
    """Marcar usuario como online cuando hace login"""
    status, created = UserStatus.objects.get_or_create(user=user)
    status.is_online = True
    status.last_seen = timezone.now()
    status.save()


@receiver(user_logged_out)
def set_user_offline(sender, user, request, **kwargs):
    """Marcar usuario como offline cuando hace logout"""
    try:
        status = UserStatus.objects.get(user=user)
        status.is_online = False
        status.last_seen = timezone.now()
        status.save()
    except UserStatus.DoesNotExist:
        pass