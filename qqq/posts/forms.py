from django import forms
from debate.models import Reply
from qqq.posts.models import Post
LMAX = 5000
SMAX = 500

class PostForm(forms.Form):
  subject = forms.CharField(required=True, max_length=SMAX, widget=forms.TextInput())
  body = forms.CharField(required=True, max_length=LMAX, widget=forms.Textarea())
  notify = forms.BooleanField(initial=True, required=False)
  
  def save(self, user):
    p = Post(
        user = user,
        subject = self.cleaned_data['subject'],
        text = self.cleaned_data['body'])
    p.save()

    # create the root node for replies
    r = Reply(
               user = user,
             object = p,
        notify_user = self.cleaned_data['notify'])
    r.save()
