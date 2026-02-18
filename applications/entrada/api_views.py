from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404

from .models import Entry, Comment, Like
from .serializers import (
    EntrySerializer,
    EntryCreateSerializer,
    CommentSerializer,
)


# 📌 Listar entradas públicas
class EntryListAPI(generics.ListAPIView):
    serializer_class = EntrySerializer

    def get_queryset(self):
        return Entry.objects.filter(public=True).order_by('-created')


# 📌 Detalle de entrada por slug
class EntryDetailAPI(generics.RetrieveAPIView):
    serializer_class = EntrySerializer
    lookup_field = 'slug'
    queryset = Entry.objects.filter(public=True)


# 📌 Crear entrada
class EntryCreateAPI(generics.CreateAPIView):
    serializer_class = EntryCreateSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


