"""
Posts URLs.
"""

from django.urls import include, path

from rest_framework.routers import DefaultRouter

from posts.views import (
    CommentViewSet,
    LikeViewSet,
    LocationViewSet,
    PollViewSet,
    PostViewSet,
)

router = DefaultRouter()
router.register(r"posts", PostViewSet, basename="post")
router.register(r"comments", CommentViewSet, basename="comment")
router.register(r"likes", LikeViewSet, basename="like")
router.register(r"polls", PollViewSet, basename="poll")
router.register(r"locations", LocationViewSet, basename="location")

urlpatterns = [
    path("", include(router.urls)),
]
