from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from ..models import Group, Post

User = get_user_model()


class TestsViewsPosts(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            group=cls.group,
            text='Тестовый пост'
        )
        cls.url_index = reverse('posts:index')
        cls.url_group_list = reverse(
            'posts:group_list',
            kwargs={'slug': cls.group.slug}
        )
        cls.url_post_detail = reverse(
            'posts:post_detail',
            kwargs={'post_id': cls.post.pk}
        )
        cls.url_profile = reverse(
            'posts:profile', kwargs={'username': cls.user.username}
        )
        cls.url_post_create = reverse('posts:post_create')
        cls.url_post_edit = reverse(
            'posts:post_edit', kwargs={'post_id': cls.post.pk}
        )

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""

        templates = {
            self.url_index: 'posts/index.html',
            self.url_group_list: 'posts/group_list.html',
            self.url_profile: 'posts/profile.html',
            self.url_post_detail: 'posts/post_detail.html',
            self.url_post_create: 'posts/create_post.html',
            self.url_post_edit: "posts/create_post.html",
        }

        for reverse_name, template in templates.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)

                self.assertTemplateUsed(response, template)

    def test_index_show_correct_context(self):
        """Шаблон index.html сформирован с правильным контекстом."""
        response = self.authorized_client.get(self.url_index)
        self.assertIn('page_obj', response.context)

    def test_group_list_show_correct_context(self):
        """Шаблон group_list.html сформирован с правильным контекстом."""
        response = self.authorized_client.get(self.url_group_list)
        self.assertIn('page_obj', response.context)
        self.assertIn('group', response.context)

    def test_profile_show_correct_context(self):
        """Шаблон profile.html сформирован с правильным контекстом."""
        response = self.authorized_client.get(self.url_profile)
        self.assertIn('page_obj', response.context)
        self.assertIn('author', response.context)

    def test_post_detail_show_correct_context(self):
        """Шаблон post_detail.html сформирован с правильным контекстом."""
        response = self.authorized_client.get(self.url_post_detail)
        self.assertIn('post', response.context)

    def test_post_create_show_correct_context(self):
        """Шаблон post_create.html сформирован с правильным контекстом."""
        response = self.authorized_client.get(self.url_post_create)
        self.assertIn('form', response.context)

    def test_post_edit_show_correct_context(self):
        """Шаблон post_create.html сформирован с правильным контекстом."""
        response = self.authorized_client.get(self.url_post_edit)
        self.assertIn('form', response.context)
        self.assertIn('post_id', response.context)
        self.assertIn('is_edit', response.context)

    def test_created_posts_shows_on_different_pages(self):
        pages = (self.url_index, self.url_group_list, self.url_profile)
        for item in pages:
            with self.subTest(item=item):
                response = self.authorized_client.get(item)
                post = response.context['page_obj'][0]
                self.assertEqual(post.text, self.post.text)
                self.assertEqual(post.author.username, self.user.username)
                self.assertEqual(post.pub_date, self.post.pub_date)
                self.assertEqual(post.author, self.post.author)
                self.assertEqual(post.group, self.post.group)


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='NoUser')
        cls.group = Group.objects.create(
            title='test-group2',
            slug='test-slug2',
            description='Тестовое описание',
        )
        cls.url_index = reverse('posts:index')
        cls.url_group_list = reverse(
            'posts:group_list',
            kwargs={'slug': cls.group.slug}
        )
        cls.url_profile = reverse(
            'posts:profile', kwargs={'username': cls.user.username}
        )
        fixtures = [Post(
            text='Тестовый текст' + f'{str(i)}',
            author=cls.user,
            group=cls.group)
            for i in range(13)]
        Post.objects.bulk_create(fixtures)

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_firsts_page_contains_ten_records(self):
        pages = [self.url_index, self.url_group_list, self.url_profile]
        for item in pages:
            with self.subTest(item=item):
                response = self.authorized_client.get(item)
                self.assertEqual(len(response.context['page_obj']), 10)

    def test_second_page_contains_ten_records(self):
        pages = [self.url_index, self.url_group_list, self.url_profile]
        for item in pages:
            with self.subTest(item=item):
                response = self.authorized_client.get(item + '?page=2')
                self.assertEqual(len(response.context['page_obj']), 3)
