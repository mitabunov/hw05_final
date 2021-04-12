from django.contrib.auth import get_user_model
from django.test import TestCase

from posts.models import Group, Post

User = get_user_model()


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username="J.Tribbiani")
        cls.group = Group.objects.create(title="Friends")
        cls.post = Post.objects.create(
            text="Everybody needs Friends!",
            author=cls.author,
            group=cls.group,
        )

    def test_verbose_name(self):
        post = PostModelTest.post
        group = PostModelTest.group
        fields = {
            post._meta.get_field("text"): "Текст",
            group._meta.get_field("title"): "Группа"
        }
        for field, expected in fields.items():
            with self.subTest(field=field):
                value = field.verbose_name
                self.assertEqual(value, expected)

    def test_help_text(self):
        post = PostModelTest.post
        group = PostModelTest.group
        fields = {
            post._meta.get_field("text"): "Введите текст вашего сообщения",
            group._meta.get_field("title"): "Название группы"
        }
        for field, expected in fields.items():
            with self.subTest(field=field):
                value = field.help_text
                self.assertEqual(value, expected)

    def test_object_name(self):
        post = PostModelTest.post
        group = PostModelTest.group
        fields = {
            post: post.text[:15],
            group: group.title
        }
        for expected, value in fields.items():
            with self.subTest(expected=str(expected)):
                self.assertEqual(value, str(expected))
