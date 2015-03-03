from django.db import models
from django.contrib.auth.models import User
from messages.models import Message

class Profile(models.Model):
  karma = models.IntegerField(default=0)
  description = models.TextField()
  user = models.ForeignKey(User,unique=True)

  def __str__(self):
    return self.user.username
  
  def messages(self):
    return Message.objects.filter(recipient=self.user, read_at__isnull=True, recipient_deleted_at__isnull=True).count()
      
  class Meta:
    db_table = 'user_profile'
