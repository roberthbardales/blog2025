import json
import random

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.views.generic import (
    CreateView,
    DeleteView,
    FormView,
    ListView,
    UpdateView,
    View,
)

from .forms import (
    ConfigurarEvaluacionForm,
    ImportarJSONForm,
    OpcionFormSet,
    PreguntaForm,
    TemaForm,
)
from .models import Opcion, Pregunta, Tema

LOGIN_URL = reverse_lazy('users_app:user-login')

NIVELES_VALIDOS = {Pregunta.FACIL, Pregunta.MEDIO, Pregunta.DIFICIL}


class TemaListView(LoginRequiredMixin, ListView):
    """Lista los bancos de preguntas (temas)"""

    model = Tema
    template_name = 'evaluaciones/tema_list.html'
    context_object_name = 'temas'
    login_url = LOGIN_URL


class TemaCreateView(LoginRequiredMixin, CreateView):
    model = Tema
    form_class = TemaForm
    template_name = 'evaluaciones/tema_form.html'
    login_url = LOGIN_URL

    def get_success_url(self):
        messages.success(self.request, '¡Tema creado exitosamente!')
        return reverse('evaluaciones_app:tema-lista')


class TemaUpdateView(LoginRequiredMixin, UpdateView):
    model = Tema
    form_class = TemaForm
    template_name = 'evaluaciones/tema_form.html'
    login_url = LOGIN_URL
    slug_field = 'slug'
    slug_url_kwarg = 'slug'

    def get_success_url(self):
        messages.success(self.request, '¡Tema actualizado exitosamente!')
        return reverse('evaluaciones_app:tema-lista')


class TemaDeleteView(LoginRequiredMixin, DeleteView):
    model = Tema
    template_name = 'evaluaciones/tema_confirm_delete.html'
    login_url = LOGIN_URL
    success_url = reverse_lazy('evaluaciones_app:tema-lista')
    slug_field = 'slug'
    slug_url_kwarg = 'slug'

    def delete(self, request, *args, **kwargs):
        messages.success(request, '¡Tema eliminado exitosamente!')
        return super().delete(request, *args, **kwargs)


class PreguntaListView(LoginRequiredMixin, ListView):
    """Lista las preguntas de un tema con sus opciones"""

    template_name = 'evaluaciones/pregunta_list.html'
    context_object_name = 'preguntas'
    login_url = LOGIN_URL

    def get_queryset(self):
        self.tema = get_object_or_404(Tema, slug=self.kwargs['slug'])
        return Pregunta.objects.filter(tema=self.tema).prefetch_related('opciones')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tema'] = self.tema
        return context


class PreguntaMixin(LoginRequiredMixin):
    login_url = LOGIN_URL
    form_class = PreguntaForm
    template_name = 'evaluaciones/pregunta_form.html'

    def get_success_url(self):
        return reverse(
            'evaluaciones_app:pregunta-lista',
            kwargs={'slug': self.object.tema.slug}
        )

    def get_tema_slug(self):
        if getattr(self, 'object', None) and self.object.pk:
            return self.object.tema.slug
        return self.kwargs.get('slug')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tema_slug'] = self.get_tema_slug()
        if self.request.POST:
            context['formset'] = OpcionFormSet(self.request.POST)
        else:
            context['formset'] = OpcionFormSet()
        return context


class PreguntaCreateView(PreguntaMixin, CreateView):

    def get_initial(self):
        initial = super().get_initial()
        tema_slug = self.kwargs.get('slug')
        if tema_slug:
            initial['tema'] = get_object_or_404(Tema, slug=tema_slug).pk
        return initial

    def form_valid(self, form):
        formset = OpcionFormSet(self.request.POST)
        if not formset.is_valid():
            return self.render_to_response(
                self.get_context_data(form=form, formset=formset)
            )
        with transaction.atomic():
            form.instance.tema = get_object_or_404(
                Tema, slug=self.kwargs['slug']
            )
            self.object = form.save()
            formset.instance = self.object
            formset.save()
        messages.success(self.request, '¡Pregunta creada exitosamente!')
        return redirect(self.get_success_url())


class PreguntaUpdateView(PreguntaMixin, UpdateView):
    model = Pregunta

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['formset'] = OpcionFormSet(
                self.request.POST, instance=self.object
            )
        else:
            context['formset'] = OpcionFormSet(instance=self.object)
        return context

    def form_valid(self, form):
        formset = OpcionFormSet(self.request.POST, instance=self.object)
        if not formset.is_valid():
            return self.render_to_response(
                self.get_context_data(form=form, formset=formset)
            )
        with transaction.atomic():
            self.object = form.save()
            formset.save()
        messages.success(self.request, '¡Pregunta actualizada exitosamente!')
        return redirect(self.get_success_url())


