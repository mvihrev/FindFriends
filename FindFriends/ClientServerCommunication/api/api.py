from rest_framework import viewsets, permissions
from rest_framework.response import Response
from .serializers import *
from ..models import *
from rest_framework.decorators import action
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from drf_spectacular.utils import extend_schema, extend_schema_view


def get_is_exists(checking_username):
    try:
        is_exists = User.objects.get(username=checking_username)
    except ObjectDoesNotExist:
        is_exists = None

    return is_exists


def get_is_yourself(user, checking_user):
    return user == checking_user


def get_is_friend(user, checking_user):
    if checking_user:
        if user.pk < checking_user.pk:
            try:
                is_friend = Friendship.objects.filter(first_user=user, second_user=checking_user)
            except ObjectDoesNotExist:
                is_friend = None
        elif user.pk == checking_user.pk:
            is_friend = None
        else:
            try:
                is_friend = Friendship.objects.filter(first_user=checking_user, second_user=user)
            except ObjectDoesNotExist:
                is_friend = None
    else:
        is_friend = None

    return is_friend


@extend_schema_view(
    list=extend_schema(
        summary='Метод получения списка пользователей'
    ),
    create=extend_schema(
        summary='Метод регистрации нового пользователя'
    ),
    retrieve=extend_schema(
        summary='Метод получения пользователя по идентификатору'
    ),
    update=extend_schema(
        summary='Метод редактирования пользователя'
    ),
    partial_update=extend_schema(
        summary='Метод редактирования пользователя'
    ),
    destroy=extend_schema(
        summary='Метод удаления пользователя'
    ),
)
class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    permissions_classes = [
        permissions.AllowAny
    ]
    serializer_class = UserSerializer

    @extend_schema(summary='Метод получения всех друзей пользователя.'
                           ' Возможно удаления пользователя из списка друзей через /?delete={username}')
    @action(detail=True, methods=['get'])
    def friends(self, request, pk=None):
        user = self.get_object()
        friendships_by_user = Friendship.objects.filter(Q(first_user=user) | Q(second_user=user))
        user_friends = [i.first_user if i.first_user != user else i.second_user for i in friendships_by_user]
        user_friends_json = UserSerializer(user_friends, many=True)

        def get_queryset(self, *args, **kwargs):
            delete_param = self.request.query_params.get('delete', None)
            if delete_param:
                friend_to_delete = get_is_exists(delete_param)
                if friend_to_delete:
                    if not get_is_yourself(user, friend_to_delete):
                        friendship_status = get_is_friend(user, friend_to_delete)
                        if friendship_status:
                            friendship_status.delete()
                            return Response({'message': 'You have successfully removed this user'
                                                        ' from your friends list'})
                        else:
                            return Response({'message': 'You are not friends so you can not delete this user'})
                    else:
                        return Response({'message': 'You can not delete yourself from your friends list'})
                else:
                    return Response({'message': 'This user does not exists'})

            return Response(user_friends_json.data)

        return get_queryset(self)

    @extend_schema(summary='Метод получения всех входящих заявок в друзья.'
                           ' Возможно добавление в список друзей через /?accept={request_id} или'
                           ' отклонение заявки через /?decline={request_id}')
    @action(detail=True, methods=['get'])
    def incoming(self, request, pk=None):
        user = self.get_object()
        incoming_requests_by_user = Request.objects.filter(receiver=user, status='O')
        incoming_requests_by_user_json = RequestSerializer(incoming_requests_by_user, many=True)

        def get_queryset(self, *args, **kwargs):
            accept_param = self.request.query_params.get('accept', None)
            if accept_param:
                if accept_param.isdigit():
                    try:
                        accept_request = incoming_requests_by_user.get(id=accept_param)
                    except ObjectDoesNotExist:
                        accept_request = None
                        Response({'message': 'This request does not exist or is not incoming'})
                    if accept_request:
                        accept_request.status = 'C'
                        accept_request.save()
                        new_friendship = Friendship(first_user=user, second_user=getattr(accept_request, 'sender'))
                        new_friendship.save()
                        return Response({'message': 'You have successfully accepted a friend request'})
                    else:
                        return Response({'message': 'Not valid request id'})
                else:
                    return Response({'message': 'You must pass an integer as a request id'})

            decline_param = self.request.query_params.get('decline', None)
            if decline_param:
                if decline_param.isdigit():
                    try:
                        decline_request = incoming_requests_by_user.get(id=decline_param)
                    except ObjectDoesNotExist:
                        decline_request = None
                        Response({'message': 'This request does not exist or is not incoming'})
                    if decline_request:
                        decline_request.status = 'C'
                        decline_request.save()
                        return Response({'message': 'You have successfully declined a friend request'})
                    else:
                        return Response({'message': 'Not valid request id'})
                else:
                    return Response({'message': 'You must pass an integer as request id'})

            return Response(incoming_requests_by_user_json.data)

        return get_queryset(self)

    @extend_schema(summary='Метод получения всех исходящих заявок в друзья')
    @action(detail=True, methods=['get'])
    def outgoing(self, request, pk=None):
        user = self.get_object()
        outgoing_requests_by_user = Request.objects.filter(sender=user, status='O')
        outgoing_requests_by_user_json = RequestSerializer(outgoing_requests_by_user, many=True)

        return Response(outgoing_requests_by_user_json.data)

    @extend_schema(summary='Метод получения статуса отношений с пользователем через ?checking_user={username}')
    @action(detail=True, methods=['get'])
    def status(self, request, pk=None):
        user = self.get_object()

        def get_queryset(self, *args, **kwargs):
            checking_user_param = self.request.query_params.get('checking_user', None)

            if checking_user_param:
                checking_user = get_is_exists(checking_user_param)
                if checking_user:
                    if not get_is_yourself(user, checking_user):
                        friendship_status = get_is_friend(user, checking_user)
                        if friendship_status:
                            return Response({'message': 'You are friends'})

                        try:
                            checking_incoming = Request.objects.get(sender=checking_user, receiver=user)
                        except ObjectDoesNotExist:
                            checking_incoming = None
                        if checking_incoming:
                            return Response({'message': 'This user sent you a friend request but you have'
                                                        ' not replied to it yet'})

                        try:
                            checking_outgoing = Request.objects.get(sender=user, receiver=checking_user)
                        except ObjectDoesNotExist:
                            checking_outgoing = None
                        if checking_outgoing:
                            return Response({'message': 'You sent a friend request to this user,'
                                                        ' but he has not responded to it yet'})

                        return Response({'message': 'You are not affiliated with this user in any way'})
                    else:
                        return Response({'message': 'You are looking at the status of yourself'})
                else:
                    return Response({'message': 'This user does not exists'})

            return Response({'message': 'Specify a user to check by ?checking_user=<username>'})

        return get_queryset(self)


