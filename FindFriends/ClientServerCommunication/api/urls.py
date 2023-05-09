from rest_framework import routers
from .api import UserViewSet, FriendshipViewSet, RequestViewSet

router = routers.DefaultRouter()

router.register('users', UserViewSet, 'users')
router.register('friendships', FriendshipViewSet, 'friendships')
router.register('requests', RequestViewSet, 'requests')

urlpatterns = router.urls
