from django.http import HttpResponse, HttpResponseRedirect, HttpResponsePermanentRedirect, HttpResponseBadRequest, Http404, HttpResponseForbidden
from django.db.models import F
from django.template.loader import get_template
from django.template import Context, RequestContext
from django.core.paginator import Paginator, EmptyPage
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.template.defaultfilters import slugify
from django.core.urlresolvers import reverse
from django.views.generic.list_detail import object_list
from django.utils.translation import ugettext as _
from django.db.models import Q
from voting.models import Vote

from qqq.collections.forms import AddCollectionForm
from qqq.questions.models import Question
from qqq.collections.models import Collection, Collection_Questions
from qqq.questions.views import serve_question

import logging

# the nr of votes needed for a question to be deleted
DELETION_VOTE_LIMIT = 10

# the number of results to paginate by
RESULTS_PER_PAGE = 25

def collection(request, extra_context={}):
  """
  How collections work:
  
  Each time the collection view is accessed (usually by clicking the 'Save selected
  questions' button), a list of questions is updated and saved to the users'
  session, along with the sorting options that are set on the collection page.
  
  If a user publishes a collection, a collection object is created and saved to
  the database. The Collection_Questions model can be used to save the exact
  orderering of the questions, something that's not possible with session-based
  storage.
  
  The extra_context is used by the add_collection view to pass in a form object
  with errors, if necessary.

  TODO: split this huge function into better manageable parts
  """
  
  # calculate and save the set currently in the collection
  collection = set(request.POST.getlist('check'))
  to_delete = set(request.POST.getlist('uncheck'))
  if 'collection' in request.session:
    collection = collection.union(request.session['collection'])
  collection = collection.difference(to_delete)
  request.session['collection'] = collection

  # save also the way to order the questions in the collection
  sort = request.POST.get('sort', False) # return sort or false
  if sort:
    if sort in ['quality', 'difficulty', 'created']:
      request.session['sort'] = sort
  elif 'sort' in request.session:
    sort = request.session['sort']
  else:
    sort = 'difficulty' # default, not saved to session

  direction = request.POST.get('direction', False)
  if direction:
    if direction in ['ascending', 'descending']:
      request.session['direction'] = direction
  elif 'direction' in request.session:
    direction = request.session['direction']
  else:
    direction = 'ascending' # default

  # prg pattern added as an afterthought...
  if not extra_context and request.method == 'POST': return HttpResponseRedirect(reverse('qqq.collections.views.collection'))

  # retrieve the set from the database
  s = '' if direction == 'ascending' else '-'
  questions = Question.objects.filter(pk__in=collection).order_by(s + sort)
  if request.user.is_authenticated():
    print 'user is authenticated'
    owned = Collection.objects.filter(user=request.user).order_by('title')
  else:
    print 'user is not authenticated'
    owned = []

  # if a specific question from the collection is requested, serve it
  nr = request.GET.get(_('question'))
  if questions and nr:
    try: nr = int(nr)
    except: raise Http404
    c = {'numero': nr, 'collection': True}
    p = Paginator(questions, 1)
    try: [q] = p.page(nr).object_list
    except EmptyPage: raise Http404
    if p.page(nr).has_previous():
      c['previous'] = reverse('qqq.collections.views.collection') + '?%s=%i' % (_('question'), nr - 1)
    if p.page(nr).has_next():
      c['next'] = reverse('qqq.collections.views.collection') + '?%s=%i' % (_('question'), nr + 1)
    return serve_question(request, q, extra_context=c)
  
  # else, serve the collection page
  t = get_template('collection.html')
  c = RequestContext(request)
  c.update(extra_context)
  c['sort'] = sort
  c['direction'] = direction
  c['questions_list'] = questions
  c['owned_collections'] = owned
  if 'form' not in c: c['form'] = AddCollectionForm()
  return HttpResponse(t.render(c))

