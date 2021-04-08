from django.forms import ModelForm, Textarea

from .models import Post


class PostForm(ModelForm):
    class Meta:
        model = Post
        fields = ("group", "text", "image")
        widgets = {"text": Textarea(attrs={"placeholder": "Введите текст"})}