from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from notes.models import Note

User = get_user_model()


class RoutesTestCase(TestCase):

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

    def test_home_page_for_anonymous_user(self):
        """
        Проверяем доступность страниц
        для анонимных пользователей.
        """
        urls = (
            'notes:home',
            'users:logout',
            'users:login',
            'users:signup'
        )
        for url in urls:
            with self.subTest(url=url):
                response = self.user_client.get(reverse(url))
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_availability_different_pages_for_auth_user(self):
        """
        Проверяем доступность страниц
        для авторизированных пользователей.
        """
        urls = (
            'notes:list',
            'notes:add',
            'notes:success',
        )
        for url in urls:
            with self.subTest(url=url):
                response = self.user_client.get(reverse(url))
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_availability_detail_delete_edit_page_for_only_author(self):
        """
        Проверяем доступность страниц
        для авторизированных пользователей
        только для автора заметки.
        """
        urls = (
            ('notes:detail', self.note.slug),
            ('notes:edit', self.note.slug),
            ('notes:delete', self.note.slug),
        )
        users_ststus = (
            (self.user_client, HTTPStatus.NOT_FOUND),
            (self.author_client, HTTPStatus.OK),
        )
        for user, status in users_ststus:
            for url, args in urls:
                with self.subTest(url=url, user=user):
                    response = user.get(reverse(url, args=(args,)))
                    self.assertEqual(response.status_code, status)

    def test_redirect_to_page_auth0rizetion_for_anonymous_user(self):
        """Проверяем редиректы для анонимных пользователей."""
        urls = ('notes:list', 'notes:add', 'notes:success')
        for url in urls:
            with self.subTest(url=url):
                response = self.client.get(reverse(url))
                self.assertRedirects(
                    response,
                    f'{reverse("users:login")}?next={reverse(url)}'
                )
