from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from pytils.translit import slugify

from notes.forms import WARNING, NoteForm
from notes.models import Note

User = get_user_model()


class ContentTestCase(TestCase):

    TITLE = 'Заголовок'
    TEXT = 'Текст'

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create(username='testUser')
        cls.user_client = Client()
        cls.user_client.force_login(cls.user)
        cls.author = User.objects.create(username='testAuthor')
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.note = Note.objects.create(
            title=cls.TITLE,
            text=cls.TEXT,
            author=cls.author,
        )

    def test_auth_user_and_notauth_user_can_create_note(self):
        """
        Тест алогиненный пользователь может создать заметку,
        а анонимный — не может
        """
        users = (
            (self.user_client, HTTPStatus.OK),
            (self.client, HTTPStatus.FOUND),
        )
        for client, status in users:
            with self.subTest(client=client):
                response = client.get(reverse('notes:add'))
                self.assertEqual(response.status_code, status)

    def test_cannot_create_note_with_same_url(self):
        """Тест нельзя создать заметку с одинаковым url"""
        response = self.user_client.post(
            reverse('notes:add'),
            data={
                'title': self.TITLE,
                'text': self.TEXT,
            },
            follow=True
        )
        self.assertContains(response, WARNING)

    def test_autofill_url_in_form(self):
        """Тест проверяет что запись создается с автозаполненным slug"""
        expected_slug = slugify(self.note.title)
        form = NoteForm(instance=self.note)
        self.assertEqual(form.initial['slug'], expected_slug)

    def test_author_can_edit_delete_note_and_cannot_edit_delete_others(self):
        """
        Тест проверяет возможность редактирования и удаления своих заметок
        и недоступность редактирования и удаления заметок других пользователей
        """
        users = (
            (self.user_client, self.note, HTTPStatus.NOT_FOUND),
            (self.author_client, self.note, HTTPStatus.OK),
        )
        for client, note, status in users:
            with self.subTest(client=client, note=note):
                response = client.get(reverse('notes:edit', args=(note.slug,)))
                self.assertEqual(response.status_code, status)
