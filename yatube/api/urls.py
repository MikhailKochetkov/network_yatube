from django.urls import include, path

from rest_framework.authtoken import views
from rest_framework import routers

from .views import PostViewSet, GroupViewSet, CommentViewSet


router = routers.DefaultRouter()
router.register(r'posts/(?P<post_id>\d+)/comments',
                CommentViewSet,
                basename='comment')
router.register(r'posts', PostViewSet, basename='posts')
router.register(r'groups', GroupViewSet, basename='groups')

urlpatterns = [
    path('v1/api-token-auth/', views.obtain_auth_token),
    path('v1/', include(router.urls)),
]