def collections(request):
  """
  Serves the collections page.
  
  Contains a full-fledged and working implementation of voting for collections,
  however it has been commented out in the templates. Uncomment only in case
  of popular demand ;-)
  """
  c = {}
  results = Collection.objects.all()
  page = request.GET.get(_('page'), 1)

  if _('query') in request.GET:
    query = request.GET[_('query')]
    c['query'] = query
    # beware: Q objects!
    results = results.filter(Q(title__icontains=query) | Q(description__icontains=query))

  # uncomment next line to enable collection voting:
  # c['votes'] = Vote.objects.get_for_user_in_bulk(results, request.user)
  
  # beware: this (deprecated) generic view creates the context key 'collections_list'
  return object_list(request,
                     queryset = results,
         template_object_name = 'collections',
                template_name = 'collections.html',
                  paginate_by = RESULTS_PER_PAGE,
                         page = page,
                extra_context = c)

def download(request, type):
  """
  Creates a text representation of the questions in the session.
  """
  if type not in ['txt', 'csv']:
    raise Http404
  collection = request.session.get('collection', False)
  if not collection: raise Http404
  sort = request.session.get('sort', 'difficulty')
  direction = request.session.get('direction', 'ascending')
  
  # retrieve the set from the database
  s = '' if direction == 'ascending' else '-'
  questions = Question.objects.filter(pk__in=collection).order_by(s + sort)

  t = get_template('download.%s' % type)
  c = Context({'questions': questions})
  return HttpResponse(t.render(c), mimetype="text/plain")

def download_saved_collection(request, numero, type):
  """
  Creates a text representation of the questions in the session.
  """
  if type not in ['txt', 'csv']:
    raise Http404
  collection = get_object_or_404(Collection, pk=numero)
  
  # retrieve the set from the database
  memberships = Collection_Questions.objects.filter(collection=collection).order_by('position')
  questions = [ membership.question for membership in memberships ]
  
  t = get_template('download.%s' % type)
  c = Context({'questions': questions})
  return HttpResponse(t.render(c), mimetype="text/plain")

def saved_collection(request, numero, slug=None):
  """
  Serves a saved-collection page, with options to edit if the logged-in
  user is the owner of the collection.
  """
  collection = get_object_or_404(Collection, pk=numero)
  memberships = Collection_Questions.objects.filter(collection=collection).order_by('position')
  owner = request.user.is_authenticated() and request.user == collection.user
  
  if not slug or slug != slugify(collection.title):
    return HttpResponsePermanentRedirect(collection.get_absolute_url())
  
  # delegate all POST requests to appropriate functions
  if owner and request.method == 'POST':
    action = request.POST.get('action', False)
    if action:
      if action == 'reorder':
        return _reorder(request, collection, memberships)
      elif action == 'delete':
        return _delete(request, collection, memberships)
      elif action == 'edit_title':
        return _edit_title(request, collection)
      elif action == 'edit_description':
        return _edit_description(request, collection)
      elif action == 'delete_collection':
        return _delete_collection(request, collection)
      else:
        return HttpResponseBadRequest(get_template('400.html').render(Context()))
           
  questions_list = [ membership.question for membership in memberships ]

  # if a specific question from the collection is requested, serve it
  nr = request.GET.get(_('question'))
  if nr:
    try: nr = int(nr)
    except: raise Http404
    c = {'numero': nr, 'collection': True}
    p = Paginator(questions_list, 1)
    try: [q] = p.page(nr).object_list
    except EmptyPage: raise Http404
    if p.page(nr).has_previous():
      c['previous'] = collection.get_absolute_url() + '?%s=%i' % (_('question'), nr - 1)
    if p.page(nr).has_next():
      c['next'] = collection.get_absolute_url() + '?%s=%i' % (_('question'), nr + 1)
    return serve_question(request, q, extra_context=c)

  # serve the (updated) collection page
  t = get_template('saved_collection.html')
  c = RequestContext(request)
  c['owner'] = owner
  c['collection'] = collection
  c['questions_list'] = questions_list
  return HttpResponse(t.render(c))

def _reorder(request, collection, memberships):
  position = int(request.POST.get('position'))
  direction = request.POST.get('direction')
  
  if direction not in ['up', 'down']:
    raise ValueError
  
  if direction == 'up':
    positions = [ position, position-1 ]
  else:
    positions = [ position, position+1 ]
  
  swap = memberships.filter(position__in=positions).order_by('position')
  obj1 = swap[0]
  obj2 = swap[1]
  
  obj1.position += 1
  obj2.position -= 1

  obj1.save()
  obj2.save()
  return HttpResponseRedirect(collection.get_absolute_url())

