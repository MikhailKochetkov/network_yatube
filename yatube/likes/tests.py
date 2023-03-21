import unittest

from django.test import TestCase, Client
from django.urls import reverse

from http import HTTPStatus

from posts.models import Post, Group, User
from .models import PostLike


class PostLikeTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username='author')
        cls.first_user = User.objects.create_user(username='first_auth_user')
        cls.second_user = User.objects.create_user(username='second_auth_user')
        cls.group = Group.objects.create(
            title='test_title',
            slug='test_slug',
        )
        cls.post = Post.objects.create(text='test_text',
                                       author=cls.author,
                                       group=cls.group)
        cls.like = PostLike.objects.create(post=cls.post,
                                           user=cls.first_user,
                                           is_like=1)

    def setUp(self):
        self.author_authorized_client = Client()
        self.first_authorized_client = Client()
        self.second_authorized_client = Client()
        self.author_authorized_client.force_login(PostLikeTest.author)
        self.first_authorized_client.force_login(PostLikeTest.first_user)
        self.second_authorized_client.force_login(PostLikeTest.second_user)

    def test_add_like(self):
        """
        Проверка добавления лайка.
        """
        like_count = PostLike.objects.count()
        form_data = {'post_id': self.post.id,
                     'user_id': self.second_user.id,
                     'is_like': True}
        response = self.second_authorized_client.post(
            reverse('likes:add'), data=form_data, follow=True)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTrue(PostLike.objects.filter(
            post=form_data['post_id'],
            user=form_data['user_id'],
            is_like=True
        ).exists())
        self.assertEqual(PostLike.objects.count(),
                         like_count + 1)

    @unittest.skip('Пропускаем тест')
    def test_remove_like(self):
        """
        Проверка удаления лайка.
        """
        pass

    @unittest.skip('Пропускаем тест')
    def test_guest_client_not_add_like(self):
        """
        Проверка запрета добавления лайка
        для неавторизованого пользователя.
        """
        pass
