from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render

# from django.views.decorators.cache import cache_page
from yatube.settings import POSTS_PER_PAGE

from .forms import CommentForm, PostForm
from .models import Follow, Group, Post

User = get_user_model()


# @cache_page(20)
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
    auth = request.user.is_authenticated
    check_follow = Follow.objects.filter(user=request.user,
                                         author__username=username
                                         ).exists()
    following = auth and check_follow
    return render(request, "profile.html", {"page": page,
                                            "author": author,
                                            "following": following})


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
    __import__("pdb").set_trace()
    following_list = get_object_or_404(Follow, user=request.user)
    following = [author.author.id for author in following_list]
    post_list = get_object_or_404(Post, author__in=following)
    paginator = Paginator(post_list, POSTS_PER_PAGE)
    page_number = request.GET.get("page")
    page = paginator.get_page(page_number)
    __import__("pdb").set_trace()
    return render(request, "follow.html", {"page": page})


@login_required
def profile_follow(request, username):
    author = get_object_or_404(User, username=username)
    if not Follow.objects.filter(user=request.user, author=author).exists():
        Follow.objects.create(user=request.user, author=author)
    return redirect("profile", username=username)


@login_required
def profile_unfollow(request, username):
    author = get_object_or_404(User, username=username)
    if Follow.objects.filter(user=request.user, author=author).exists():
        Follow.objects.filter(user=request.user, author=author).delete()
    return redirect("profile", username=username)
