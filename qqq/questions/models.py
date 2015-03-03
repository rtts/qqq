from django.db import models
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.contrib.contenttypes.models import ContentType
from django.template.defaultfilters import slugify
from django.db.models import Avg
from tagging.models import Tag

from user_profile.views import get_profile
from qqq.models import Contribution
from qqq.revisions.models import Revision

class Question(Contribution):
  """
  A quiz question
  """
  numero = models.AutoField(primary_key=True)
  text = models.TextField(db_index=True)
  answer = models.TextField()
  sources = models.TextField(blank=True)
  quality = models.FloatField(default=0)
  difficulty = models.FloatField(default=0)
  video_url = models.TextField(blank=True)
  video_html = models.TextField(blank=True)
  is_deleted = models.BooleanField(default=False)
  needs_revision = models.BooleanField(default=False)
  contributors = models.ManyToManyField(User, related_name='questions')

  def get_summary(self):
    return self.text
  
  def get_absolute_url(self):
    return reverse('qqq.questions.views.question', args=[self.numero, slugify(self.text)])
  
  def get_revisions(self):
    type = ContentType.objects.get_for_model(self)
    return Revision.objects.filter(content_type=type, object_id=self.numero)

  def set_tags(self, tags):
    Tag.objects.update_tags(self, tags)

  def get_tags(self):
    tag_list = Tag.objects.get_for_object(self)
    return tag_list

  def has_video(self):
    if self.video_html: return True

  def __str__(self):
    return self.text
  
  class Meta:
    db_table = 'contribution_question'

class Rating(models.Model):
  """
  A quality and difficulty rating of a Question object.
  """
  question = models.ForeignKey(Question, related_name='ratings')
  user = models.ForeignKey(User)
  quality = models.IntegerField()
  difficulty = models.IntegerField()
  
  def save(self):
    question = self.question
    if question.is_deleted:
      return
    else:
      super(Rating, self).save()
      
      # calculate and save quality and difficulty on question object
      mean = question.ratings.aggregate(Avg('quality'))['quality__avg']
      question.quality = (mean - 1) / 9.0
      mean = question.ratings.aggregate(Avg('difficulty'))['difficulty__avg']
      question.difficulty = (mean - 1) / 9.0

      # set cleanup flag if rating is insufficient
      nr_ratings = question.ratings.count()
      if nr_ratings > 10 and question.quality < 0.5:
        question.needs_revision = True
      else:
        question.needs_revision = False
      question.save()
      
      # adjust user karma depending on quality rating
      if self.quality >= 6:
        profile = get_profile(question.user)
        if self.quality in [6,7]:
          profile.karma += 1
        elif self.quality in [8,9]:
          profile.karma += 2
        elif self.quality == 10:
          profile.karma += 3
        profile.save()
      else:
        # don't be so mean to subtract karma points
        pass
  
  class Meta:
    db_table = 'rating'
