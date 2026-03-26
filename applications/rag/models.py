from django.db import models
from applications.entrada.models import Entry


class EntryChunk(models.Model):
    entry = models.ForeignKey(Entry, on_delete=models.CASCADE, related_name="chunks")
    content = models.TextField()
    embedding = models.JSONField()  # guardamos el vector aquí

    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Chunk {self.id} - Entry {self.entry.id}"