class PreguntaDeleteView(LoginRequiredMixin, DeleteView):
    model = Pregunta
    template_name = 'evaluaciones/pregunta_confirm_delete.html'
    login_url = LOGIN_URL

    def get_success_url(self):
        messages.success(self.request, '¡Pregunta eliminada exitosamente!')
        return reverse(
            'evaluaciones_app:pregunta-lista',
            kwargs={'slug': self.object.tema.slug}
        )


class ImportarJSONView(LoginRequiredMixin, FormView):
    """Carga masiva de preguntas desde un archivo .json"""

    template_name = 'evaluaciones/importar_json.html'
    form_class = ImportarJSONForm
    login_url = LOGIN_URL

    def dispatch(self, request, *args, **kwargs):
        self.tema = get_object_or_404(Tema, slug=kwargs['slug'])
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tema'] = self.tema
        return context

    def form_valid(self, form):
        datos = form.cleaned_data['datos']
        creadas, errores = self._importar_preguntas(datos)

        if creadas:
            messages.success(
                self.request,
                f'¡Importación completada! {creadas} pregunta(s) creada(s) '
                f'en "{self.tema.nombre}".'
            )
        for error in errores:
            messages.error(self.request, error)

        return redirect('evaluaciones_app:tema-lista')

    def _importar_preguntas(self, datos):
        creadas = 0
        errores = []

        for i, item in enumerate(datos, start=1):
            error = self._validar_item(item)
            if error:
                errores.append(f'Pregunta #{i}: {error}')
                continue

            opciones = item['opciones']
            correctas = sum(
                1 for o in opciones if o.get('es_correcta') is True
            )
            if correctas != 1:
                errores.append(
                    f'Pregunta #{i}: debe tener exactamente una opción '
                    f'"es_correcta": true (tiene {correctas})'
                )
                continue

            niveles_validos = dict(Pregunta.NIVEL_CHOICES)
            nivel = item.get('nivel', Pregunta.MEDIO)
            if nivel not in niveles_validos:
                errores.append(
                    f'Pregunta #{i}: nivel inválido "{nivel}" '
                    f'(use: facil, medio o dificil)'
                )
                continue

            try:
                with transaction.atomic():
                    pregunta = Pregunta.objects.create(
                        tema=self.tema,
                        texto=item['texto'],
                        nivel=nivel,
                        explicacion=item.get('explicacion', ''),
                    )
                    Opcion.objects.bulk_create([
                        Opcion(
                            pregunta=pregunta,
                            texto=o['texto'],
                            es_correcta=o.get('es_correcta', False),
                        )
                        for o in opciones
                    ])
                creadas += 1
            except Exception as e:
                errores.append(f'Pregunta #{i}: error al guardar ({e})')

        return creadas, errores

    @staticmethod
    def _validar_item(item):
        if not isinstance(item, dict):
            return 'debe ser un objeto con "texto" y "opciones"'
        if not item.get('texto'):
            return 'falta el campo "texto"'
        opciones = item.get('opciones')
        if not isinstance(opciones, list) or len(opciones) < 2:
            return 'debe tener al menos 2 opciones en "opciones"'
        for o in opciones:
            if not isinstance(o, dict) or not o.get('texto'):
                return 'cada opción debe ser un objeto con el campo "texto"'
        return None


class ConfigurarEvaluacionView(LoginRequiredMixin, FormView):
    """Formulario previo al quiz: nivel + cantidad + modo"""

    template_name = 'evaluaciones/configurar_evaluacion.html'
    form_class = ConfigurarEvaluacionForm
    login_url = LOGIN_URL

    def dispatch(self, request, *args, **kwargs):
        self.tema = get_object_or_404(Tema, slug=kwargs['slug'])
        return super().dispatch(request, *args, **kwargs)

    def get_initial(self):
        return {
            'nivel': self.request.GET.get('nivel', ''),
            'cantidad': self.request.GET.get('cantidad', 10),
            'modo': self.request.GET.get('modo', 'examen'),
        }

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tema'] = self.tema
        return context

    def form_valid(self, form):
        url = reverse(
            'evaluaciones_app:evaluacion',
            kwargs={'slug': self.tema.slug}
        )
        params = {
            'nivel': form.cleaned_data['nivel'],
            'cantidad': form.cleaned_data['cantidad'],
            'modo': form.cleaned_data['modo'],
        }
        query = '&'.join(f'{k}={v}' for k, v in params.items())
        return redirect(f'{url}?{query}')


