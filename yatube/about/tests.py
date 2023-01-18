from django.test import TestCase

from http import HTTPStatus


class StaticPagesTests(TestCase):
    def test_about_url_exists_at_desired_location(self):
        """
        Проверка доступности страниц
        /about/author/ и /about/tech/.
        """
        urls = ('/about/author/', '/about/tech/')
        for url in urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_about_url_uses_correct_template(self):
        """
        URL-адрес /about/author/ и /about/tech/
        использует соответствующий шаблон.
        """
        templates_urls = {
            '/about/author/': 'about/author.html',
            '/about/tech/': 'about/tech.html',
        }
        for address, template in templates_urls.items():
            with self.subTest(address=address):
                response = self.client.get(address)
                self.assertTemplateUsed(response, template)
