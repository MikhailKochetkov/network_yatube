from django.urls import path, include

from .views import AddLikeView, RemoveLikeView


app_name = 'likes'

urlpatterns = [
    path('likes/', include([
        path('add/', AddLikeView.as_view(), name='add'),
        path('remove/', RemoveLikeView.as_view(), name='remove'),
    ])),
]
