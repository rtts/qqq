from django.db import models
from django.core.urlresolvers import reverse
from django.contrib.contenttypes.models import ContentType
from django.template.defaultfilters import slugify
from voting.models import Vote
from django.utils.encoding import smart_str
from cPickle import loads, dumps
from django.contrib.contenttypes import generic
from django.utils.html import escape
from django.utils.safestring import mark_safe
# google-diff-match-patch: http://code.google.com/p/google-diff-match-patch/
from diff_match_patch import diff_match_patch

from qqq.models import Contribution

class Revision(Contribution):
  """
  A revision to another object, that saves the diffs to the fields
  specified to the encode() method.
  
  Since it is only used to revise Question objects, the GenericForeignKey
  might as well be replaced with a ForeignKey to Question.
  
  On the other hand, if it ain't broke, don't fix it!
  """
  content_type = models.ForeignKey(ContentType)
  object_id    = models.PositiveIntegerField()
  object       = generic.GenericForeignKey()

  nr = models.PositiveIntegerField()
  
  description = models.TextField()
  edit_distance = models.PositiveIntegerField(default=0)

  diff = models.TextField() # stores a pickled hash of diffs
  
  def get_absolute_url(self):
    temp_question = self.decode()
    return reverse('qqq.revisions.views.revision', args=[self.object_id, self.nr, slugify(temp_question.text)])

  def test_url(self, slug):
    temp_question = self.decode()
    correct_slug = slugify(temp_question.text)
    if slug != correct_slug:
      return reverse('qqq.revisions.views.revision', args=[self.object_id, self.nr, correct_slug]) 

  def score(self):
    return Vote.objects.get_score(self)['score']
  
  def encode(self, old_object, new_object, fields=[], save=True):
    """
    Computes and saves a patch given two objects and a list of (string) members
    """
    self.content_type = ContentType.objects.get_for_model(old_object)
    self.object_id = old_object.pk
    dmp = diff_match_patch()
    patches = {}
    for field in fields:
      patches[field] = dmp.patch_toText(dmp.patch_make(
                         eval('old_object.' + field),
                         eval('new_object.' + field)))

      # ugly hack to exempt sources from edit distance computation
      if not field == 'sources':
        self.edit_distance += dmp.diff_levenshtein(
                              dmp.diff_main(escape(eval('old_object.' + field)),
                                            escape(eval('new_object.' + field))))
    self.diff = dumps(patches)
    if save:
      self.save()
  
  def decode(self):
    """
    Returns a new object with the patch(es) applied
    """
    dmp = diff_match_patch()
    new_object = self.content_type.model_class()()
    new_object.id = self.object_id
    patches = loads(smart_str(self.diff))
    for field in patches:
      # some exec trickery is needed here to address class members by
      # names we only know by the string value 'field'
      if patches[field]:
        exec('new_object.' + field + ' = dmp.patch_apply(dmp.patch_fromText(' \
                                         + 'patches[field]), self.object.' + field + ')[0]')
      else:
        exec('new_object.' + field + ' = self.object.' + field)
    return new_object

  def decode_pretty(self):
    """
    Returns a revised object with pretty formatted fields
    """
    dmp = diff_match_patch()
    old_object = self.object
    new_object = self.decode()
    patches = loads(smart_str(self.diff)) # only needed for the keys
    
    for field in patches:
      if not patches[field]:
        continue
      diff = dmp.diff_main(escape(eval('old_object.' + field)),
                           escape(eval('new_object.' + field)))
      dmp.diff_cleanupSemantic(diff)
      html = []
      for (op, text) in diff:
        if op == 1:
          html.append("<ins>%s</ins>" % text)
        elif op == -1:
          html.append("<del>%s</del>" % text)
        elif op == 0:
          html.append(text)
      exec('new_object.' + field + ' = mark_safe("".join(html))')
    return new_object
  
  def apply(self):
    """
    Applies the revision to its associated object, and then deletes itself.
    """
    old_object = self.object
    new_object = self.decode()
    patches = loads(smart_str(self.diff))
    for field in patches:
      exec('old_object.' + field + ' = new_object.' + field)
    # print "old_object.text = " + old_object.text
    old_object.save()
    self.delete()

  def __str__(self):
    return self.description

  class Meta:
    ordering = ['created']
    db_table = 'contribution_revision'
