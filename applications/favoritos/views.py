
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
    login_url = reverse_lazy('users_app:user-login')
    paginate_by = 6

    def get_queryset(self):
        usuario = self.request.user
        queryset = Favorites.objects.none()

        if usuario.is_authenticated:
            queryset = Favorites.objects.entradas_user(usuario)

            # --- Filtro por grupo ---
            grupo = self.request.GET.get("grupo", "").strip()
            if grupo:
                queryset = queryset.filter(group__name=grupo)

            # --- Nuevo: orden dinámico por fecha, grupo o categoría ---
            orden = self.request.GET.get("orden", "fecha")

            if orden == "fecha":
                queryset = queryset.order_by('-created')
            elif orden == "grupo":
                queryset = queryset.order_by('group__name')
            elif orden == "categoria":
                queryset = queryset.order_by('entry__category__name')
            else:
                queryset = queryset.order_by('-created')  # por defecto

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["contexto_grupos"] = FavoriteGroup.objects.filter(user=self.request.user)
        # --- Nuevo: mantener qué orden está seleccionado en el template ---
        context["orden_seleccionado"] = self.request.GET.get("orden", "fecha")
        return context

class CambiarGrupoView(UsuarioPermisoMixin, View):
    """Cambia el grupo de un favorito usando botones y recargando la página"""

    def get(self, request, pk, *args, **kwargs):
        favorito = get_object_or_404(Favorites, pk=pk, user=request.user)
        group_id = request.GET.get("group_id", "")

        if group_id:
            grupo = get_object_or_404(FavoriteGroup, id=group_id, user=request.user)
            favorito.group = grupo
        else:
            favorito.group = None  # Sin grupo

        favorito.save()
        return redirect("favoritos_app:perfil")  # vuelve al perfil

class AddFavoritosView(UsuarioPermisoMixin, View):

    def post(self, request, *args, **kwargs):
        usuario = self.request.user
        entrada = Entry.objects.get(id=self.kwargs['pk'])

        # Obtener o crear el grupo General
        grupo_general, _ = FavoriteGroup.objects.get_or_create(
            user=usuario,
            name="General"
        )

        # Registrar favorito evitando duplicados
        favorito, creado = Favorites.objects.get_or_create(
            user=usuario,
            entry=entrada,
            defaults={'group': grupo_general}
        )


        return redirect(reverse('favoritos_app:perfil'))

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


class FavoritoListView(ListView):
    model = Favorites
    template_name = 'favoritos/lista.html'
    context_object_name = 'favoritos'

    def get_queryset(self):
        queryset = super().get_queryset()
        orden = self.request.GET.get('orden', 'fecha')

        if orden == 'fecha':
            queryset = queryset.order_by('-fecha')
        elif orden == 'grupo':
            queryset = queryset.order_by('grupo__nombre')
        elif orden == 'categoria':
            queryset = queryset.order_by('categoria__nombre')

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['orden_seleccionado'] = self.request.GET.get('orden', 'fecha')
        return context



"""
from applications.favoritos.models import *
Favorites.objects.
"""
