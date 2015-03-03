from django import forms
from tagging.forms import TagField
LMAX = 5000
SMAX = 500

class RevisionForm(forms.Form):
  """
  The RevisionForm is not your typical form, due to the 2-step process
  of submitting a revision. This form is used for the second step, which
  contains all the data entered in the first step as hidden fields.
  
  All the real logic can be found in the view add_revision
  """
  description = forms.CharField(required=True, max_length=LMAX, widget=forms.Textarea())
  text = forms.CharField(required=True, max_length=LMAX, widget=forms.HiddenInput())
  answer = forms.CharField(required=True, max_length=LMAX, widget=forms.HiddenInput())
  sources = forms.CharField(required=False, max_length=LMAX, widget=forms.HiddenInput())
  tags = TagField(required=False, max_length=SMAX, widget=forms.HiddenInput())
