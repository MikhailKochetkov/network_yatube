from django.test import TestCase
from django.conf import settings

from posts.models import Post, Group, User


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Тестовый слаг',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Утро начал хорошо, поработал, но вечер! Боже, неужели никогда я',
        )

    def test_models_have_correct_post_text(self):
        """
        Проверяем, что у модели Post корректно работает __str__.
        """
        self.assertEqual(len(str(self.post).split(' ')), settings.QTY_WORDS)

    def test_models_have_correct_group_title(self):
        """
        Проверяем, что у модели Group корректно работает __str__.
        """
        self.assertEqual(self.group.title, str(self.group))

    def test_verbose_name(self):
        """
        Проверка verbose_name модели Post.
        """
        tst_verbose_name = self.post
        field_verboses = {
            'text': 'Текст поста',
            'pub_date': 'Дата публикации',
            'author': 'Автор',
            'group': 'Группа',
        }
        for field, expected_value in field_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(
                    tst_verbose_name._meta.get_field(field).verbose_name,
                    expected_value
                )

    def test_help_text(self):
        """
        Проверка help_text модели Post.
        """
        tst_help_text = self.post
        field_help = {
            'text': 'Введите текст поста',
            'group': 'Группа, к которой будет относиться пост',
        }
        for field, expected_value in field_help.items():
            with self.subTest(field=field):
                self.assertEqual(
                    tst_help_text._meta.get_field(field).help_text,
                    expected_value
                )
