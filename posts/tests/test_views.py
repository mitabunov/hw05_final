import shutil
import tempfile

from django import forms
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from posts.models import Follow, Group, Post
from yatube.settings import POSTS_PER_PAGE

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)

User = get_user_model()


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostViewTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        small_gif = (
            b"\x47\x49\x46\x38\x39\x61\x02\x00"
            b"\x01\x00\x80\x00\x00\x00\x00\x00"
            b"\xFF\xFF\xFF\x21\xF9\x04\x00\x00"
            b"\x00\x00\x00\x2C\x00\x00\x00\x00"
            b"\x02\x00\x01\x00\x00\x02\x02\x0C"
            b"\x0A\x00\x3B"
        )
        uploaded = SimpleUploadedFile(
            name="small.gif",
            content=small_gif,
            content_type="image/gif"
        )
        cls.group = Group.objects.create(
            title="Остаться в живых",
            slug="lost",
        )
        cls.author = User.objects.create_user(username="J.Locke")
        cls.user = User.objects.create_user(username="B.Linus")
        cls.post = Post.objects.create(
            text="Только я знаю, что я могу.",
            author=cls.author,
            group=cls.group,
            image=uploaded,
        )

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)
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
        self.assertEqual(post.image, "posts/small.gif")

    def test_pages_use_correct_template(self):
        templates_pages_names = {
            "index.html": reverse("index"),
            "new_post.html": reverse("new_post"),
            "group.html": (
                reverse("group", kwargs={"slug": self.group.slug})
            ),
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
        response_profile = self.authorized_client.get(
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
            "image": forms.fields.ImageField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context["form"].fields[value]
                self.assertIsInstance(form_field, expected)

    def test_edit_post_shows_correct_context(self):
        response = self.authorized_client.get(
            reverse("post_edit",
                    kwargs={"username": self.author,
                            "post_id": self.post.id}))
        form_fields = {
            "text": forms.fields.CharField,
            "image": forms.fields.ImageField,
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

    def test_cache_index(self):
        response_1 = self.authorized_client.get(reverse("index"))
        Post.objects.create(text="Test cache", author=self.author)
        response_2 = self.authorized_client.get(reverse("index"))
        self.assertEqual(
            response_1.content, response_2.content)
        cache.clear()
        response_3 = self.authorized_client.get(reverse("index"))
        self.assertNotEqual(response_2.content, response_3.content)

    def test_follow_feature(self):
        self.user_client = Client()
        self.user_client.force_login(self.user)
        follow_count = Follow.objects.count()
        response = self.user_client.get(
            reverse("profile_follow", kwargs={
                "username": self.author})
        )
        new_follow = Follow.objects.first()
        self.assertRedirects(response, reverse("profile", kwargs={
            "username": self.author})
        )
        self.assertEqual(Follow.objects.count(), follow_count + 1)
        self.assertEqual(new_follow.author, self.author)
        self.assertEqual(new_follow.user, self.user)

    def test_unfollow_feature(self):
        self.user_client = Client()
        self.user_client.force_login(self.user)
        Follow.objects.create(user=self.user, author=self.author)
        follow_count = Follow.objects.count()
        response = self.user_client.get(
            reverse("profile_unfollow", kwargs={
                "username": self.author})
        )
        self.assertRedirects(response, reverse("profile", kwargs={
            "username": self.author})
        )
        self.assertEqual(Follow.objects.count(), follow_count - 1)

    def test_post_visible_for_follower(self):
        Follow.objects.create(user=self.user, author=self.author)
        self.authorized_client.force_login(self.user)
        response = self.authorized_client.get(reverse("follow_index"))
        self.check_post(response)

    def test_post_invisible_for_a_non_follower(self):
        Follow.objects.create(user=self.user, author=self.author)
        non_follower = User.objects.create_user(username="SpongeBob")
        self.authorized_client.force_login(non_follower)
        response = self.authorized_client.get(reverse("follow_index"))
        self.assertEqual(response.context["page"].paginator.count, 0)
