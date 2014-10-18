from django.db import models
from django.contrib.auth.models import User
# Create your models here.

class UserProfile(models.Model):
    user = models.OneToOneField(User)
    nickname = models.CharField(max_length=128)
    comment = models.TextField()
    country = models.CharField(max_length=128, blank=True)
    url = models.CharField(max_length=128, blank=True)
    ignores = models.ManyToManyField(User, related_name='ignore_set', blank=True, null=True)

    def __unicode__(self):
        return "%s" % self.user

    def serialize(self):
        data = {
            'user': self.user_id,
            'username': self.user.username,
            'nickname': self.nickname,
            'comment': self.comment,
            'country': self.country,
            'url': self.url,
            'ignores':[],
        }
        return data

class Message(models.Model):
    user = models.ForeignKey(User)
    message = models.CharField(max_length=128)
    created = models.DateTimeField(auto_now_add=True)
    def serialize(self):
        data = {
            'id': self.id,
            'user': self.user_id,
            'username': self.user.username,
            'liked': self.like_set.count(),
            'message': self.message,
            'created': self.created.ctime()
        }
        return data

class Like(models.Model):
    user = models.ForeignKey(User)
    message = models.ForeignKey('Message')