@extend_schema_view(
    list=extend_schema(
        summary='Метод получения списка дружеских отношений'
    ),
    create=extend_schema(
        summary='Метод создания новых дружеских отношений'
    ),
    retrieve=extend_schema(
        summary='Метод получения дружеского отношения по идентификатору'
    ),
    update=extend_schema(
        summary='Метод редактирования дружеского отношения'
    ),
    partial_update=extend_schema(
        summary='Метод редактирования дружеского отношения'
    ),
    destroy=extend_schema(
        summary='Метод удаления дружеского отношения '
    ),
)
class FriendshipViewSet(viewsets.ModelViewSet):
    queryset = Friendship.objects.all()
    permissions_classes = [
        permissions.AllowAny
    ]
    serializer_class = FriendshipSerializer


@extend_schema_view(
    list=extend_schema(
        summary='Метод получения списка запросов'
    ),
    create=extend_schema(
        summary='Метод создания нового запроса'
    ),
    retrieve=extend_schema(
        summary='Метод получения запроса по идентификатору'
    ),
    update=extend_schema(
        summary='Метод редактирования запроса'
    ),
    partial_update=extend_schema(
        summary='Метод редактирования запроса'
    ),
    destroy=extend_schema(
        summary='Метод удаления запроса'
    ),
)
class RequestViewSet(viewsets.ModelViewSet):
    queryset = Request.objects.all()
    permissions_classes = [
        permissions.AllowAny
    ]
    serializer_class = RequestSerializer
