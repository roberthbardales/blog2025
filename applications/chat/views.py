# applications/chat/views.py CORREGIDO
from django.shortcuts import get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, TemplateView
from django.http import JsonResponse
from django.utils import timezone
from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.dispatch import receiver

from applications.users.models import User
from .models import Message, UserStatus

from datetime import timedelta


class ChatHomeView(LoginRequiredMixin, ListView):
    model = User
    template_name = 'chat/home.html'
    context_object_name = 'users'
    login_url = '/login/'

    def get_queryset(self):
        online_threshold = timezone.now() - timedelta(seconds=120)

        users = User.objects.exclude(id=self.request.user.id)
        status_map = {s.user_id: s.last_seen for s in UserStatus.objects.all()}

        for user in users:
            last_seen = status_map.get(user.id)
            user.is_online = last_seen and last_seen > online_threshold

        return users

    def render_to_response(self, context, **response_kwargs):
        if self.request.GET.get('json') == '1':
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

        messages = Message.objects.filter(
            sender__in=[self.request.user, other_user],
            recipient__in=[self.request.user, other_user]
        ).order_by('created')

        # ⚠️ CORREGIDO: Crear lista de diccionarios correctamente
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


# Signals para estado online/offline
@receiver(user_logged_in)
def set_user_online(sender, user, request, **kwargs):
    status, created = UserStatus.objects.get_or_create(user=user)
    status.is_online = True
    status.last_seen = timezone.now()
    status.save()

@receiver(user_logged_out)
def set_user_offline(sender, user, request, **kwargs):
    try:
        status = UserStatus.objects.get(user=user)
        status.is_online = False
        status.last_seen = timezone.now()
        status.save()
    except UserStatus.DoesNotExist:
        pass

from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.http import JsonResponse

@csrf_exempt
def ping(request):
    if request.user.is_authenticated:
        status, _ = UserStatus.objects.get_or_create(user=request.user)
        status.last_seen = timezone.now()
        status.save()
        return JsonResponse({"ok": True})
    return JsonResponse({"ok": False})
