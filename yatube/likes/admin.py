from django.contrib import admin
from .models import PostLike


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


admin.site.register(PostLike, LikeAdmin)
