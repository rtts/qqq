from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType

# django-mptt: http://github.com/django-mptt/django-mptt/
from mptt.models import MPTTModel, TreeForeignKey
from mptt.managers import TreeManager

MAX_LENGTH = 10000

class Reply(MPTTModel):
  """
  A generic reply to an object, or to another reply
  """
  parent = TreeForeignKey('self', null=True, blank=True, related_name='children')

  content_type = models.ForeignKey(ContentType)
  object_id    = models.PositiveIntegerField()
  object       = generic.GenericForeignKey('content_type', 'object_id')

  user     = models.ForeignKey(User, null=True, blank=True)
  created  = models.DateTimeField(auto_now_add=True)
  modified = models.DateTimeField(auto_now=True)

  is_public   = models.BooleanField(default=True)
  is_removed  = models.BooleanField(default=False)
  notify_user = models.BooleanField()

  text = models.TextField(max_length=MAX_LENGTH)
  
  class Meta:
    db_table = 'debate_tree'
  
  def get_absolute_url(self):
    return '#'.join([self.object.get_absolute_url(), str(self.lft)])
  
  def get_summary(self):
    if self.lft > 1:
      return self.text
    else:
      return self.object.get_summary()
