from django.db import models
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.db.models.signals import post_save, post_delete
from tagging.models import Tag

class Contribution(models.Model):
  """
  Base class for user contributions, using multi-table inheritance.
  This way, a query for all Contribution objects will automagically
  yield a time-ordered feed of different child-objects.
  
  For performance reasons, be sure to always use a 'select-related' clause
  on any query for Contribution objects, or many more queries will follow
  when accessing child objects!
  """
  created = models.DateTimeField(auto_now_add=True)
  modified = models.DateTimeField(auto_now=True)
  user = models.ForeignKey(User, blank=True, null=True, related_name='contributions')

  class Meta:
    ordering = ['-created']
    db_table = 'contribution'

class TagAction(Contribution):
  """
  These objects describe the deletion or addition of a tag in the database.
  Two signal handlers automatically create TagAction objects when needed:
  """
  name = models.CharField(max_length = 50)
  is_deleted = models.BooleanField()
  
  class Meta:
    db_table = 'contribution_tagaction'

def new_tag_handler(sender, instance, created, **kwargs):
  if created:
    TagAction.objects.filter(name=instance.name).delete()
    t = TagAction(name = instance.name)
    t.is_deleted = False
    t.save()
post_save.connect(new_tag_handler, sender=Tag)

def del_tag_handler(sender, instance, **kwargs):
  TagAction.objects.filter(name=instance.name).delete()
  t = TagAction(name = instance.name)
  t.is_deleted = True
  t.save()
post_delete.connect(del_tag_handler, sender=Tag)
