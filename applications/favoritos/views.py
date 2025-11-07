
from django.urls import reverse_lazy,reverse

from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from django.shortcuts import render
from django.db.models import Q
from django.contrib.postgres.search import TrigramSimilarity

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

# --------------------------------
class EntryListView(ListView):
    model=Entry
    template_name = "entrada/lista.html"
    context_object_name ='entradas'
    paginate_by = 9

    def get_context_data(self, **kwargs):
        context = super(EntryListView, self).get_context_data(**kwargs)
        # context['categorias']=Category.objects.all().order_by('name')

        return context

    #buscador input

    def get_queryset(self):
        kword= self.request.GET.get('kword_prueba','')
        categoria= self.request.GET.get('categoria','')
        kword_general = self.request.GET.get('kword_general', '').strip()
        #consulta de busqueda
        resultado= Entry.objects.buscar_entrada_categoria(kword,categoria)

        if kword_general:

            resultado = Entry.objects.buscar_general(kword_general)
            # resultado = resultado.filter(title__icontains=kword_general)
        return resultado
# --------------------------------

class ToggleFavoritoView(View):
    def post(self, request, pk, *args, **kwargs):
        entry = get_object_or_404(Entry, pk=pk)
        favorito = Favorites.objects.filter(user=request.user, entry=entry).first()

        if favorito:
            favorito.delete()  # si ya existe, lo quita
        else:
            Favorites.objects.create(user=request.user, entry=entry)  # si no, lo agrega

        return redirect(reverse("entrada_app:entry-detail", kwargs={"slug": entry.slug}))





class UserPageView(ListView):
    template_name = "favoritos/perfil.html"
    context_object_name = 'entradas_user'
    login_url = reverse_lazy('users_app:user-login')
    paginate_by = 6

    def get_queryset(self):
        usuario = self.request.user
        queryset = Favorites.objects.none()
        kword_favorito = self.request.GET.get("kword_favorito", "")

        if kword_favorito:
            queryset = Favorites.objects.filter(
            Q(user=usuario),
            Q(entry__title__icontains=kword_favorito,) |
            Q(entry__title__trigram_similar=kword_favorito,)
        ).order_by('-created')
            # print(queryset)
            return(queryset)

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

"""
pruebas
"""
class AddFavoritosView2(UsuarioPermisoMixin, View):
    """
    Vista para agregar o quitar un favorito.
    Permite seleccionar un grupo desde un <select>.
    Si no hay grupos, crea uno llamado "General".
    Muestra mensajes de feedback al usuario.
    """

    def post(self, request, pk, *args, **kwargs):
        usuario = request.user
        entrada = get_object_or_404(Entry, pk=pk)

        # Obtener el group_id enviado desde el formulario
        kword_grupo = request.POST.get("kword_grupo")

        # Si no se seleccionó grupo o se envió "0", usar/crear "General"
        if not kword_grupo or kword_grupo == "0":
            grupo, _ = FavoriteGroup.objects.get_or_create(user=usuario, name="General")
        else:
            # Intentar obtener el grupo seleccionado por el usuario
            grupo = FavoriteGroup.objects.filter(id=kword_grupo, user=usuario).first()
            # Si por alguna razón no existe, usar "General"
            if not grupo:
                grupo, _ = FavoriteGroup.objects.get_or_create(user=usuario, name="General")

        # Revisar si el entry ya es favorito del usuario
        favorito = Favorites.objects.filter(user=usuario, entry=entrada).first()

        if favorito:
            favorito.delete()
            messages.warning(request, f'"{entrada.title}" fue eliminado de tus favoritos.')
        else:
            Favorites.objects.create(user=usuario, entry=entrada, group=grupo)
            messages.success(request, f'"{entrada.title}" fue agregado a tus favoritos en el grupo "{grupo.name}".')

        # Redirigir al detalle de la entrada
        return redirect(reverse("entrada_app:entry-detail", kwargs={"slug": entrada.slug}))
"""
fin pruebas
"""

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


# class PruebaListView(ListView):
#     model = FavoriteGroup
#     template_name = "favoritos/prueba.html"
#     context_object_name = "contexto_prueba"

#     def get_queryset(self):
#         return FavoriteGroup.objects.filter(
#             user=self.request.user,
#         )


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
