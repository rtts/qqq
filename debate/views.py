from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404
from django.template import Context, RequestContext
from django.template.loader import get_template
from debate.forms import ReplyForm
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist
from debate.models import Reply
from django.contrib.auth.decorators import login_required

@login_required
def post_reply(request):
  t = get_template('form.html')
  c = RequestContext(request)

  try:
    parent = Reply.tree.get(id=int(request.GET['parent']))
  except (ValueError, OjectDoesNotExist):
    raise Http404
  
  if request.method == 'POST':
    form = ReplyForm(request.POST)
    if form.is_valid():
      reply = form.save(user=request.user, parent=parent)
      return HttpResponseRedirect(reply.get_absolute_url())
         
  else:
    form = ReplyForm()
  
  c['form'] = form
  c['parent'] = parent
  return HttpResponse(t.render(c))

@login_required
def edit_reply(request, id):
  t = get_template('form.html')
  c = RequestContext(request)
  reply = get_object_or_404(Reply, id=id)
  if not reply.user == request.user:
    raise PermissionDenied
  if request.method == 'POST':
    form = ReplyForm(request.POST)
    if form.is_valid():
      reply.text = form.cleaned_data['text']
      reply.notify_user = form.cleaned_data['notify']
      reply.save()
      return HttpResponseRedirect(reply.get_absolute_url())
  else:
    form = ReplyForm({
           'text':   reply.text,
           'notify': reply.notify_user})
  
  c['form'] = form
  c['parent'] = reply.parent
  c['object'] = object
  return HttpResponse(t.render(c))
