from django import forms
from debate.models import MAX_LENGTH, Reply
from django.template.loader import get_template
from messages.models import Message
from django.utils.translation import ugettext as _
from django.template import Context

class ReplyForm(forms.Form):
  text = forms.CharField(required=True, max_length=MAX_LENGTH, widget=forms.Textarea())
  notify = forms.BooleanField(initial=True, required=False)
  
  def save(self, parent=None, user=None):
    r = Reply(
             object = parent.object,
               user = user,
        notify_user = self.cleaned_data['notify'],
               text = self.cleaned_data['text'])
    r.insert_at(parent, position='last-child', save=True)
    if parent.notify_user:
      t = get_template('reply_notification.txt')
      msg = Message(
        sender = user,
        recipient = parent.user,
        subject = _('Reply to one of your contributions!'),
        body = t.render(Context({
                 'username': user.username,
            'original_text': r.parent.get_summary(),
               'reply_text': r.get_summary(),
                      'url': parent.get_absolute_url() })))
      msg.save()
    return r
