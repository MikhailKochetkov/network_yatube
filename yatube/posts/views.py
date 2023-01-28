from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.conf import settings

from .models import Post, Group, User, Follow
from .forms import PostForm, CommentForm


def page_paginator(request, obj):
    """
    Пагинатор для страниц.
    """
    paginator = Paginator(obj, settings.POSTS_ON_PAGE)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return page_obj


def index(request):
    """
    Главная страница.
    """
    posts = Post.objects.all()
    context = {
        'page_obj': page_paginator(request, posts),
    }
    return render(request, 'posts/index.html', context)


def group_posts(request, slug):
    """
    Страница постов группы.
    """
    group = get_object_or_404(Group, slug=slug)
    grp_posts = group.posts.all()
    context = {
        'group': group,
        'page_obj': page_paginator(request, grp_posts),
    }
    return render(request, 'posts/group_list.html', context)


def profile(request, username):
    """
    Страница профайла пользователя.
    """
    profile_user = get_object_or_404(User, username=username)
    profile_posts = profile_user.posts.all()
    following = (request.user.is_authenticated
                 and Follow.objects.filter(user=request.user,
                                           author=profile_user).exists())
    context = {
        'profile': profile_user,
        'page_obj': page_paginator(request, profile_posts),
        'following': following,
    }
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    """
    Страница поста.
    """
    post = get_object_or_404(Post, id=post_id)
    comments = post.comments.all()
    comment_form = CommentForm()
    context = {
        'post': post,
        'form': comment_form,
        'comments': comments,
    }
    return render(request, 'posts/post_detail.html', context)


@login_required
def post_create(request):
    """
    Страница создания поста.
    """
    form = PostForm(request.POST or None,
                    files=request.FILES or None)
    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect('posts:profile', request.user)
    context = {
        'form': form,
    }
    return render(request, 'posts/create_post.html', context)


@login_required
def post_edit(request, post_id):
    """
    Страница редактирования поста.
    """
    edit_post = get_object_or_404(Post, id=post_id)
    edit_form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=edit_post
    )
    if edit_post.author != request.user:
        return redirect('posts:post_detail', post_id)
    if edit_form.is_valid():
        edit_form.save()
        return redirect('posts:post_detail', post_id)
    context = {
        'form': edit_form,
        'post': edit_post,
        'is_edit': True,
    }
    return render(request, 'posts/create_post.html', context)


@login_required
def add_comment(request, post_id):
    comment_post = get_object_or_404(Post, id=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = comment_post
        comment.save()
    return redirect('posts:post_detail', post_id=post_id)


@login_required
def follow_index(request):
    posts = Post.objects.filter(author__following__user=request.user)
    context = {
        'page_obj': page_paginator(request, posts)
    }
    return render(request, 'posts/follow.html', context)


@login_required
def profile_follow(request, username):
    author = get_object_or_404(User, username=username)
    user = request.user
    if author != user:
        Follow.objects.get_or_create(user=user, author=author)
    return redirect('posts:profile', username=username)


@login_required
def profile_unfollow(request, username):
    user = request.user
    Follow.objects.filter(user=user, author__username=username).delete()
    return redirect('posts:profile', username=username)
