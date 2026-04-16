from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse

from applications.favoritos.models import Favorites
from applications.entrada.models import Category, Comment, Entry, Like


User = get_user_model()


class EntryDetailViewTests(TestCase):
    def setUp(self):
        self.author = User.objects.create(
            email='author@example.com',
            full_name='Author User',
            is_active=True,
        )
        self.viewer = User.objects.create(
            email='viewer@example.com',
            full_name='Viewer User',
            is_active=True,
        )
        self.category = Category.objects.create(
            short_name='tech',
            name='Tecnología',
        )
        image = SimpleUploadedFile(
            'test.jpg',
            b'filecontent',
            content_type='image/jpeg'
        )
        self.entry = Entry.objects.create(
            user=self.author,
            category=self.category,
            title='Entry Detail Test',
            resume='Resumen de prueba',
            content='Contenido de prueba',
            public=True,
            image=image,
        )

    def test_entry_detail_context_includes_related_data(self):
        comment = Comment.objects.create(
            post=self.entry,
            user=self.author,
            content='Comentario principal',
        )
        Comment.objects.create(
            post=self.entry,
            user=self.viewer,
            content='Respuesta al comentario',
            parent=comment,
        )
        Like.objects.create(user=self.viewer, entry=self.entry)
        Favorites.objects.create(user=self.viewer, entry=self.entry)

        self.client.force_login(self.viewer)
        response = self.client.get(
            reverse('entrada_app:entry-detail', kwargs={'slug': self.entry.slug})
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['entry'].pk, self.entry.pk)
        self.assertTrue(response.context['has_liked'])
        self.assertTrue(response.context['is_favorite'])
        self.assertEqual(response.context['likes_count'], 1)
        self.assertEqual(len(response.context['main_comments']), 1)
        self.assertEqual(response.context['main_comments'][0].content, 'Comentario principal')
        self.assertEqual(response.context['main_comments'][0].replies.count(), 1)
