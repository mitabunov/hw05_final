from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Group, Post

User = get_user_model()


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group = Group.objects.create(
            title="Доктор Хаус",
            slug="housemd",
        )
        cls.author = User.objects.create_user(username="G.House")
        cls.post = Post.objects.create(
            text="Если ему станет лучше, прав я. Если он умрёт — права ты.",
            author=cls.author,
            group=cls.group
        )

    def setUp(self):
        self.guest_client = Client()
        self.user = User.objects.create_user(username="AndreyG")
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_homepage(self):
        response = self.guest_client.get(reverse("index"))
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_slug_url_exists_at_desired_location(self):
        response = self.guest_client.get(
            reverse("group", kwargs={"slug": self.group.slug}))
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_user_profile(self):
        response = self.authorized_client.get(
            reverse("profile", kwargs={"username": self.author}))
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_user_post_id(self):
        response = self.guest_client.get(
            reverse("post", kwargs={
                "username": self.author,
                "post_id": self.post.id,
            }))
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_guest_user_redirect_from_edit_post(self):
        path = reverse("post_edit", kwargs={
            "username": self.author,
            "post_id": self.post.id})
        redirect_path = reverse("login") + '?next=' + path
        response = self.guest_client.get(path)
        self.assertRedirects(response, redirect_path)

    def test_post_edit_page_is_available_to_the_author(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.author)
        response = self.authorized_client.get(
            reverse("post_edit", kwargs={
                "username": self.author,
                "post_id": self.post.id}))
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_post_edit_page_is_not_available_to_the_not_author(self):
        path = reverse("post_edit", kwargs={
            "username": self.author,
            "post_id": self.post.id})
        redirect_path = reverse("post", kwargs={
            "username": self.author,
            "post_id": self.post.id,
        })
        response = self.authorized_client.get(path)
        self.assertRedirects(response, redirect_path)

    def test_new_post_url_exists_at_desired_location(self):
        response = self.authorized_client.get(reverse("new_post"))
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_new_post_url_redirect_anonymous(self):
        path = reverse("new_post")
        redirect_path = reverse("login") + "?next=" + path
        response = self.guest_client.get(path)
        self.assertRedirects(response, redirect_path)

    def test_urls_uses_correct_template(self):
        templates_url_names = {
            "index.html": reverse("index"),
            "group.html": reverse(
                "group", kwargs={"slug": self.group.slug}),
            "new_post.html": reverse("new_post"),
            "follow.html": reverse("follow_index"),
        }
        for template, reverse_name in templates_url_names.items():
            with self.subTest(template=template):
                self.authorized_client.force_login(self.author)
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_urls_uses_correct_template_edit_post(self):
        self.authorized_client.force_login(self.author)
        response = self.authorized_client.get(
            reverse("post_edit", kwargs={
                "username": self.author,
                "post_id": self.post.id})
        )
        self.assertTemplateUsed(response, "new_post.html")

    def test_page_not_found(self):
        response = self.guest_client.get(reverse("page_not_found"))
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_server_error(self):
        response = self.guest_client.get(reverse("server_error"))
        self.assertEqual(
            response.status_code, HTTPStatus.INTERNAL_SERVER_ERROR
        )
