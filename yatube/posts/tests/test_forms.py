import shutil
import tempfile

from django.test import TestCase, Client, override_settings
from django.urls import reverse
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from http import HTTPStatus

from posts.models import Post, Group, User, Comment

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostFormTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth_user')
        cls.group = Group.objects.create(
            title='test_title',
            slug='test_slug',
        )

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(PostFormTest.user)
        self.small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        self.uploaded = SimpleUploadedFile(
            name='small_img.gif',
            content=self.small_gif,
            content_type='image/gif',
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def test_create_post(self):
        """
        Проверка создания поста.
        """
        posts_count = Post.objects.count()
        form_data = {'text': 'form_post_text',
                     'group': self.group.id,
                     'image': self.uploaded,
                     }
        response = self.authorized_client.post(reverse('posts:post_create'),
                                               data=form_data,
                                               follow=True)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTrue(Post.objects.filter(
            text=form_data['text'],
            group=PostFormTest.group.id,
            image=f'posts/{self.uploaded}',
            author=self.user).exists())
        self.assertEqual(Post.objects.count(), posts_count + 1)

    def test_edit_post(self):
        """
        Проверка редактирования поста.
        """
        new_small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        new_uploaded = SimpleUploadedFile(
            name='new_small_img.gif',
            content=new_small_gif,
            content_type='image/gif',
        )
        editing_post = Post.objects.create(text='test_text',
                                           author=PostFormTest.user,
                                           group=PostFormTest.group,
                                           image=self.uploaded)
        self.editing_group = Group.objects.create(title='test_title_new',
                                                  slug='test-slug_new',
                                                  description='test_desc')
        form_data = {'text': 'test_text_new',
                     'group': self.editing_group.id,
                     'image': new_uploaded}
        response = self.authorized_client.post(
            reverse('posts:post_edit', kwargs={'post_id': editing_post.id}),
            data=form_data,
            follow=True)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTrue(Post.objects.filter(
            group=self.editing_group.id,
            author=self.user,
            pub_date=editing_post.pub_date,
            text=form_data['text'],
            image=f'posts/{new_uploaded}',
        ).exists())
        self.assertNotEqual(editing_post.text, form_data['text'])
        self.assertNotEqual(editing_post.group, form_data['group'])
        self.assertNotEqual(editing_post.image, form_data['image'])

    def test_guest_client_cannot_create_post(self):
        """
        Неавторизованный пользователь не может создать пост.
        """
        posts_count = Post.objects.count()
        form_data = {'text': 'form_post_text',
                     'group': self.group.id,
                     'image': self.uploaded,
                     }
        response = self.client.post(reverse('posts:post_create'),
                                    data=form_data,
                                    follow=True)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertNotEqual(Post.objects.count(), posts_count + 1)

    def test_group_may_be_null(self):
        """
        Проверяем, что группу для поста можно не указывать.
        """
        post = Post.objects.create(text='test_text',
                                   author=self.user,
                                   group=self.group)
        form_data = {'text': 'form_post_text',
                     'group': ''}
        response = self.authorized_client.post(
            reverse('posts:post_edit', kwargs={'post_id': post.id}),
            data=form_data,
            follow=True)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertNotEqual(post.group, form_data['group'])

    def test_guest_client_redirect(self):
        """
        Проверка перенаправления неавторизованного пользователя.
        """
        post = Post.objects.create(text='test_text',
                                   author=self.user,
                                   group=self.group)
        form_data = {'text': 'form_post_text'}
        response = self.client.post(
            reverse('posts:post_edit', kwargs={'post_id': post.id}),
            data=form_data,
            follow=True)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertRedirects(response,
                             f'/auth/login/?next=/posts/{post.id}/edit/')

    def test_guest_no_edit_post(self):
        """
        Проверка запрета редактирования для неавторизованного пользователя.
        """
        posts_count = Post.objects.count()
        form_data = {
            'text': 'form_post_text',
            'group': self.group.id
        }
        response = self.client.post(reverse('posts:post_create'),
                                    data=form_data,
                                    follow=True)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertNotEqual(Post.objects.count(),
                            posts_count + 1)


class CommentFormTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth_user')
        cls.group = Group.objects.create(
            title='test_title',
            slug='test_slug',
        )
        cls.post = Post.objects.create(text='test_text',
                                       author=cls.user,
                                       group=cls.group)
        cls.comment = Comment.objects.create(post_id=cls.post.id,
                                             author=cls.user,
                                             text='test_comment')

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(CommentFormTest.user)

    def test_create_comment(self):
        """
        Проверка создания комментария.
        """
        comment_count = Comment.objects.count()
        form_data = {'post_id': self.post.id,
                     'text': 'other_test_comment'}
        response = self.authorized_client.post(
            reverse('posts:add_comment',
                    kwargs={'post_id': self.post.id}),
            data=form_data, follow=True)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTrue(Comment.objects.filter(
            text=form_data['text'],
            post=self.post.id,
            author=self.user
        ).exists())
        self.assertEqual(Comment.objects.count(),
                         comment_count + 1
                         )

    def test_guest_client_not_edit_comment(self):
        """
        Проверка запрета создавать комментарии
        для неавторизованого пользователя.
        """
        comment_count = Comment.objects.count()
        form_data = {'text': 'other_test_comment'}
        response = self.client.post(reverse('posts:add_comment',
                                            kwargs={'post_id': self.post.id}),
                                    data=form_data,
                                    follow=True)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertNotEqual(Comment.objects.count(),
                            comment_count + 1
                            )

    def test_comment_empty(self):
        """
        Проверка запрета пустого комментария.
        """
        comment_count = Comment.objects.count()
        form_data = {'text': ''}
        response = self.authorized_client.post(
            reverse('posts:add_comment',
                    kwargs={'post_id': self.post.id}),
            data=form_data,
            follow=True)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertNotEqual(Comment.objects.count(),
                            comment_count + 1)
