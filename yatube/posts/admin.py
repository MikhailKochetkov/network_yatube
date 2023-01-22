from django.contrib import admin
from .models import Post, Group, Comment


class PostAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'text',
        'pub_date',
        'author',
        'group',
    )
    list_editable = ('group',)
    search_fields = ('text',)
    list_filter = ('pub_date',)
    empty_value_display = '-пусто-'


class GroupAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'title',
        'slug',
        'description',
    )
    list_editable = ('description',)
    search_fields = ('title',)
    list_filter = ('title',)
    empty_value_display = '-пусто-'


class CommentAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'post',
        'text',
        'author',
        'created',
    )
    list_editable = ('text',)
    search_fields = ('text',)
    list_filter = ('created',)
    empty_value_display = '-пусто-'


"""
class LikeAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'post',
        'user',
        'is_like',
        'like_date',
    )
    list_editable = ('user', 'is_like', 'like_date',)
    search_fields = ('like_date', 'user',)
    list_filter = ('like_date', 'user',)
    empty_value_display = '-пусто-'
"""

admin.site.register(Post, PostAdmin)
admin.site.register(Group, GroupAdmin)
admin.site.register(Comment, CommentAdmin)
"""
admin.site.register(Like, LikeAdmin)
"""
