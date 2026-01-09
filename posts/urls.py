"""
Posts URLs.
"""

from django.urls import include, path

from rest_framework.routers import DefaultRouter

from posts.views import CommentViewSet, LikeViewSet, PostViewSet

router = DefaultRouter()
router.register(r"posts", PostViewSet, basename="post")
router.register(r"comments", CommentViewSet, basename="comment")
router.register(r"likes", LikeViewSet, basename="like")

urlpatterns = [
    path("", include(router.urls)),
]
