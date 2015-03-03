from django.db import models
from django.core.urlresolvers import reverse
from django.template.defaultfilters import slugify

from qqq.models import Contribution
from qqq.questions.models import Question

class Collection(Contribution):
  """
  A collection of quiz questions
  """
  
  numero = models.AutoField(primary_key=True)
  title = models.TextField(db_index=True)
  description = models.TextField(db_index=True)
  questions = models.ManyToManyField(Question, through='Collection_Questions')
  downloads = models.PositiveIntegerField(default=0)
  difficulty = models.FloatField(default=0)

  # ugly denormalization to be able to sort by votes
  votes = models.IntegerField(default=0)
  
  def get_absolute_url(self):
    return reverse('qqq.collections.views.saved_collection', args=[self.numero, slugify(self.title)])
  
  class Meta:
    ordering = ['-downloads']
    db_table = 'contribution_collection'

class Collection_Questions(models.Model):
  """
  A many-to-many relation of questions to collections.
  The 'position' attribute provides a way to order the questions in a collection
  """
  collection = models.ForeignKey(Collection)
  question = models.ForeignKey(Question)
  position = models.PositiveIntegerField()

  def __str__(self):
    return self.title
  
  class Meta:
    ordering = ['position']
    db_table = 'contribution_collection_questions'
