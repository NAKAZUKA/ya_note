from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

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

    def test_note_and_user_lists_in_context(self):
        """
        Отдельная заметка передаётся на страницу со
        списком заметок в списке object_list в словаре context, и
        заметка автора не отображается в списке заметок пользователя
        """
        clients = (
            (self.user_client, self.note, False),
            (self.author_client, self.note, True),
        )
        for client, note, expected_in_list in clients:
            with self.subTest(client=client, note=note):
                response = client.get(reverse('notes:list'))
                object_list = response.context['object_list']
                if expected_in_list:
                    assert note in object_list
                else:
                    assert note not in object_list

    def test_page_add_and_edit_includ_forms(self):
        """
        Страница создания и редактирования заметки
        включает в себя форму
        """
        urls = (
            ('notes:add', None),
            ('notes:edit', (self.note.slug,)),
        )
        for url, args in urls:
            with self.subTest(url=url):
                response = self.author_client.get(reverse(url, args=args))
                self.assertIn('form', response.context)
