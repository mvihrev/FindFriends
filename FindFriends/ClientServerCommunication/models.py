from django.db import models, IntegrityError
from rest_framework import serializers


class User(models.Model):
    username = models.CharField(max_length=32, primary_key=True)


class Friendship(models.Model):
    class Meta:
        unique_together = ('first_user', 'second_user')

    first_user = models.ForeignKey(User, related_name='%(app_label)s_%(class)s_first_user', on_delete=models.CASCADE)
    second_user = models.ForeignKey(User, related_name='%(app_label)s_%(class)s_second_user', on_delete=models.CASCADE)

    def clean(self):
        if self.first_user == self.second_user:
            response = serializers.ValidationError({'message': 'You can not add yourself as a friend'})
            response.status_code = 200

            raise response

    def save(self, *args, **kwargs):
        self.clean()

        if self.first_user.pk > self.second_user.pk:
            self.first_user, self.second_user = self.second_user, self.first_user

        super(Friendship, self).save(*args, **kwargs)


class Request(models.Model):
    class Status(models.TextChoices):
        open = 'O', 'Open'
        closed = 'C', 'Closed'

    sender = models.ForeignKey(User, related_name='%(app_label)s_%(class)s_sender', on_delete=models.CASCADE)
    receiver = models.ForeignKey(User, related_name='%(app_label)s_%(class)s_receiver', on_delete=models.CASCADE)
    status = models.CharField(max_length=1, choices=Status.choices, default='O')

    def clean(self):
        if self.sender == self.receiver:
            response = serializers.ValidationError({'message': 'You can not send request to yourself'})
            response.status_code = 200

            raise response

    def save(self, *args, **kwargs):
        self.clean()

        first_user = self.sender
        second_user = self.receiver
        if first_user.pk > second_user.pk:
            first_user, second_user = second_user, first_user

        already_friends = Friendship.objects.filter(first_user=first_user, second_user=second_user)
        if already_friends.exists():
            response = serializers.ValidationError({'message': 'You are already friends'})
            response.status_code = 200

            raise response

        reverse = Request.objects.filter(sender=self.receiver, receiver=self.sender)
        if reverse.exists():
            self.status = 'C'
            reverse.update(status='C')
            Friendship.objects.create(first_user=self.sender, second_user=self.receiver)

        super(Request, self).save(*args, **kwargs)

