from django.http import HttpResponse, HttpResponseRedirect
from django.template.loader import get_template
from django.template import RequestContext
from django.core.exceptions import PermissionDenied
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.contrib.contenttypes.models import ContentType
from debate.models import Reply
from qqq.posts.forms import PostForm

from qqq.posts.models import Post
import logging

def view_post(request, id):
  """
  The post view is public, however, there is for the public no way to get there,
  except for guessing the URL.
  """
  post = get_object_or_404(Post, id=id)
  t = get_template('view_post.html')
  c = RequestContext(request)
  c['post'] = post
  return HttpResponse(t.render(c))

###################################################################################
#################################### MEMBERS ONLY #################################
###################################################################################

@login_required
def new_post(request):
  """
  A simple view to submit a new post
  """
  if request.method == "POST":
    form = PostForm(request.POST)
    if form.is_valid():
      form.save(request.user)
      return HttpResponseRedirect('/')
  else:
    form = PostForm()
  t = get_template('new_post.html')
  c = RequestContext(request)
  c['form'] = form
  return HttpResponse(t.render(c))

@login_required
def edit_post(request, id):
  """
  A simple view to allow authors to edit their own posts.
  """
  post = get_object_or_404(Post, pk=id)
  type = ContentType.objects.get_for_model(post)

  # warning: this requires the root reply to exist!
  root_reply = Reply.objects.get(content_type=type, lft=1, object_id=post.id)

  if not post.user == request.user:
    raise PermissionDenied
  if request.method == "POST":
    form = PostForm(request.POST)
    if form.is_valid():
      post.subject = form.cleaned_data['subject']
      post.text = form.cleaned_data['body']
      post.save()
      root_reply.notify_user = form.cleaned_data['notify']
      root_reply.save()
      return HttpResponseRedirect(post.get_absolute_url())
  else:
    form = PostForm({
           'subject': post.subject,
           'body': post.text,
           'notify': root_reply.notify_user})
  
  t = get_template('new_post.html')
  c = RequestContext(request)
  c['form'] = form
  return HttpResponse(t.render(c))
