import shutil
import tempfile

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Group, Post

User = get_user_model()


class FormsTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        settings.MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)
        cls.group = Group.objects.create(
            title="test-title",
            slug="test-slug",
        )
        cls.author = User.objects.create_user(username="Nikolay")

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

    def setUp(self):
        self.small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        self.uploaded = SimpleUploadedFile(
            name='small.gif',
            content=self.small_gif,
            content_type='image/gif'
        )
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.author)

    def test_guest_user_cant_create_new_post(self):
        posts_count = Post.objects.count()
        form_data = {
            "group": FormsTests.group,
            "text": "Тестовый текст гостя",
        }
        response = self.guest_client.post(
            reverse("new_post"), data=form_data, follow=True
        )
        reference = reverse("login") + "?next=" + reverse("new_post")
        self.assertRedirects(response, reference)
        self.assertEqual(Post.objects.count(), posts_count)

    def test_authorised_user_new_post(self):
        posts_count = Post.objects.count()
        form_data = {
            "group": FormsTests.group.id,
            "text": "Добавленный пост",
            "image": self.uploaded,
        }
        response = self.authorized_client.post(
            reverse("new_post"),
            data=form_data,
            follow=True
        )
        new_post = Post.objects.last()
        self.assertRedirects(response, reverse("index"))
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertEqual(new_post.group, FormsTests.group)
        self.assertEqual(new_post.text, form_data["text"])
        self.assertEqual(new_post.author, self.author)
        self.assertTrue(new_post.image)

    def test_author_can_edit_post(self):
        post = Post.objects.create(
            text="Текст для теста",
            author=self.author,
            group=FormsTests.group,
        )
        posts_count = Post.objects.count()
        form_data = {
            "group": FormsTests.group.id,
            "text": "Измененный текст",
            "image": self.uploaded,
        }
        response = self.authorized_client.post(
            reverse("post_edit",
                    kwargs={"username": self.author.username,
                            "post_id": post.id}),
            data=form_data,
            follow=True
        )
        self.assertRedirects(
            response,
            reverse("post",
                    kwargs={"username": self.author.username,
                            "post_id": post.id})
        )
        modified_post = Post.objects.last()
        self.assertEqual(Post.objects.count(), posts_count)
        self.assertEqual(modified_post.group, FormsTests.group)
        self.assertEqual(modified_post.text, form_data["text"])
        self.assertEqual(modified_post.author, self.author)
        self.assertEqual(modified_post.image.name, "posts/small.gif")