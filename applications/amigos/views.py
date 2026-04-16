from datetime import datetime, timedelta
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, View
from applications.entrada.models import Entry, Category

from .models import Friendship
from applications.entrada.models import Entry


User = get_user_model()


class ListaAmigosView(LoginRequiredMixin, ListView):
    template_name = 'amigos/lista_amigos.html'
    context_object_name = 'amigos'
    login_url = reverse_lazy('users_app:user-login')

    def get_queryset(self):
        user = self.request.user
        friendships = Friendship.objects.get_friends(user).select_related('sender', 'receiver')
        # Devuelve los User objects (el otro lado de la relación)
        result = []
        for f in friendships:
            friend = f.receiver if f.sender == user else f.sender
            result.append({'friendship': f, 'user': friend})
        return result

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['solicitudes_recibidas'] = Friendship.objects.get_pending_received(
            self.request.user
        ).select_related('sender', 'receiver')
        context['solicitudes_enviadas'] = Friendship.objects.get_pending_sent(
            self.request.user
        ).select_related('sender', 'receiver')
        return context



class BuscarUsuariosView(LoginRequiredMixin, ListView):
    template_name = 'amigos/buscar_usuarios.html'
    context_object_name = 'usuarios'
    login_url = reverse_lazy('users_app:user-login')
    paginate_by = 12

    def get_queryset(self):
        kword = self.request.GET.get('kword', '').strip()
        if not kword:
            return []

        user = self.request.user
        usuarios = User.objects.filter(
            Q(email__icontains=kword) |
            Q(full_name__icontains=kword)
        ).exclude(pk=user.pk)

        friendships = Friendship.objects.filter(
            Q(sender=user, receiver__in=usuarios) |
            Q(sender__in=usuarios, receiver=user)
        ).select_related('sender', 'receiver')

        friendship_map = {}
        for friendship in friendships:
            other_user = friendship.receiver if friendship.sender_id == user.id else friendship.sender
            friendship_map[other_user.id] = friendship

        result = []
        for u in usuarios:
            f = friendship_map.get(u.id)
            result.append({
                'user'      : u,
                'friendship': f,
                'status'    : f.status if f else None,
                'soy_sender': f.sender == user if f else False,
            })
        return result

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['kword'] = self.request.GET.get('kword', '')
        return context



class EnviarSolicitudView(LoginRequiredMixin, View):
    login_url = reverse_lazy('users_app:user-login')

    def post(self, request, pk, *args, **kwargs):
        receiver = get_object_or_404(User, pk=pk)

        if receiver == request.user:
            messages.error(request, 'No puedes enviarte una solicitud a ti mismo.')
            return redirect('amigos_app:buscar')

        # Verificar si ya existe alguna relación
        existente = Friendship.objects.get_friendship(request.user, receiver)
        if existente:
            messages.warning(request, 'Ya existe una relación con este usuario.')
        else:
            Friendship.objects.create(sender=request.user, receiver=receiver)
            messages.success(request, f'Solicitud enviada a {receiver.full_name}.')

        return redirect('amigos_app:buscar')


class AceptarSolicitudView(LoginRequiredMixin, View):
    login_url = reverse_lazy('users_app:user-login')

    def post(self, request, pk, *args, **kwargs):
        solicitud = get_object_or_404(
            Friendship, pk=pk, receiver=request.user, status='pending'
        )
        solicitud.status = Friendship.STATUS_ACCEPTED
        solicitud.save()
        messages.success(request, f'Ahora eres amigo de {solicitud.sender.full_name}.')
        return redirect('amigos_app:lista')


class RechazarSolicitudView(LoginRequiredMixin, View):
    login_url = reverse_lazy('users_app:user-login')

    def post(self, request, pk, *args, **kwargs):
        solicitud = get_object_or_404(
            Friendship, pk=pk, receiver=request.user, status='pending'
        )
        solicitud.status = Friendship.STATUS_REJECTED
        solicitud.save()
        messages.warning(request, f'Solicitud de {solicitud.sender.full_name} rechazada.')
        return redirect('amigos_app:lista')


class CancelarSolicitudView(LoginRequiredMixin, View):
    """El sender cancela su propia solicitud pendiente"""
    login_url = reverse_lazy('users_app:user-login')

    def post(self, request, pk, *args, **kwargs):
        solicitud = get_object_or_404(
            Friendship, pk=pk, sender=request.user, status='pending'
        )
        solicitud.delete()
        messages.info(request, 'Solicitud cancelada.')
        return redirect('amigos_app:lista')


class EliminarAmigoView(LoginRequiredMixin, View):
    login_url = reverse_lazy('users_app:user-login')

    def post(self, request, pk, *args, **kwargs):
        friend = get_object_or_404(User, pk=pk)
        friendship = Friendship.objects.get_friendship(request.user, friend)
        if friendship and friendship.status == 'accepted':
            friendship.delete()
            messages.info(request, f'{friend.full_name} eliminado de tus amigos.')
        return redirect('amigos_app:lista')


class BloquearUsuarioView(LoginRequiredMixin, View):
    login_url = reverse_lazy('users_app:user-login')

    def post(self, request, pk, *args, **kwargs):
        target = get_object_or_404(User, pk=pk)
        friendship = Friendship.objects.get_friendship(request.user, target)

        if friendship:
            friendship.status = Friendship.STATUS_BLOCKED
            friendship.sender = request.user   # quien bloquea es el sender
            friendship.receiver = target
            friendship.save()
        else:
            Friendship.objects.create(
                sender=request.user,
                receiver=target,
                status=Friendship.STATUS_BLOCKED
            )
        messages.warning(request, f'{target.full_name} ha sido bloqueado.')
        return redirect('amigos_app:lista')




class PerfilRedView(LoginRequiredMixin, ListView):
    template_name = 'amigos/perfil_red.html'
    context_object_name = 'mis_posts'
    paginate_by = 10
    login_url = reverse_lazy('users_app:user-login')

    def get_queryset(self):
        user = self.request.user
        queryset = Entry.objects.filter(user=user).select_related('category').order_by('-created')

        # Solo uno de los dos filtros actúa a la vez
        categoria = self.request.GET.get('categoria', '').strip()
        kword = self.request.GET.get('kword', '').strip()

        if categoria:
            queryset = queryset.filter(category__short_name=categoria)
        elif kword:
            queryset = queryset.filter(
                Q(title__icontains=kword) |
                Q(resume__icontains=kword)
            )

        return queryset



    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        context['total_amigos'] = Friendship.objects.get_friends(user).count()
        context['total_posts'] = Entry.objects.filter(user=user).count()
        context['solicitudes_pendientes'] = Friendship.objects.get_pending_received(user).count()
        context['categorias'] = Category.objects.all().order_by('name')
        context['categoria_sel'] = self.request.GET.get('categoria', '')
        context['fecha_sel'] = self.request.GET.get('fecha', '')
        return context
