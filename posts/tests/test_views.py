import shutil
import tempfile

from django import forms
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Group, Post
from yatube.settings import POSTS_PER_PAGE

User = get_user_model()


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        settings.MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)
        cls.small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        cls.uploaded = SimpleUploadedFile(
            name='small.gif',
            content=cls.small_gif,
            content_type='image/gif'
        )
        cls.group = Group.objects.create(
            title="test-title",
            slug="test-slug",
        )
        cls.author = User.objects.create_user(username="Nikolay")
        cls.post = Post.objects.create(
            text="Текст для теста, больше 15 символов",
            author=cls.author,
            group=cls.group,
            image=cls.uploaded,
        )

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.author)

    def check_post(self, response):
        if "page" in response.context:
            post = response.context["page"][0]
        else:
            post = response.context["post"]
        self.assertEqual(post.id, self.post.id)
        self.assertEqual(post.author, self.post.author)
        self.assertEqual(post.text, self.post.text)
        self.assertEqual(post.group, self.post.group)
        self.assertEqual(post.image.name, 'posts/small.gif')

    def test_pages_use_correct_template(self):
        templates_pages_names = {
            "index.html": reverse("index"),
            "new_post.html": reverse("new_post"),
            "group.html": (
                reverse("group", kwargs={"slug": self.group.slug})
            ),
            "misc/404.html": reverse("page_not_found"),
            "misc/500.html": reverse("server_error"),
        }
        for template, reverse_name in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_home_page_shows_correct_context(self):
        response = self.authorized_client.get(reverse("index"))
        self.check_post(response)

    def test_group_page_show_correct_context(self):
        response_group = self.authorized_client.get(
            reverse("group", kwargs={"slug": self.group.slug})
        )
        self.assertEqual(
            response_group.context["group"], self.group)
        self.check_post(response_group)

    def test_profile_page_show_correct_context(self):
        response_profile = self.guest_client.get(
            reverse("profile", kwargs={"username": self.author})
        )
        self.check_post(response_profile)

    def test_post_view_page_show_correct_context(self):
        response_post_view = self.guest_client.get(
            reverse("post", kwargs={"username": self.author,
                                    "post_id": self.post.id})
        )
        self.check_post(response_post_view)

    def test_new_post_shows_correct_context(self):
        response = self.authorized_client.get(reverse("new_post"))
        form_fields = {
            "text": forms.fields.CharField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context["form"].fields[value]
                self.assertIsInstance(form_field, expected)

    def test_edit_post_shows_correct_context(self):
        self.authorized_client.force_login(self.author)
        response = self.authorized_client.get(
            reverse("post_edit",
                    kwargs={"username": self.author,
                            "post_id": self.post.id}))
        form_fields = {
            "text": forms.fields.CharField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context["form"].fields[value]
                self.assertIsInstance(form_field, expected)

    def test_first_page_containse_ten_records(self):
        objs = [Post(text="Test", author=self.author) for obj in range(12)]
        Post.objects.bulk_create(objs)
        response = self.guest_client.get(reverse("index"))
        self.assertEqual(len(response.context.get(
            "page").object_list), POSTS_PER_PAGE)

    def test_second_page_containse_three_records(self):
        objs = (Post(text="Test", author=self.author) for obj in range(12))
        Post.objects.bulk_create(objs)
        response = self.guest_client.get(reverse("index") + "?page=2")
        self.assertEqual(len(response.context.get("page").object_list), 3)