"""
Users URLs.
"""

from django.urls import include, path

from rest_framework.routers import DefaultRouter

from users.views import FollowViewSet, UserViewSet

router = DefaultRouter()
router.register(r"users", UserViewSet, basename="user")
router.register(r"follows", FollowViewSet, basename="follow")

urlpatterns = [
    path("", include(router.urls)),
]
