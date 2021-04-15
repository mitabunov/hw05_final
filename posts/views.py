from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render

from yatube.settings import POSTS_PER_PAGE

from .forms import CommentForm, PostForm
from .models import Follow, Group, Post

User = get_user_model()


def index(request):
    latest = Post.objects.all()
    paginator = Paginator(latest, POSTS_PER_PAGE)
    page_number = request.GET.get("page")
    page = paginator.get_page(page_number)
    return render(request, "index.html", {"page": page})


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.all()
    paginator = Paginator(posts, POSTS_PER_PAGE)
    page_number = request.GET.get("page")
    page = paginator.get_page(page_number)
    return render(request, "group.html", {"group": group, "page": page})


@login_required
def new_post(request):
    form = PostForm(request.POST or None, request.FILES or None)
    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect("index")
    return render(request, "new_post.html", {"form": form})


def profile(request, username):
    author = get_object_or_404(User, username=username)
    post_list = author.posts.all()
    paginator = Paginator(post_list, POSTS_PER_PAGE)
    page_number = request.GET.get("page")
    page = paginator.get_page(page_number)
    is_not_author = False
    following = False
    if request.user.is_authenticated:
        is_not_author = author != request.user
        following = author.following.filter(user=request.user)
    return render(request, "profile.html", {"page": page,
                                            "author": author,
                                            "following": following,
                                            "is_not_author": is_not_author})


def post_view(request, username, post_id):
    post = get_object_or_404(Post, id=post_id, author__username=username)
    author = post.author
    form = CommentForm()
    comments = post.comments.all()
    return render(request, 'post.html', {"post": post,
                                         "author": author,
                                         "form": form,
                                         "comments": comments})


@login_required
def post_edit(request, username, post_id):
    post = get_object_or_404(Post, id=post_id, author__username=username)
    if request.user != post.author:
        return redirect("post", username=username, post_id=post_id)
    form = PostForm(request.POST or None,
                    files=request.FILES or None,
                    instance=post)
    if form.is_valid():
        form.save()
        return redirect("post", username=username, post_id=post_id)
    return render(request, 'new_post.html', {"post": post,
                                             "form": form})


@login_required
def add_comment(request, username, post_id):
    post = get_object_or_404(Post, id=post_id, author__username=username)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect("post", username=username, post_id=post_id)


def page_not_found(request, exception=None):
    return render(
        request, "misc/404.html", {"path": request.path}, status=404
    )


def server_error(request):
    return render(request, "misc/500.html", status=500)


@login_required
def follow_index(request):
    post_list = Post.objects.filter(author__following__user=request.user)
    paginator = Paginator(post_list, POSTS_PER_PAGE)
    page_number = request.GET.get("page")
    page = paginator.get_page(page_number)
    return render(request, "follow.html", {"page": page})


@login_required
def profile_follow(request, username):
    author = get_object_or_404(User, username=username)
    follow_now = Follow.objects.filter(
        user=request.user, author=author).exists()
    if not follow_now and author != request.user:
        Follow.objects.create(user=request.user, author=author)
    return redirect("profile", username=username)


@login_required
def profile_unfollow(request, username):
    database_entry = get_object_or_404(
        Follow, author__username=username, user=request.user)
    if database_entry.exists():
        database_entry.delete()
    return redirect("profile", username=username)
