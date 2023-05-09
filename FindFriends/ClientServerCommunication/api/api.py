from rest_framework import viewsets, permissions
from rest_framework.response import Response
from rest_framework.decorators import action
from django.db.models import Q
from ..models import User, Friendship, Request
from .serializers import UserSerializer, FriendshipSerializer, RequestSerializer


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    permissions_classes = [
        permissions.AllowAny
    ]
    serializer_class = UserSerializer

    @action(detail=True, methods=['get'])
    def friends(self, request, pk=None):
        user = self.get_object()
        friendships_by_user = Friendship.objects.filter(Q(first_user=user) | Q(second_user=user))
        user_friends = [i.first_user if i.first_user != user else i.second_user for i in friendships_by_user]
        user_friends_json = UserSerializer(user_friends, many=True)

        return Response(user_friends_json .data)


class FriendshipViewSet(viewsets.ModelViewSet):
    queryset = Friendship.objects.all()
    permissions_classes = [
        permissions.AllowAny
    ]
    serializer_class = FriendshipSerializer


class RequestViewSet(viewsets.ModelViewSet):
    queryset = Request.objects.all()
    permissions_classes = [
        permissions.AllowAny
    ]
    serializer_class = RequestSerializer
