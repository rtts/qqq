from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import get_object_or_404, render_to_response
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from django.template.loader import get_template
from django.template import Context, RequestContext
from django.contrib.auth.decorators import login_required
from user_profile.models import Profile
from user_profile.forms import *
from messages.models import Message
from qqq.models import Contribution
from messages.views import reply as dm_reply
from messages.views import delete as dm_delete
from messages.views import compose as dm_compose
from messages.utils import format_quote
from datetime import datetime
import types

def get_profile(user):
  """Returns a user's profile, and creates one if it doesn't exist
     yet. (Should've been implemented in some auth module, but just
     in case...)"""
  try:
    p = Profile.objects.get(user=user)
  except Profile.DoesNotExist:
    p = Profile(description='', user=user)
    p.save()
  return p
     
def view_profile(request, username):
  t = get_template('profile.html')
  c = RequestContext(request)
  user = get_object_or_404(User, username=username)
  profile = get_profile(user)
  c['karma'] = profile.karma
  c['description'] = profile.description
  c['feed'] = user.contributions.all().select_related('user', 'question', 'revision', 'post', 'tagaction')[:25]
  c['username'] = username
  return HttpResponse(t.render(c))



@login_required
def view_message(request, id):
  t = get_template('view_pm.html')
  c = RequestContext(request)
  msg = get_object_or_404(Message, id=id)
  msg.read_at = datetime.now()
  msg.save()
  c['msg'] = msg
  return HttpResponse(t.render(c))

@login_required
def edit_profile(request):
  t = get_template('edit_profile.html')
  c = RequestContext(request)
  profile = get_profile(request.user)

  if request.method == 'POST':
    form = ProfileForm(request.POST)
    if form.is_valid():
      form.save(profile)
      return HttpResponseRedirect(reverse(view_profile, args=[request.user.username]))
  else:
    form = ProfileForm(initial={'description': profile.description})

  c['form'] = form
  c['username'] = request.user.username
  return HttpResponse(t.render(c))

def sent(request):
  c = RequestContext(request)
  t = get_template('pm_sent.html')
  return HttpResponse(t.render(c))

@login_required
def compose(request, username):
  t = get_template('send-pm.html')
  c = RequestContext(request)
  next = reverse(sent)
  recipient = get_object_or_404(User, username=username)
  
  if 'parent' in request.GET:
    parent = get_object_or_404(Message, id=request.GET['parent'])
  else:
    parent = False

  if request.method == 'POST':
    form = MessageForm(request.POST)
    if form.is_valid():
      form.save(sender=request.user, recipient=recipient, parent=parent)
      return HttpResponseRedirect(next)
  else:
    if parent:
      body = format_quote(parent.sender, parent.body)
    else:
      body = ''
    form = MessageForm(initial = {'body': body})
  
  c['form'] = form
  c['username'] = username
  return HttpResponse(t.render(c))

@login_required
def delete(request):
  if 'message' in request.GET:
    return dm_delete(request, request.GET['message'], success_url="/")
  else:
    raise Http404
