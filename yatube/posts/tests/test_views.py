import shutil
import tempfile

from django.conf import settings
from django.test import TestCase, Client, override_settings
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.cache import cache
from django import forms
from http import HTTPStatus

from posts.models import Post, Group, User, Follow

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostViewTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        cls.uploaded = SimpleUploadedFile(
            name='small_img.gif',
            content=small_gif,
            content_type='image/gif',
        )
        cls.user = User.objects.create_user(username='auth_user')
        cls.group = Group.objects.create(
            title='test_title',
            slug='test_slug',
        )
        cls.post = Post.objects.create(
            text='test_post',
            author=cls.user,
            group=cls.group,
            image=cls.uploaded,
        )

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(PostViewTest.user)

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def get_context(self, response, flag=False):
        if flag:
            con = response.context.get('post')
            self.assertEqual(con.id, self.post.id)
            self.assertEqual(con.text, self.post.text)
            self.assertEqual(con.image, self.post.image)
        else:
            con = response.context['page_obj'][0]
            self.assertEqual(con.text, self.post.text)
            self.assertEqual(con.image, self.post.image)
            self.assertEqual(con.author.username, self.user.username)

    def test_pages_uses_correct_template(self):
        """
        URL-адрес использует соответствующий шаблон.
        """
        templates_pages_names = {
            reverse('posts:index'): 'posts/index.html',
            reverse('posts:group_list',
                    kwargs={'slug': 'test_slug'}
                    ): 'posts/group_list.html',
            reverse('posts:profile',
                    kwargs={'username': 'auth_user'}
                    ): 'posts/profile.html',
            reverse('posts:post_detail',
                    kwargs={'post_id': f'{self.post.id}'}
                    ): 'posts/post_detail.html',
            reverse('posts:post_edit',
                    kwargs={'post_id': f'{self.post.id}'}
                    ): 'posts/create_post.html',
            reverse('posts:post_create'): 'posts/create_post.html',
        }
        for reverse_name, template in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_index_page_show_correct_context(self):
        """
        Шаблон index сформирован с правильным контекстом.
        """
        response = self.client.get(reverse('posts:index'))
        self.get_context(response)

    def test_group_list_page_show_correct_context(self):
        """
        Шаблон group_list сформирован с правильным контекстом.
        """
        response = self.authorized_client.get(
            reverse('posts:group_list',
                    kwargs={'slug': 'test_slug'}
                    )
        )
        first_object = response.context['group']
        self.assertTrue(isinstance(first_object, Group))
        self.assertEqual(first_object.title, self.group.title)
        self.assertEqual(first_object.slug, self.group.slug)

    def test_profile_page_show_correct_context(self):
        """
        Шаблон profile сформирован с правильным контекстом.
        """
        response = self.authorized_client.get(
            reverse('posts:profile',
                    kwargs={'username': 'auth_user'}
                    )
        )
        self.get_context(response)

    def test_create_post_page_show_correct_context(self):
        """
        Шаблон create_post сформирован с правильным контекстом.
        """
        response = self.authorized_client.get(reverse('posts:post_create'))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_post_detail_page_show_correct_context(self):
        """
        Шаблон post_detail сформирован с правильным контекстом.
        """
        response = self.authorized_client.get(
            reverse('posts:post_detail',
                    kwargs={'post_id': self.post.id}
                    )
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTrue('post' in response.context)
        self.get_context(response, flag=True)

    def test_post_edit_page_show_correct_context(self):
        """
        Шаблон post_edit сформирован с правильным контекстом.
        """
        response = self.authorized_client.get(
            reverse('posts:post_edit',
                    kwargs={'post_id': f'{self.post.id}'}
                    )
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTrue('is_edit' in response.context)

    def test_post_added_correctly_on_pages(self):
        """
        Пост корректно добавляется на страницы.
        """
        post = Post.objects.create(
            text='test_post_added_on_page',
            author=self.user,
            group=self.group,
            image=self.uploaded,
        )
        response_index = self.authorized_client.get(
            reverse('posts:index'))
        response_group = self.authorized_client.get(
            reverse('posts:group_list',
                    kwargs={'slug': f'{self.group.slug}'}))
        response_profile = self.authorized_client.get(
            reverse('posts:profile',
                    kwargs={'username': f'{self.user.username}'}))
        index = response_index.context['page_obj']
        group = response_group.context['page_obj']
        profile = response_profile.context['page_obj']
        self.assertIn(post, index)
        self.assertIn(post, group)
        self.assertIn(post, profile)

    def test_post_added_correctly_in_group(self):
        """
        Пост корректно добавляется в группу.
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
        second_user = User.objects.create_user(username='second_user')
        other_group = Group.objects.create(
            title='other_test_title',
            slug='other_test_slug',
        )
        posts_count = Post.objects.filter(group=self.group).count()
        Post.objects.create(
            text='other_test_post',
            author=second_user,
            group=other_group,
            image=new_uploaded,
        )
        other_posts_count = Post.objects.filter(group=other_group).count()
        self.assertEqual(posts_count, other_posts_count)

    def test_cache_index(self):
        """
        Проверка кэширования страницы index.
        """
        before_create_post = self.authorized_client.get(
            reverse('posts:index'))
        first_item_before = before_create_post.content
        Post.objects.create(
            text='test_cache',
            author=self.user,
            group=self.group)
        after_create_post = self.authorized_client.get(reverse('posts:index'))
        first_item_after = after_create_post.content
        self.assertEqual(first_item_before, first_item_after)
        cache.clear()
        after_clear = self.authorized_client.get(reverse('posts:index'))
        self.assertNotEqual(first_item_after, after_clear)

    def test_page_404(self):
        """
        Страница 404 использует кастомный шаблон.
        """
        templates_urls = {
            '/unexisting_page/': 'core/404.html',
        }
        for address, template in templates_urls.items():
            response = self.client.get(address)
            self.assertTemplateUsed(response, template)


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='test_title',
            slug='test_slug',
        )
        cls.posts = []
        for i in range(settings.QTY_POSTS):
            cls.posts.append(Post(
                text=f'test_post {i}',
                author=cls.user,
                group=cls.group))
        Post.objects.bulk_create(cls.posts)

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_first_page_contains_ten_records(self):
        """
        Проверка пагинатора на первой странице.
        """
        urls = (
            reverse('posts:index'),
            reverse('posts:group_list', kwargs={
                'slug': self.group.slug
            }),
            reverse('posts:profile', kwargs={
                'username': self.user.username
            }),
        )
        for url in urls:
            guest_response = self.client.get(url)
            auth_response = self.authorized_client.get(url)
            self.assertEqual(
                len(guest_response.context.get('page_obj').object_list),
                settings.POSTS_ON_PAGE
            )
            self.assertEqual(
                len(auth_response.context.get('page_obj').object_list),
                settings.POSTS_ON_PAGE
            )

    def test_second_page_contains_three_records(self):
        """
        Проверка пагинатора на второй странице.
        """
        urls = (
            reverse('posts:index'),
            reverse('posts:group_list', kwargs={
                'slug': self.group.slug
            }),
            reverse('posts:profile', kwargs={
                'username': self.user.username
            }),
        )
        for url in urls:
            guest_response = self.client.get(url + '?page=2')
            auth_response = self.authorized_client.get(url + '?page=2')
            self.assertEqual(
                len(guest_response.context.get('page_obj').object_list),
                settings.QTY_POSTS - settings.POSTS_ON_PAGE
            )
            self.assertEqual(
                len(auth_response.context.get('page_obj').object_list),
                settings.QTY_POSTS - settings.POSTS_ON_PAGE
            )


class FollowViewTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.first_user = User.objects.create_user(username='first_auth_user')
        cls.second_user = User.objects.create_user(username='second_auth_user')
        cls.author = User.objects.create_user(username='author')
        cls.follow = Follow.objects.create(
            user=cls.second_user,
            author=cls.author,
        )

    def setUp(self):
        self.first_authorized_client = Client()
        self.first_authorized_client.force_login(FollowViewTest.first_user)
        self.second_authorized_client = Client()
        self.second_authorized_client.force_login(FollowViewTest.second_user)

    def test_user_follow_to_author(self):
        """
        Пользователь подписался на автора.
        """
        count_follow = Follow.objects.filter(user=self.first_user).count()
        data_follow = {'user': self.first_user,
                       'author': self.author}
        redirect = reverse(
            'posts:profile',
            kwargs={'username': self.author.username}
        )
        response = self.first_authorized_client.post(
            reverse('posts:profile_follow',
                    kwargs={'username': self.author.username}),
            data=data_follow,
            follow=True)
        new_count_follow = Follow.objects.filter(
            user=self.first_user).count()
        self.assertTrue(Follow.objects.filter(
            user=self.first_user,
            author=self.author).exists())
        self.assertRedirects(response, redirect)
        self.assertEqual(count_follow + 1, new_count_follow)

    def test_user_unfollow_to_author(self):
        """
        Пользователь отписался от автора.
        """
        count_follow = Follow.objects.filter(user=self.second_user).count()
        data_follow = {'user': self.second_user,
                       'author': self.author}
        redirect = reverse(
            'posts:profile',
            kwargs={'username': self.author.username}
        )
        response = self.second_authorized_client.post(
            reverse('posts:profile_unfollow',
                    kwargs={'username': self.author.username}),
            data=data_follow,
            follow=True)
        new_count_unfollow = Follow.objects.filter(
            user=self.second_user).count()
        self.assertFalse(Follow.objects.filter(
            user=self.second_user,
            author=self.author).exists())
        self.assertRedirects(response, redirect)
        self.assertNotEqual(count_follow, new_count_unfollow)

    def test_follower_new_post(self):
        """
        У подписчика появляется новый пост избранного автора.
        """
        new_post_follower = Post.objects.create(
            author=self.author,
            text='test_text')
        Follow.objects.create(user=self.first_user,
                              author=self.author)
        response = self.first_authorized_client.get(
            reverse('posts:follow_index'))
        new_posts = response.context['page_obj']
        self.assertIn(new_post_follower, new_posts)

    def test_unfollower_new_post(self):
        """
        Новый пост не появляется у пользователя, который не подписан.
        """
        new_post_follower = Post.objects.create(
            author=self.first_user,
            text='other_test_text')
        Follow.objects.create(user=self.second_user,
                              author=self.author)
        response = self.second_authorized_client.get(
            reverse('posts:follow_index'))
        new_post_unfollower = response.context['page_obj']
        self.assertNotIn(new_post_follower, new_post_unfollower)
