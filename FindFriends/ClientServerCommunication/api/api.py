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