def _delete(request, collection, memberships):
  position = int(request.POST.get('position'))

  # retrieve to-be-removed membership object
  toast = Collection_Questions.objects.get(collection=collection, position=position)
  
  # subtract 1 of the position all records following the to-be-removed membership
  Collection_Questions.objects.filter(collection=collection, position__gt=toast.position).update(position=F('position')-1)
  
  # delete the to-be-removed membership object
  toast.delete()

  return HttpResponseRedirect(collection.get_absolute_url())

def _edit_title(request, collection):
  title = request.POST.get('title', False)
  if title:
    collection.title = title
    collection.save()
  else:
    return HttpResponseBadRequest(get_template('400.html').render(Context()))
  return HttpResponseRedirect(collection.get_absolute_url())
  
def _edit_description(request, collection):
  description = request.POST.get('description', False)
  if description:
    collection.description = description
    collection.save()
  else:
    return HttpResponseBadRequest(get_template('400.html').render(Context()))
  return HttpResponseRedirect(collection.get_absolute_url())
  
def _delete_collection(request, collection):
  collection.delete()
  return HttpResponse(reverse('qqq.collections.views.collections'))

###################################################################################
#################################### MEMBERS ONLY #################################
###################################################################################

@login_required
def add_collection(request):
  """
  Creates a collection object from the questions currently in the session
  """
  if request.method == 'POST':
    form = AddCollectionForm(request.POST)
    if form.is_valid():
      list = request.session.get('collection', False)
      if not list: return HttpResponseRedirect(reverse('qqq.collections.views.collection'))
      sort = request.session.get('sort', 'difficulty')
      direction = request.session.get('direction', 'ascending')
      s = '' if direction == 'ascending' else '-'
      questions = Question.objects.filter(pk__in=list).order_by(s + sort)
      c = form.save(request.user, questions)
      return HttpResponseRedirect(c.get_absolute_url())
  else:
    form = AddCollectionForm()
  c = {'form': form}
  return collection(request, extra_context=c)

@login_required
def add_to_saved_collection(request):
  numero = int(request.POST.get('numero'))
  collection = Collection.objects.get(pk=numero)
  to_add = request.session.get('collection')
  memberships = Collection_Questions.objects.filter(collection=collection)
  
  # create and save new membership objects for each submitted question
  if to_add:
    sort = request.session.get('sort', 'difficulty')
    direction = request.session.get('direction', 'ascending')
    s = '' if direction == 'ascending' else '-'
    count = memberships.count()
    
    # loop over to-be-added Question objects
    for (i,q) in enumerate(Question.objects.filter(pk__in=to_add).order_by(s + sort)):
      
      # When you are in an optimizing mood, check if multiple rows can be
      # added in one database INSERT INTO query.
      
      # Even more stuff to do: prevent adding of questions that are
      # already in the collection.
      
      membership = Collection_Questions(
                   collection = collection,
                     question = q,
                     position = i + 1 + count)
      membership.save()
  
  return HttpResponseRedirect(collection.get_absolute_url())

@login_required
def vote_for_collection(request):
  if not request.method == 'POST':
    logging.warning('Someone accessed the vote form target at %s with a GET request (should be POST)', reverse('qqq.collections.views.vote_for_collection'))
    raise Http404
  collection = get_object_or_404(Collection, pk=request.POST.get('id'))
  if request.POST.get('vote') == 'up':
    Vote.objects.record_vote(collection, request.user, +1)
  if request.POST.get('vote') == 'down':
    Vote.objects.record_vote(collection, request.user, -1)
  # score is saved on collection objects as well
  # (yes, this leads to a race condition and data duplication,
  # please ask the django-voting makers for a way to sort by votes)
  collection.votes = Vote.objects.get_score(collection)['score']
  collection.save()
  parameters = ''
  if request.POST.get('sort'):
    parameters = "?%s=%s" % (_('sort'), _(request.POST['sort']))
  return HttpResponseRedirect(reverse('qqq.collections.views.collections') + parameters)

