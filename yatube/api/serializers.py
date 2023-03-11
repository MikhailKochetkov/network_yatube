from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from posts.models import Group, Post, Comment, Follow, User
from likes.models import PostLike


class LikeSerializer(serializers.ModelSerializer):
    post = serializers.PrimaryKeyRelatedField(read_only=True)
    count_likes = serializers.SerializerMethodField()

    class Meta:
        model = PostLike
        fields = ('id', 'post', 'count_likes')

    def get_count_likes(self, obj):
        return PostLike.objects.filter(post__id=obj.post.id).count()


class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ('id', 'title', 'slug', 'description')


class PostSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True
    )

    class Meta:
        model = Post
        fields = ('id', 'text', 'author', 'image', 'group', 'pub_date')


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True
    )
    post = serializers.ReadOnlyField(source='post.id')

    class Meta:
        model = Comment
        fields = ('id', 'author', 'post', 'text', 'created')


class FollowSerializer(serializers.ModelSerializer):
    user = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True,
        default=serializers.CurrentUserDefault())
    following = serializers.SlugRelatedField(
        slug_field='username',
        queryset=User.objects.all())

    class Meta:
        model = Follow
        fields = ('id', 'user', 'author')
        validators = [
            UniqueTogetherValidator(
                queryset=Follow.objects.all(),
                fields=('user', 'author')
            )
        ]

    def validate(self, data):
        if data['author'] == self.context['request'].user:
            raise serializers.ValidationError(
                'Нельзя подписаться на самого себя'
            )
        return data
