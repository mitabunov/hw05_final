from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Group(models.Model):
    title = models.CharField(verbose_name="Группа",
                             max_length=200,
                             help_text="Название группы")
    slug = models.SlugField(unique=True)
    description = models.TextField()

    def __str__(self):
        return self.title


class Post(models.Model):
    text = models.TextField("Текст",
                            help_text="Введите текст вашего сообщения")
    pub_date = models.DateTimeField("Дата публикации", auto_now_add=True)
    author = models.ForeignKey(User,
                               on_delete=models.CASCADE,
                               related_name="posts",
                               verbose_name="Автор")
    group = models.ForeignKey(Group,
                              on_delete=models.SET_NULL,
                              blank=True,
                              null=True,
                              related_name="posts",
                              verbose_name="Группа",
                              help_text="Название группы")
    image = models.ImageField(verbose_name="Изображение",
                              help_text="Прикрепите изображение",
                              upload_to="posts/",
                              blank=True,
                              null=True)

    class Meta:
        ordering = ["-pub_date"]

    def __str__(self):
        return self.text[:15]


class Comment(models.Model):
    text = models.TextField("Комментарий",
                            help_text="Введите текст вашего сообщения")
    created = models.DateTimeField("Дата комментария", auto_now_add=True)
    author = models.ForeignKey(User,
                               on_delete=models.CASCADE,
                               related_name="comments",
                               verbose_name="Автор")
    post = models.ForeignKey(Post,
                             on_delete=models.CASCADE,
                             related_name="comments")

    class Meta:
        ordering = ["-created"]

    def __str__(self):
        return self.text[:15]


class Follow(models.Model):
    user = models.ForeignKey(User,
                             on_delete=models.CASCADE,
                             related_name="follower",
                             verbose_name="Подписчик")
    author = models.ForeignKey(User,
                               on_delete=models.CASCADE,
                               related_name="following",
                               verbose_name="Автор")

    class Meta:
        ordering = ["-user"]
        constraints = [
            models.UniqueConstraint(
                fields=["user", "author"], name="unique_following")
        ]

    def __str__(self):
        return f'{self.user} -> {self.author}'
