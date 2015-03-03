from django import forms
from tagging.forms import TagField
from debate.models import Reply
from qqq.utils import url_to_html
from qqq.questions.models import Question, Rating
LMAX = 5000
SMAX = 500

class AddQuestionForm(forms.Form):
  """
  Users can submit questions and revisions using this form.
  A valid form can be saved to yield a new question, or can be used
  as the first step in submitting a revision.
  """
  video_url = forms.CharField(required=False, max_length=SMAX)
  text = forms.CharField(required=True, max_length=LMAX, widget=forms.Textarea())
  answer = forms.CharField(required=True, max_length=SMAX)
  sources = forms.CharField(required=False, max_length=LMAX, widget=forms.Textarea())
  tags = TagField(required=False, max_length=SMAX)
  notify = forms.BooleanField(initial=True, required=False)

  def save(self, user):
    q = Question(
              user = user,
              text = self.cleaned_data['text'],
            answer = self.cleaned_data['answer'], 
           sources = self.cleaned_data['sources'],
         video_url = self.cleaned_data['video_url'],
        video_html = url_to_html(self.cleaned_data['video_url']))
    q.save()
    q.set_tags(self.cleaned_data['tags'])
    
    # create the root node for replies
    r = Reply(
               user = user,
             object = q,
        notify_user = self.cleaned_data['notify'])
    r.save()

    return q

class RateQuality(forms.Form):
  quality = forms.ChoiceField(
            choices=((1,1),(2,2),(3,3),(4,4),(5,5),(6,6),(7,7),(8,8),(9,9),(10,10)),
            widget=forms.RadioSelect())
  difficulty = forms.ChoiceField(
            choices=((1,1),(2,2),(3,3),(4,4),(5,5),(6,6),(7,7),(8,8),(9,9),(10,10)),
            widget=forms.RadioSelect())
  
  def save(self, user, question):
    r = Rating(
        user = user,
        question = question,
        quality = int(self.cleaned_data['quality']),
        difficulty = int(self.cleaned_data['difficulty']))
    r.save()
