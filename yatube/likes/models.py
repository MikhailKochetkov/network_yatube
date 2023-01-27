from django.db import models

from django.utils import timezone

from posts.models import Post, User


class PostLike(models.Model):
    post = models.ForeignKey(Post,
                             on_delete=models.CASCADE,
                             blank=True,
                             null=True)
    user = models.ForeignKey(User,
                             on_delete=models.CASCADE,
                             null=True)
    is_like = models.BooleanField(default=False)
    like_date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f'{self.user}: {self.post}  {self.is_like}'

    class Meta:
        verbose_name = 'Post Like'
        verbose_name_plural = 'Post Likes'
        ordering = ["-like_date"]


# TODO Comments likes
# class CommentLike(models.Model):
#     pass
