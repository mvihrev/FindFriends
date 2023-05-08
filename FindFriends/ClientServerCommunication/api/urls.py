from rest_framework import routers
from .api import UserViewSet, FriendshipViewSet, RequestViewSet

router = routers.DefaultRouter()

router.register('api/users', UserViewSet, 'users')
router.register('api/friendships', FriendshipViewSet, 'friendships')
router.register('api/requests', RequestViewSet, 'requests')

urlpatterns = router.urls
