from django.db import models


class User(models.Model):
    username = models.CharField(max_length=32, primary_key=True)


class Friendship(models.Model):
    class Meta:
        unique_together = ('first_user', 'second_user')

    first_user = models.ForeignKey(User, related_name='%(app_label)s_%(class)s_first_user', on_delete=models.CASCADE)
    second_user = models.ForeignKey(User, related_name='%(app_label)s_%(class)s_second_user', on_delete=models.CASCADE)

    def save(self, *args, **kwargs):
        if self.first_user.id > self.second_user.id:
            self.first_user, self.second_user = self.second_user, self.first_user

        super(Friendship, self).save(*args, **kwargs)


class Request(models.Model):
    class Status(models.TextChoices):
        open = 'O', 'Open'
        closed = 'C', 'Closed'

    sender = models.ForeignKey(User, related_name='%(app_label)s_%(class)s_sender', on_delete=models.CASCADE)
    receiver = models.ForeignKey(User, related_name='%(app_label)s_%(class)s_receiver', on_delete=models.CASCADE)
    status = models.CharField(max_length=1, choices=Status.choices, default='O')

    def save(self, *args, **kwargs):
        reverse = Request.objects.filter(sender=self.reciver, reciver=self.sender)
        if reverse.exists():
            self.status = 'C'
            reverse.update(status='C')
            Friendship.objects.create(first_user=self.sender, second_user=self.receiver)

        super(Request, self).save(*args, **kwargs)
