import shutil
import tempfile

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Comment, Group, Post

User = get_user_model()


class FormsTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        settings.MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)
        cls.group = Group.objects.create(
            title="Теория Большого взрыва",
            slug="the-big-bang-theory",
        )
        cls.author = User.objects.create_user(username="S.Cooper")
        cls.post = Post.objects.create(
            text="Я не сумасшедший. Моя мамуля меня проверяла.",
            author=cls.author,
            group=FormsTests.group,
        )

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.author)

    def test_guest_user_cant_create_new_post(self):
        posts_count = Post.objects.count()
        form_data = {
            "group": FormsTests.group,
            "text": "Barry Kripke was here",
        }
        response = self.guest_client.post(
            reverse("new_post"), data=form_data, follow=True
        )
        reference = reverse("login") + "?next=" + reverse("new_post")
        self.assertRedirects(response, reference)
        self.assertEqual(Post.objects.count(), posts_count)

    def test_authorised_user_new_post(self):
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
        posts_count = Post.objects.count()
        form_data = {
            "group": FormsTests.group.id,
            "text": "Спокойной ночи, жалкий человечишка!",
            "image": self.uploaded,
        }
        response = self.authorized_client.post(
            reverse("new_post"),
            data=form_data,
            follow=True
        )
        new_post = Post.objects.first()
        self.assertRedirects(response, reverse("index"))
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertEqual(new_post.group, FormsTests.group)
        self.assertEqual(new_post.text, form_data["text"])
        self.assertEqual(new_post.author, self.author)
        self.assertTrue(new_post.image)

    def test_author_can_edit_post(self):
        posts_count = Post.objects.count()
        form_data = {
            "group": FormsTests.group.id,
            "text": "Ненавижу эту планету!",
        }
        response = self.authorized_client.post(
            reverse("post_edit",
                    kwargs={"username": self.author.username,
                            "post_id": self.post.id}),
            data=form_data,
            follow=True
        )
        self.assertRedirects(
            response,
            reverse("post",
                    kwargs={"username": self.author.username,
                            "post_id": self.post.id})
        )
        modified_post = Post.objects.first()
        self.assertEqual(Post.objects.count(), posts_count)
        self.assertEqual(modified_post.group, FormsTests.group)
        self.assertEqual(modified_post.text, form_data["text"])
        self.assertEqual(modified_post.author, self.author)

    def test_guest_user_cant_comment_post(self):
        comments_count = Comment.objects.count()
        form_data = {
            "text": "Ах ты, гравитация, бессердечная ты сука!",
        }
        response = self.guest_client.post(
            reverse("add_comment", kwargs={
                "username": self.author,
                "post_id": self.post.id
            }),
            data=form_data,
            follow=True
        )
        reference = reverse("login") + "?next=" + reverse(
            "add_comment",
            kwargs={
                "username": self.author,
                "post_id": self.post.id
            })
        self.assertRedirects(response, reference)
        self.assertEqual(Comment.objects.count(), comments_count)

    def test_authorised_user_can_comment_post(self):
        comments_count = Comment.objects.count()
        form_data = {
            "text": "Бугагашенька!",
        }
        response = self.authorized_client.post(
            reverse("add_comment", kwargs={
                "username": self.author,
                "post_id": self.post.id
            }),
            data=form_data,
            follow=True
        )
        new_comment = Comment.objects.first()
        self.assertRedirects(response, reverse(
            "post", kwargs={
                "username": self.author,
                "post_id": self.post.id
            }))
        self.assertEqual(Comment.objects.count(), comments_count + 1)
        self.assertEqual(new_comment.text, form_data["text"])
        self.assertEqual(new_comment.author, self.author)
