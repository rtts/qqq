from django.http import HttpResponse, HttpResponseRedirect, HttpResponsePermanentRedirect, Http404
from django.template.loader import get_template
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.core.urlresolvers import reverse
from django.views.generic.list_detail import object_list
from django.template.defaultfilters import slugify
from django.utils.translation import ugettext as _
from tagging.models import Tag, TaggedItem
from tagging.utils import parse_tag_input
from voting.models import Vote
from qqq.questions.models import Question, Rating
from qqq.questions.forms import AddQuestionForm, RateQuality
import logging

# the nr of votes needed for a question to be deleted
DELETION_VOTE_LIMIT = 10

# the number of results to paginate by
RESULTS_PER_PAGE = 25

def questions(request):
  """
  Serves the result page for question queries.

  Queries can include a search string, one or more tags (which are intersected)
  and an ordering. The serving uses django's generic view object_list, which
  paginates the results.
  
  There is currently no way to specify more than one tag, except for manually
  appending extra &tag=foo's to the URL.
  """
  c = {} # context that will be passed to generic view
  # Translators: qqq.org/search?sort=foo
  sort = request.GET.get(_('sort'))
  results = Question.objects.all().filter(is_deleted=False).select_related('user', 'contributors')
  
  # there is an SQL n+1 problem here, as the template calls for each question
  # question.get_tags() resulting in a db query. It's not possible to do a
  # select_related() since it won't span a manytomany relationship.
  # a possible solution is to query tagging_taggeditems directly with a
  # select_related(), however it won't span a GenericForeignKey... :-(

  # Translators: these are the URL options for sort
  if sort not in [_('quality'), _('difficulty'), _('created')]:
    results = results.order_by('-quality')
  else:
    if sort == _('quality'): sort = 'quality'
    if sort == _('difficulty'): sort = 'difficulty'
    if sort == _('created'): sort = 'created'
    c['sort'] = sort
    # warning: template variable 'sort' is not translated, because a translated
    # value prevents using {% if sort == 'quality' %}selected="selected"{% endif %}
    # attribute on the <option> tag
    results = results.order_by('-' + sort)

  # Translators: qqq.org/search?query=foo
  if _('query') in request.GET:
    query = request.GET[_('query')]
    c['query'] = query
    results = results.filter(text__icontains=query)
  
  # Translators: qqq.org/search?query=foo&tag=bar
  if _('tag') in request.GET:
    tags = request.GET.getlist(_('tag'))
    c['selected_tags'] = tags
    results = TaggedItem.objects.get_by_model(results, tags)
  
  # Translators: qqq.org/search?contains=video
  if _('contains') in request.GET:
    # not implemented yet
    c['contains'] = request.GET.getlist(_('contains'))
  
  c['tags_list'] = Tag.objects.cloud_for_model(Question, steps=9, min_count=None)
  
  # Translators: qqq.org/query=foo&sort=bar&page=2
  page = request.GET.get(_('page')) or 1
  
  # really no need for the generic view here, just use Paginator directly
  # (then again, when is there ever a need for a generic view?)
  return object_list(request,
                    queryset = results,
        template_object_name = 'questions',
               template_name = 'questions.html',
                 paginate_by = RESULTS_PER_PAGE,
                        page = page,
               extra_context = c)
 
def question(request, id, slug=None):
  """
  The single-question view.

  This view should be called when a user requests a single question,
  without a collection context. There will be no previous/next links,
  and no question number.
  """
  q = get_object_or_404(Question, pk=id)
  
  if q.is_deleted:
    c = RequestContext(request)
    c['question'] = q
    t = get_template('question_deleted.html')
    return HttpResponse(t.render(c))
  
  if not slug or slug != slugify(q.text):
    return HttpResponsePermanentRedirect(q.get_absolute_url())
  
  return serve_question(request, q, {})

def serve_question(request, q, extra_context={}):
  """
  Provides the meat of the question view, but depends on a question
  object that was already fetched from the database (so it cannot
  be called from urls.py)
  
  The extra_context is used by the collection view to pass
  in previous/next values and a question numero
  """
  c = RequestContext(request)
  c.update(extra_context)

  if q.needs_revision:
    total = Vote.objects.get_score(q)
    c['limit'] = DELETION_VOTE_LIMIT
    c['pro'] = (total['num_votes'] + total['score']) / 2
    c['con'] = total['num_votes'] - c['pro']
    c['score'] = total['score']
    c['vote'] = Vote.objects.get_for_user(q, request.user)

  if not request.user.is_anonymous():
    try:
      existing_rating = Rating.objects.get(question=q, user=request.user)
    except Rating.DoesNotExist:
      existing_rating = False
      c['should_rate'] = True
    except Rating.MultipleObjectsReturned:
      # someone cheated!
      pass

  # secret code path for user 1
  if request.user.id == 1:
    existing_rating = False
    c['should_rate'] = True

  if request.user.is_authenticated() and request.method == 'POST':
    if existing_rating:
      t = get_template('403.html')
      return HttpResponse(t.render(c))
    form = RateQuality(request.POST)
    if form.is_valid():
      form.save(request.user, q)
      return HttpResponseRedirect(q.get_absolute_url())
  
  c['question'] = q
  c['tags'] = q.get_tags()
  t = get_template('question.html')
  return HttpResponse(t.render(c))

###################################################################################
#################################### MEMBERS ONLY #################################
###################################################################################

@login_required
def update_tags(request, question_pk):
  """
  A form targeted from the question view. Maybe require some kind of karma
  treshold to be able to change tags?
  
  New tags will trigger the creation of a TagAction object for display in the
  feed, as well as tags that are after the update no longer associated with
  any questions. See the tag_handlers in the models.
  """
  q = get_object_or_404(Question, pk=question_pk)
  if request.method == "POST":
    # should really use a forms.Form with a tagging.TagField for this
    current_tags = q.get_tags()
    updated_tags = parse_tag_input(request.POST['tags'])
    removal_tags = [tag for tag in current_tags if tag.name not in updated_tags]
    Tag.objects.filter(name__in=removal_tags).delete()
    q.set_tags(request.POST['tags'])
  return HttpResponseRedirect(q.get_absolute_url())

@login_required
def add_question(request):
  """
  Add your questions here!
  """
  t = get_template('addquestion.html')
  c = RequestContext(request)
  if request.method == 'POST':
    form = AddQuestionForm(request.POST)
    if form.is_valid():
      q = form.save(request.user)
      return HttpResponseRedirect(q.get_absolute_url())
  else:
    form = AddQuestionForm()
  c['form'] = form
  return HttpResponse(t.render(c))

@login_required
def vote_for_deletion(request):
  """
  Registers a vote for deletion of a question, and performs the delete
  after enough votes.
  """
  if not request.method == 'POST':
    logging.warning('Someone accessed the vote form target at %s with a GET request (should be POST)', reverse('qqq.questions.views.vote_for_deletion)'))
    raise Http404
  question = get_object_or_404(Question, pk=request.POST['id'])
  if not question.needs_revision:
    raise Http404
  if (request.POST['vote'] == 'up'):
    Vote.objects.record_vote(question, request.user, +1)
  if (request.POST['vote'] == 'down'):
    Vote.objects.record_vote(question, request.user, -1)
  if Vote.objects.get_score(question)['score'] >= DELETION_VOTE_LIMIT:
    question.is_deleted = True
    question.save()
  return HttpResponseRedirect(question.get_absolute_url())
