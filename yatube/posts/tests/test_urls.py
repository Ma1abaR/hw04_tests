from http import HTTPStatus
from django.contrib.auth import get_user_model
from django.test import TestCase, Client

from ..models import Group, Post

User = get_user_model()


class TaskURLTests(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='HasNoName')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            description='Тестовое описание',
            slug='test-slug'
        )

        cls.post = Post.objects.create(
            author=cls.user,
            group=cls.group,
            text='Тестовый пост'
        )

        cls.url_index = '/'
        cls.url_group_list = f'/group/{cls.group.slug}/'
        cls.url_post_detail = f'/posts/{cls.post.pk}/'
        cls.url_profile = f'/profile/{cls.user.username}/'
        cls.url_post_create = '/create/'
        cls.url_post_edit = f'/posts/{cls.post.pk}/edit/'
        cls.url_redirect_to_login = '/auth/login/?next=/create/'
        cls.url_unexisting_page = '/unexisting_page/'

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.another_user = User.objects.create_user(username='TestUser')
        self.another_user_client = Client()
        self.another_user_client.force_login(self.another_user)

    def test_urls_uses_correct_template(self):
        templates_url_names = {
            self.url_index: 'posts/index.html',
            self.url_group_list: 'posts/group_list.html',
            self.url_profile: 'posts/profile.html',
            self.url_post_detail: 'posts/post_detail.html',
            self.url_post_edit: 'posts/create_post.html',
            self.url_post_create: 'posts/create_post.html',
        }

        for address, template in templates_url_names.items():
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertTemplateUsed(response, template)

    def test_unexisting_page(self):
        response = self.guest_client.get(self.url_unexisting_page)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_post_create_url_redirect_anonymous_on_admin_login(self):
        response = self.guest_client.get(self.url_post_create, follow=True)
        self.assertRedirects(
            response, self.url_redirect_to_login
        )

    def test_post_edit_url_redirect_not_author_on_post_detail(self):
        response = self.another_user_client.get(
            self.url_post_edit, follow=True)
        self.assertRedirects(
            response, self.url_post_detail
        )

    def test_home_url_exists_at_desired_location(self):
        response = self.guest_client.get(self.url_index)
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_group_list_exists_at_desired_location(self):
        response = self.guest_client.get(self.url_group_list)
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_profile_exists_at_desired_location(self):
        response = self.guest_client.get(self.url_profile)
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_post_detail_exists_at_desired_location(self):
        response = self.guest_client.get(self.url_post_detail)
        self.assertEqual(response.status_code, HTTPStatus.OK)
