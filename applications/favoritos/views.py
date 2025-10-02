
from django.urls import reverse_lazy,reverse

from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from django.shortcuts import render

# from django.contrib.auth.mixins import LoginRequiredMixin

from django.views.generic import(
    ListView,
    View,
    DeleteView,
    CreateView,
    UpdateView,

)
from .models import Favorites, Entry,FavoriteGroup

from applications.entrada.models import Entry
#
from applications.users.mixins import (
    AdministradorPermisoMixin,
    UsuarioPermisoMixin,
)

class UserPageView(ListView):

    template_name = "favoritos/perfil.html"
    context_object_name = 'entradas_user'
    login_url=reverse_lazy('users_app:user-login')

    def get_queryset(self):
        return Favorites.objects.entradas_user(self.request.user)
    # para q muestre los grupos creados
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Agregamos los grupos de favoritos del usuario
        context["contexto_grupos"] = FavoriteGroup.objects.filter(user=self.request.user)
        return context

class AddFavoritosView(UsuarioPermisoMixin,View):

    def post(self,request,*args,**kwargs):
        #recuperar el usuario
        usuario=self.request.user
        entrada= Entry.objects.get(id=self.kwargs['pk'])
        #registramos favoritos

        Favorites.objects.get_or_create(
            user=usuario,
            entry=entrada,
        )
        return HttpResponseRedirect(
            reverse(
                'favoritos_app:perfil',
            )
        )

class FavoritesDeleteView(UsuarioPermisoMixin,DeleteView):

    model = Favorites
    success_url='.'
    success_url=reverse_lazy('favoritos_app:perfil')

# groups CRUD

class MisGruposListView(UsuarioPermisoMixin,ListView):
    model = FavoriteGroup
    template_name = "favoritos/listar_grupo.html"
    context_object_name = "contexto_grupos"

    def get_queryset(self):
        # Solo los grupos del usuario autenticado
        return FavoriteGroup.objects.filter(user=self.request.user)

class GruposCRUDView(UsuarioPermisoMixin, View):
    template_name = "favoritos/listar_grupo.html"

    def get(self, request):
        # Solo lista grupos del usuario autenticado
        grupos = FavoriteGroup.objects.filter(user=request.user)
        return render(request, self.template_name, {"grupos": grupos})

    def post(self, request):
        action = request.POST.get("action")

        # Crear grupo
        if action == "create":
            name = request.POST.get("name")
            description = request.POST.get("description", "")

            if FavoriteGroup.objects.filter(user=request.user, name=name).exists():
                messages.error(request, f"Ya existe un grupo con el nombre «{name}».")
            else:
                FavoriteGroup.objects.create(
                    name=name,
                    description=description,
                    user=request.user
                )
                messages.success(request, f"Grupo «{name}» creado con éxito.")

        # Editar grupo
        # elif action == "update":
        #     grupo_id = request.POST.get("grupo_id")
        #     grupo = FavoriteGroup.objects.get(id=grupo_id, user=request.user)
        #     new_name = request.POST.get("name")
        #     new_description = request.POST.get("description", "")

        #     # Validar duplicados al editar
        #     if FavoriteGroup.objects.filter(user=request.user, name=new_name).exclude(id=grupo.id).exists():
        #         messages.error(request, f"Ya tienes otro grupo llamado «{new_name}».")
        #     else:
        #         grupo.name = new_name
        #         grupo.description = new_description
        #         grupo.save()
        #         messages.success(request, f"Grupo «{new_name}» actualizado con éxito.")

        # Eliminar grupo
        elif action == "delete":
            grupo_id = request.POST.get("grupo_id")
            grupo = FavoriteGroup.objects.get(id=grupo_id, user=request.user)
            grupo.delete()
            messages.success(request, f"Grupo «{grupo.name}» eliminado con éxito.")

        return redirect("favoritos_app:grupos_crud")

class EditarGrupoView(UsuarioPermisoMixin, UpdateView):
    model = FavoriteGroup
    template_name = "favoritos/editar_grupo.html"
    fields = ["name", "description"]  # Django genera el form automáticamente
    success_url = reverse_lazy("favoritos_app:grupos_crud")

    def get_queryset(self):
        # Asegura que solo pueda editar sus propios grupos
        return FavoriteGroup.objects.filter(user=self.request.user)

    def form_valid(self, form):
        new_name = form.cleaned_data.get("name")
        # Validar duplicados antes de guardar
        if FavoriteGroup.objects.filter(
            user=self.request.user,
            name=new_name
        ).exclude(id=form.instance.id).exists():
            messages.error(self.request, f"Ya tienes otro grupo llamado «{new_name}».")
            return self.form_invalid(form)

        messages.success(self.request, f"Grupo «{new_name}» actualizado con éxito.")
        return super().form_valid(form)


class FavoritosByGrupoListView(UsuarioPermisoMixin, ListView):
    model = Favorites
    template_name = "favoritos/lista_de_grupos.html"
    context_object_name = "favoritos_grupo"
    paginate_by = 9

    def get_queryset(self):
        grupo_id = self.kwargs.get("pk")

        resultado= Favorites.objects.filter(
            user=self.request.user,
            group__id=grupo_id
        )
        # print("/*/*/*/*/*")
        # print(resultado)
        return resultado


class PruebaListView(ListView):
    model = FavoriteGroup
    template_name = "favoritos/prueba.html"
    context_object_name = "contexto_prueba"

    def get_queryset(self):
        return FavoriteGroup.objects.filter(
            user=self.request.user,
        )


"""
from applications.favoritos.models import *
Favorites.objects.
"""
