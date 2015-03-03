from django.db import models
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.db.models.signals import post_save, post_delete
from tagging.models import Tag
from qqq.models import Contribution

class Post(Contribution):
  """
  A forum post
  """
  subject = models.TextField(db_index=True)
  text = models.TextField(db_index=True)

  def get_summary(self):
    return self.subject

  def get_absolute_url(self):
    return reverse('qqq.posts.views.view_post', args=[self.id])

  def __str__(self):
    return self.subject
    
  class Meta:
    db_table = 'contribution_post'