def _armar_quiz(tema, nivel, cantidad):
    """Selecciona preguntas mezcladas y baraja sus opciones"""
    qs = tema.preguntas.all()
    if nivel in NIVELES_VALIDOS:
        qs = qs.filter(nivel=nivel)
    preguntas = list(qs.order_by('?')[:cantidad])

    quiz = []
    for p in preguntas:
        opciones_ordenadas = random.sample(list(p.opciones.all()),
                                           p.opciones.count())
        quiz.append({
            'id': p.pk,
            'texto': p.texto,
            'nivel': p.nivel,
            'explicacion': p.explicacion,
            'opciones': [
                {'id': o.pk, 'texto': o.texto}
                for o in opciones_ordenadas
            ],
        })
    return quiz


class EvaluacionView(LoginRequiredMixin, View):
    """Renderiza el quiz de un tema (una pregunta por vez con JS)"""

    login_url = LOGIN_URL

    def get(self, request, slug):
        tema = get_object_or_404(Tema, slug=slug)

        form = ConfigurarEvaluacionForm(data=request.GET or None)
        if not form.is_valid():
            return redirect('evaluaciones_app:configurar-evaluacion', slug=slug)

        nivel = form.cleaned_data['nivel'] or ''
        cantidad = form.cleaned_data['cantidad']
        modo = form.cleaned_data['modo']

        disponibles = tema.preguntas.filter(nivel=nivel).count() \
            if nivel in NIVELES_VALIDOS else tema.preguntas.count()

        if disponibles == 0:
            messages.warning(
                request,
                f'El tema "{tema.nombre}" no tiene preguntas para ese nivel.'
            )
            return redirect('evaluaciones_app:configurar-evaluacion', slug=slug)

        cantidad_efectiva = min(cantidad, disponibles)
        avisos = []
        if cantidad_efectiva < cantidad:
            avisos.append(
                f'Solo hay {disponibles} pregunta(s) disponible(s); '
                f'se usarán todas.'
            )

        quiz = _armar_quiz(tema, nivel, cantidad_efectiva)

        return render(
            request,
            'evaluaciones/evaluacion.html',
            {
                'tema': tema,
                'quiz_json': json.dumps(quiz),
                'modo': modo,
                'nivel': nivel,
                'avisos': avisos,
            }
        )


class VerificarPreguntaView(LoginRequiredMixin, View):
    """AJAX modo Práctica: corrige una pregunta al instante"""

    login_url = LOGIN_URL

    def post(self, request, pk):
        try:
            data = json.loads(request.body.decode('utf-8'))
        except (json.JSONDecodeError, UnicodeDecodeError):
            return JsonResponse({'error': 'JSON inválido'}, status=400)

        opcion_id = data.get('opcion_id')
        if not opcion_id:
            return JsonResponse({'error': 'Falta opcion_id'}, status=400)

        pregunta = get_object_or_404(Pregunta, pk=pk)
        correcta = pregunta.opciones.filter(es_correcta=True).first()

        return JsonResponse({
            'es_correcta': bool(correcta and str(correcta.pk) == str(opcion_id)),
            'opcion_correcta_id': correcta.pk if correcta else None,
            'texto_correcta': correcta.texto if correcta else '',
            'explicacion': pregunta.explicacion,
        })


class CalificarEvaluacionView(LoginRequiredMixin, View):
    """AJAX modo Examen: corrige todo y devuelve resultados"""

    login_url = LOGIN_URL

    def post(self, request, slug):
        tema = get_object_or_404(Tema, slug=slug)

        try:
            data = json.loads(request.body.decode('utf-8'))
            respuestas = data.get('respuestas', {})
        except (json.JSONDecodeError, UnicodeDecodeError, AttributeError):
            return JsonResponse({'error': 'JSON inválido'}, status=400)

        if not isinstance(respuestas, dict):
            return JsonResponse({'error': 'Formato inválido'}, status=400)

        detalle = []
        correctas = incorrectas = 0

        for pregunta_id, opcion_id in respuestas.items():
            pregunta = Pregunta.objects.filter(
                pk=pregunta_id, tema=tema
            ).first()
            if not pregunta:
                continue

            correcta = pregunta.opciones.filter(es_correcta=True).first()
            elegida = pregunta.opciones.filter(pk=opcion_id).first()

            acierto = bool(correcta and elegida and correcta.pk == elegida.pk)
            if acierto:
                correctas += 1
            else:
                incorrectas += 1

            detalle.append({
                'pregunta_id': pregunta.pk,
                'texto_pregunta': pregunta.texto,
                'elegida_id': elegida.pk if elegida else None,
                'texto_elegida': elegida.texto if elegida else '(sin respuesta)',
                'correcta_id': correcta.pk if correcta else None,
                'texto_correcta': correcta.texto if correcta else '',
                'es_correcta': acierto,
                'explicacion': pregunta.explicacion,
            })

        total = correctas + incorrectas
        return JsonResponse({
            'correctas': correctas,
            'incorrectas': incorrectas,
            'total': total,
            'porcentaje': round(correctas * 100 / total) if total else 0,
            'detalle': detalle,
        })
