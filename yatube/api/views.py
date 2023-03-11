from django.shortcuts import get_object_or_404

from rest_framework import viewsets, filters
from rest_framework.permissions import (IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.pagination import LimitOffsetPagination

from posts.models import Group, Post
from likes.models import PostLike

from .serializers import (GroupSerializer,
                          PostSerializer,
                          CommentSerializer,
                          FollowSerializer,
                          LikeSerializer)
from .permissions import IsOwnerOrReadOnly
from .mixins import CreateListRetrieveViewSet


class FollowViewSet(CreateListRetrieveViewSet):
    permission_classes = [IsOwnerOrReadOnly, IsAuthenticated]
    serializer_class = FollowSerializer
    filter_backends = (filters.SearchFilter,)
    search_fields = ('user__username', 'author__username')

    def get_queryset(self):
        return self.request.user.follower.all()

    def perform_create(self, serializer):
        user = self.request.user
        serializer.save(user=user)


class GroupViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer


class PostViewSet(viewsets.ModelViewSet):
    permission_classes = [IsOwnerOrReadOnly, IsAuthenticatedOrReadOnly]
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    pagination_class = LimitOffsetPagination

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class CommentViewSet(viewsets.ModelViewSet):
    permission_classes = [IsOwnerOrReadOnly, IsAuthenticatedOrReadOnly]
    serializer_class = CommentSerializer

    def get_queryset(self):
        post = get_object_or_404(Post, id=self.kwargs.get("post_id"))
        return post.comments.all()

    def perform_create(self, serializer):
        post = get_object_or_404(Post, id=self.kwargs.get('post_id'))
        serializer.save(author=self.request.user, post=post)


class LikeViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = PostLike.objects.all()
    serializer_class = LikeSerializer
