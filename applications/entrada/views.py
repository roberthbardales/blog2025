
from django.shortcuts import render
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy,reverse
from django.db.models import Q

#forms
from django.views.generic import(
    TemplateView,
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    View,
    DeleteView,
)
#
from .forms import EntradaForm
from .forms import CommentForm

#models
from .models import Entry,Category,Tag,Comment,Like

#mixin
from applications.users.mixins import (
    AdministradorPermisoMixin,
    UsuarioPermisoMixin,
)
# class BuscadorGeneralTemplateView(TemplateView):
#     template_name = "entrada/lista.html"

#     def get_context_data(self, **kwargs):
#         contexto_russell = super(BuscadorGeneralTemplateView, self).get_context_data(**kwargs)
#         #entradas recientes
#         contexto_russell['russell']=Entry.objects.buscador_general()
#         return contexto_russell

# class EntryListViewBySearch(ListView):
#     template_name = "entrada/lista.html"
#     context_object_name ='entradas'
#     paginate_by = 9

#     def get_context_data(self, **kwargs):
#         context = super(EntryListViewBySearch, self).get_context_data(**kwargs)
#         context['categorias']=Category.objects.all()

#         return context

#     def get_queryset(self):
#         kword_general= self.request.GET.get('kword_general','')
#         categoria= self.request.GET.get('categoria','')
#         #consulta de busqueda
#         resultado= Entry.objects.buscador_general(kword_general,categoria)

#         return resultado



class EntryListView(ListView):
    model=Entry
    template_name = "entrada/lista.html"
    context_object_name ='entradas'
    paginate_by = 9

    def get_context_data(self, **kwargs):
        context = super(EntryListView, self).get_context_data(**kwargs)
        context['categorias']=Category.objects.all().order_by('name')

        # context['categorias2']=Category.objects.all().order_by('-created')
        # print("//////////////////////////////////////////")
        # lista=context['categorias2']
        # for item in lista:
        #     print(f"{item.id} - {item.name}")

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

class EntryDetailView(UsuarioPermisoMixin, DetailView):
    template_name = 'entrada/detail.html'
    model = Entry
    context_object_name = 'entry'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Formulario de comentarios
        context['main_comments'] = self.object.comments.filter(parent__isnull=True).order_by('created')
        context['comment_form'] = CommentForm()
        # Usuario actual
        user = self.request.user
        entry = self.get_object()

        # Verificar si el usuario ya dio like
        context['has_liked'] = False
        if user.is_authenticated:
            context['has_liked'] = entry.likes.filter(user=user).exists()

        # Contar todos los likes
        context['likes_count'] = entry.likes.count()
        return context

class AgregarEntradaCreateView(AdministradorPermisoMixin,CreateView):
    template_name = "entrada/agregar.html"
    form_class= EntradaForm
    success_url = '/'

    def form_valid(self, form):

        #logica del proceso
        entrada = form.save()
        #empleado.full_name = empleado.first_name + ' ' + empleado.last_name
        entrada.save()
        return super(AgregarEntradaCreateView, self).form_valid(form)


class ActualizarEntradaUpdateView(AdministradorPermisoMixin,UpdateView):
    template_name = "entrada/actualizar.html"
    model=Entry
    form_class= EntradaForm
    reverse_lazy = 'entrada_app:entry-lista/'

    def form_valid(self, form):

        return super(ActualizarEntradaUpdateView, self).form_valid(form)


def buscador_general(request):
    queryset=request.GET.get('kword_general')
    print(queryset)
    resultado=Entry.objects.filter(public=True)
    if queryset:
        resultado=Entry.objects.filter(
            Q(title__icontains=resultado) |
            Q(resume__icontains=resultado)
    ).distinct
    print(resultado)
    return render(request,'entrada/lista.html',{'resultado':resultado})

#like
from django.http import HttpResponseRedirect

class ToggleLikeView(View):
    def post(self, request, pk, *args, **kwargs):
        entry = get_object_or_404(Entry, pk=pk)
        like = Like.objects.filter(user=request.user, entry=entry).first()

        if like:
            # Ya existía → quitar like
            like.delete()
        else:
            # No existía → crear
            like = Like.objects.create(user=request.user, entry=entry)

        return HttpResponseRedirect(reverse("entrada_app:entry-detail", kwargs={"slug": entry.slug}))


# comentarios

class CommentCreateView(UsuarioPermisoMixin, CreateView):
    model = Comment
    form_class = CommentForm
    template_name = 'entradas/add_comment.html'

    def form_valid(self, form):
        # Obtener el post mediante slug
        slug = self.kwargs['slug']
        post = get_object_or_404(Entry, slug=slug)
        # Asignar automáticamente post y usuario
        form.instance.post = post
        form.instance.user = self.request.user

        # Manejar comentario padre (respuesta)
        parent_id = form.cleaned_data.get('parent_id')
        if parent_id:
            parent_comment = Comment.objects.filter(id=parent_id, post=post).first()
            form.instance.parent = parent_comment  # puede ser None si no existe

        return super().form_valid(form)

    def get_success_url(self):
        # Redirige al detalle del post después de enviar el comentario
        slug = self.kwargs['slug']
        return reverse_lazy('entrada_app:entry-detail', kwargs={'slug': slug})

class CommentDeleteView(UsuarioPermisoMixin, DeleteView):
    model = Comment

    def get_queryset(self):
        """
        Filtra los comentarios para que el usuario solo pueda
        eliminar los suyos propios
        """
        return Comment.objects.filter(user=self.request.user)

    def get_success_url(self):
        # Redirige al post después de eliminar
        post = self.object.post
        return reverse_lazy('entrada_app:entry-detail', kwargs={'slug': post.slug})

