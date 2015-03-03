from django.http import HttpResponse, Http404
from django.template.loader import get_template
from django.template import RequestContext
from django.core.paginator import Paginator, EmptyPage
from django.utils.translation import ugettext as _
from tagging.models import Tag
from messages.models import Message

from settings import LANGUAGE_CODE as lang
from qqq.models import Contribution
from qqq.questions.models import Question
from qqq.revisions.models import Revision
from qqq.collections.models import Collection
from qqq.posts.models import Post

import logging

# the number of results to paginate by
RESULTS_PER_PAGE = 25

def home(request):
  """
  Serves the home page, which depends on whether the user is logged in or not.
  """
  if request.user.is_authenticated():
    return participate(request)
  else:
    c = RequestContext(request)
    if lang == "nl":
      c['frontpage'] = 'frontpage_nl.html'
    else:
      c['frontpage'] = 'frontpage_en.html'
    
    t = get_template('home_public.html')
    c['tags_list'] = Tag.objects.cloud_for_model(Question, steps=9, min_count=None)
    return HttpResponse(t.render(c))

###################################################################################
#################################### MEMBERS ONLY #################################
###################################################################################

def participate(request):
  """
  Serves the home page for logged-in users
  """
  t = get_template('home_members.html')
  c = RequestContext(request)
  
  filter = request.GET.get(_('filter'), False)
  
  # behold some serious django-fu!
  if filter == _('questions'):
    c['filter'] = 'questions'
    questions = Question.objects.all()
    objects = Contribution.objects.filter(question__in=questions).select_related('user', 'question', 'revision', 'collection', 'post', 'tagaction')
  elif filter == _('improvements'):
    c['filter'] = 'improvements'
    revisions = Revision.objects.all()
    objects = Contribution.objects.filter(revision__in=revisions).select_related('user', 'question', 'revision', 'collection', 'post', 'tagaction')
  elif filter == _('collections'):
    c['filter'] = 'collections'
    collections = Collection.objects.all()
    objects = Contribution.objects.filter(collection__in=collections).select_related('user', 'question', 'revision', 'collection', 'post', 'tagaction')
  elif filter == _('posts'):
    c['filter'] = 'posts'
    posts = Post.objects.all()
    objects = Contribution.objects.filter(post__in=posts).select_related('user', 'question', 'revision', 'collection', 'post', 'tagaction')
  else:
    objects = Contribution.objects.all().select_related('user', 'question', 'revision', 'collection', 'post', 'tagaction')

  p = Paginator(objects, RESULTS_PER_PAGE)
  c['type'] = {'all': True}
  c['paginator'] = p
  try:
    c['feed'] = p.page(request.GET.get(_('page'), '1'))
  except EmptyPage:
    raise Http404
  c['message_list'] = Message.objects.inbox_for(request.user)
  return HttpResponse(t.render(c))
