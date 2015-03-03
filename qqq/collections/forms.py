from django import forms
from debate.models import Reply
from qqq.collections.models import Collection, Collection_Questions
LMAX = 5000
SMAX = 500

class AddCollectionForm(forms.Form):
  """
  This form's save() method should be called with the list (queryset)
  of question objects that should be saved with it. The calling view
  (add_collection) currently determines this from the questions nrs
  stored in the session
  """
  title = forms.CharField(required=True, max_length=SMAX)
  description = forms.CharField(required=True, max_length=LMAX, widget=forms.Textarea())
  notify = forms.BooleanField(initial=True, required=False)
  
  def save(self, user, questions):
    c = Collection(
              title = self.cleaned_data['title'],
        description = self.cleaned_data['description'],
               user = user)
    c.save()
    
    # well, this is embarassing: saving records in a for loop...
    # please find a better way (no, add() is not supported in Django's
    # ManyToManyField if a specific join table is specified)
    for (i,q) in enumerate(questions):
      membership = Collection_Questions(
                   collection = c,
                     question = q,
                     position = i + 1)
      membership.save()
    
    # create the root node for replies
    r = Reply(
               user = user,
             object = c,
        notify_user = self.cleaned_data['notify'])
    r.save()
    
    return c

class EditCollectionForm(forms.Form):
  """
  Simple form for editing collections.
  Beware: only let users edit their own collections!
  """
  title = forms.CharField(required=True, max_length=SMAX)
  description = forms.CharField(required=True, max_length=LMAX, widget=forms.Textarea())
  
  def save(self, user, collection):
    collection.title = self.cleaned_data['title']
    collection.description = self.cleaned_data['description']
    collection.save()
