from django.shortcuts import redirect
from django.views.generic import View

from posts.models import Post, User
from .models import PostLike


class AddLikeView(View):
    def post(self, request):
        post_id = int(request.POST.get('post_id'))
        user_id = int(request.POST.get('user_id'))
        url_from = request.POST.get('url_from')
        user_inst = User.objects.get(id=user_id)
        post_inst = Post.objects.get(id=post_id)
        try:
            like_inst = PostLike.objects.get(post=post_inst, user=user_inst)
        except Exception as e:
            post_like = PostLike(post=post_inst,
                                 user=user_inst,
                                 is_like=True)
            post_like.save()
        return redirect(url_from)


class RemoveLikeView(View):
    def post(self, request):
        likes_id = int(request.POST.get('post_likes_id'))
        url_from = request.POST.get('url_from')
        post_like = PostLike.objects.get(id=likes_id)
        post_like.delete()
        return redirect(url_from)
