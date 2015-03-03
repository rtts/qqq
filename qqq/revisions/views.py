from django.http import HttpResponse, HttpResponseRedirect, HttpResponsePermanentRedirect, Http404
from django.template.loader import get_template
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext as _
from voting.models import Vote

from user_profile.views import get_profile
from qqq.revisions.forms import RevisionForm
from qqq.questions.forms import AddQuestionForm
from qqq.questions.models import Question
from qqq.revisions.models import Revision

import logging

# the nr of votes needed for a question to be deleted
DELETION_VOTE_LIMIT = 10

# the number of results to paginate by
RESULTS_PER_PAGE = 25

def revision(request, question_nr, revision_nr, slug=None):
  """
  Serves a revision to a question. The resulting page looks almost like
  a question page, but the changes to the original question will be highlighted
  using <ins> and <del> tags.
  """
  c = RequestContext(request)
  t = get_template('revision.html')
  
  try:
    revision = Revision.objects.get(nr=revision_nr, object_id=question_nr)
  except Revision.DoesNotExist:
    raise Http404
  
  correct_slug = revision.test_url(slug)
  if correct_slug:
    return HttpResponsePermanentRedirect(correct_slug)
  
  total = Vote.objects.get_score(revision)
  c['limit'] = revision.edit_distance + 1
  c['pro'] = (total['num_votes'] + total['score']) / 2
  c['con'] = total['num_votes'] - c['pro']
  c['score'] = total['score']
  c['vote'] = Vote.objects.get_for_user(revision, request.user)
  c['revision'] = revision
  c['question'] = revision.decode_pretty()
  return HttpResponse(t.render(c))

###################################################################################
#################################### MEMBERS ONLY #################################
###################################################################################

@login_required
def add_revision(request):
  """
  The process of adding a revision is rather complicated. First, the user
  is presented an AddQuestionForm with the questions prefilled. After
  changing and submitting, the user sees an unfinished revision object page,
  with a pretty formatted revision to the question but no save to the database
  yet (all information is contained in hidden form fields).

  After supplying a description the hidden form data is validated (again) and
  the revision object is saved to the database.
  
  This view handles all these steps (in reverse order):
    1) addquestion.html with question prefilled
    2) revision.html with marked changes
    3) final save to the database
  
  All revision-related logic happens in the Revision class, be sure to check out
  its methods.
  """
  c = RequestContext(request)
  
  # my first translated GET parameter! :-)
  nr = request.GET.get(_('question'))

  old_question = get_object_or_404(Question, numero=nr)

  if request.method == 'POST':
    form = AddQuestionForm(request.POST)
    if form.is_valid():
      post = form.cleaned_data
      new_question = Question(text = post['text'],
                            answer = post['answer'],
                           sources = post['sources'])
      r = Revision(user = request.user)
      r.encode(old_object = old_question,
               new_object = new_question,
                   fields = ['text', 'answer', 'sources'],
                     save = False)
      
      if request.POST['final'] == 'true':
        # mind the reassignment to 'form':
        form = RevisionForm(request.POST)
        if form.is_valid():
          r.description = form.cleaned_data['description']
          r.nr = 1 + Revision.objects.filter(object_id = old_question.pk).count()
          r.save()
          return HttpResponseRedirect(r.get_absolute_url())
      else:
        form = RevisionForm(initial=request.POST) #!
      
      c['question'] = r.decode_pretty()
      c['revision'] = True
      c['form'] = form
      t = get_template('addrevision.html')
      return HttpResponse(t.render(c))

  else:
    form = AddQuestionForm(
           {'text': old_question.text,
            'answer': old_question.answer,
            'sources': old_question.sources})
    
  c['form'] = form
  c['question'] = old_question
  t = get_template('addquestion.html')
  return HttpResponse(t.render(c))

@login_required
def vote_for_revision(request):
  """
  Registers a vote for a revision, and applies the revision after enough votes.
  """
  if not request.method == 'POST':
    logging.warning('Someone accessed the vote form target at %s with a GET request (should be POST)', reverse('qqq.revisions.views.vote_for_revision'))
    raise Http404
  revision = get_object_or_404(Revision, id=request.POST['id'])
  if (request.POST['vote'] == 'up'):
    Vote.objects.record_vote(revision, request.user, +1)
  if (request.POST['vote'] == 'down'):
    Vote.objects.record_vote(revision, request.user, -1)
  if Vote.objects.get_score(revision)['score'] > revision.edit_distance:
    question = revision.object
    
    # add revision user to contributors list
    if question.user != revision.user:
      question.contributors.add(revision.user)
    
    # reward revision user with karma for the upvotes
    profile = get_profile(revision.user)
    profile.karma += revision.edit_distance
    profile.save()

    revision.apply()
    # the apply method already deletes the revision!
    # revision.delete()

    return HttpResponseRedirect(question.get_absolute_url())
  return HttpResponseRedirect(request.POST['next'])
