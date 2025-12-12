from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib import messages
from django.http import JsonResponse

from .models import Nota
from .forms import NotaForm


class NotaListView(LoginRequiredMixin, ListView):
    """Lista todas las notas del usuario actual"""
    model = Nota
    template_name = 'notas/lista_notas.html'
    context_object_name = 'notas'
    login_url = reverse_lazy('users_app:user-login')

    def get_queryset(self):
        # Solo mostrar las notas del usuario actual
        return Nota.objects.filter(usuario=self.request.user)


class NotaDetailView(LoginRequiredMixin, DetailView):
    """Muestra el detalle de una nota"""
    model = Nota
    template_name = 'notas/detalle_nota.html'
    context_object_name = 'nota'
    login_url = reverse_lazy('users_app:user-login')

    def get_queryset(self):
        # Solo permitir ver las notas del usuario actual
        return Nota.objects.filter(usuario=self.request.user)


class NotaCreateView(LoginRequiredMixin, CreateView):
    """Crea una nueva nota"""
    model = Nota
    form_class = NotaForm
    template_name = 'notas/crear_nota.html'
    success_url = reverse_lazy('notas_app:lista-notas')
    login_url = reverse_lazy('users_app:user-login')

    def form_valid(self, form):
        # Asignar el usuario actual a la nota
        form.instance.usuario = self.request.user
        messages.success(self.request, '¡Nota creada exitosamente!')
        return super().form_valid(form)


class NotaUpdateView(LoginRequiredMixin, UpdateView):
    """Edita una nota existente"""
    model = Nota
    form_class = NotaForm
    template_name = 'notas/editar_nota.html'
    success_url = reverse_lazy('notas_app:lista-notas')
    login_url = reverse_lazy('users_app:user-login')

    def get_queryset(self):
        # Solo permitir editar las notas del usuario actual
        return Nota.objects.filter(usuario=self.request.user)

    def form_valid(self, form):
        messages.success(self.request, '¡Nota actualizada exitosamente!')
        return super().form_valid(form)


class NotaDeleteView(LoginRequiredMixin, DeleteView):
    """Elimina una nota"""
    model = Nota
    template_name = 'notas/eliminar_nota.html'
    success_url = reverse_lazy('notas_app:lista-notas')
    context_object_name = 'nota'
    login_url = reverse_lazy('users_app:user-login')

    def get_queryset(self):
        # Solo permitir eliminar las notas del usuario actual
        return Nota.objects.filter(usuario=self.request.user)

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, '¡Nota eliminada exitosamente!')
        return super().delete(request, *args, **kwargs)