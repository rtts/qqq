import datetime
from django import forms
from messages.models import Message

class ProfileForm(forms.Form):
  description = forms.CharField(required=False, max_length=5000, widget=forms.Textarea(attrs={'rows': '20', 'cols': '80'}))
  
  # i'm not sure about defining a form.save() method, because each form needs
  # different stuff when on saving, and views might need some or all of that
  # stuff as well. who says we need this method anyway?
  def save(self, profile):
    profile.description = self.cleaned_data['description']
    profile.save()

class MessageForm(forms.Form):
  subject = forms.CharField(max_length=500)
  body = forms.CharField(max_length=5000, widget=forms.Textarea())
  
  def save(self, sender, recipient, parent):
    msg = Message(
          sender = sender,
          recipient = recipient,
          subject = self.cleaned_data['subject'],
          body = self.cleaned_data['body'])
    if parent:
      msg.parent_msg = parent
      parent.replied_at = datetime.datetime.now()
      parent.save()
    msg.save()
