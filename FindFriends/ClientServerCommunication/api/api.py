from rest_framework import viewsets, permissions
from rest_framework.response import Response
from .serializers import *
from rest_framework.decorators import action
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from ..models import User, Friendship, Request


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

    @action(detail=True, methods=['get'])
    def incoming(self, request, pk=None):
        user = self.get_object()
        incoming_requests_by_user = Request.objects.filter(receiver=user, status='O')
        incoming_requests_by_user_json = RequestSerializer(incoming_requests_by_user, many=True)

        return Response(incoming_requests_by_user_json.data)

    @action(detail=True, methods=['get'])
    def outgoing(self, request, pk=None):
        user = self.get_object()
        outgoing_requests_by_user = Request.objects.filter(sender=user, status='O')
        outgoing_requests_by_user_json = RequestSerializer(outgoing_requests_by_user, many=True)

        return Response(outgoing_requests_by_user_json.data)

    @action(detail=True, methods=['get'])
    def status(self, request, pk=None):
        user = self.get_object()

        def get_queryset(self, *args, **kwargs):
            checking_user = self.request.query_params.get('checking_user', None)

            if checking_user:
                try:
                    checking_user_object = User.objects.get(username=checking_user)
                except ObjectDoesNotExist:
                    checking_user_object = None

                if checking_user_object:
                    if user.pk < checking_user_object.pk:
                        try:
                            checking_friendship = Friendship.objects.get(first_user=user,
                                                                         second_user=checking_user_object)
                        except ObjectDoesNotExist:
                            checking_friendship = None
                    elif user.pk == checking_user_object.pk:
                        return Response({'message': 'You are looking at the status of yourself'})
                    else:
                        try:
                            checking_friendship = Friendship.objects.get(first_user=checking_user_object,
                                                                         second_user=user)
                        except ObjectDoesNotExist:
                            checking_friendship = None

                    if checking_friendship:
                        return Response({'message': 'You are friends'})

                    try:
                        checking_incoming = Request.objects.get(sender=checking_user_object, receiver=user)
                    except ObjectDoesNotExist:
                        checking_incoming = None
                    if checking_incoming:
                        return Response({'message': 'This user sent you a friend request but you have'
                                                    ' not replied to it yet'})

                    try:
                        checking_outgoing = Request.objects.get(sender=user, receiver=checking_user_object)
                    except ObjectDoesNotExist:
                        checking_outgoing = None
                    if checking_outgoing:
                        return Response({'message': 'You sent a friend request to this user,'
                                                    ' but he has not responded to it yet'})

                    return Response({'message': 'You are not affiliated with this user in any way'})
                else:
                    return Response({'message': 'This user dose not exists'})

            return Response({'message': 'Specify a user to check by ?checking_user=<user_to_check>'})

        return get_queryset(self)


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
