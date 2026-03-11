"""
Posts URLs.
"""

from django.urls import include, path

from rest_framework.routers import DefaultRouter

from posts.views import (
    HashtagViewSet,
    LikeViewSet,
    LocationViewSet,
    NotificationViewSet,
    PollViewSet,
    PostViewSet,
    SearchViewSet,
)

router = DefaultRouter()
router.register(r"posts", PostViewSet, basename="post")
router.register(r"likes", LikeViewSet, basename="like")
router.register(r"polls", PollViewSet, basename="poll")
router.register(r"locations", LocationViewSet, basename="location")
router.register(r"hashtags", HashtagViewSet, basename="hashtag")
router.register(r"notifications", NotificationViewSet, basename="notification")
router.register(r"search", SearchViewSet, basename="search")

urlpatterns = [
    path("", include(router.urls)),
]
