from django.db import models


from django.db.models import Q
from django.contrib.postgres.search import TrigramSimilarity


class EntryManager(models.Manager):
    #procedmiento para entrada

    def entrada_en_portada(self):

        return self.filter(
            public=True,
            portada=True,
        ).order_by('-created').first()

    def entradas_en_home(self):
    #devuelve las ultimas 4 entradas en home
        return self.filter(
            public=True,
            in_home=True,
        ).order_by('-created')[:4]

    #devuelve las ultimas 6 entradas recientes
    def entradas_recientes(self):
        return self.filter(
            public=True,
        ).order_by('-created')[:8]


    #procedimiento para buscar entradas por categoria o palabra clave
    def buscar_entrada_categoria(self, kword, categoria):
        qs = self.filter(public=True)

        if categoria:
            qs = qs.filter(category__short_name=categoria)

        # 👉 VALIDAR SI LA PALABRA ESTÁ VACÍA
        if not kword:
            return qs.order_by('-created')

        # Si no está vacía → sí usamos trigram
        return qs.filter(
            Q(title__icontains=kword) |
            Q(resume__icontains=kword) |
            Q(content__icontains=kword) |
            Q(title__trigram_similar=kword) |
            Q(content__trigram_similar=kword)
        ).order_by('-created')


    def buscar_general(self, kword_general):

        # 👉 VALIDAR SI ESTÁ VACÍO
        if not kword_general:
            return self.filter(public=True).order_by('-created')

        return self.filter(
            Q(title__icontains=kword_general) |
            Q(title__trigram_similar=kword_general)
        ).filter(public=True).order_by('-created')

