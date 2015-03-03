from django.conf.urls.defaults import *
from django.utils.translation import ugettext as _

urlpatterns = patterns('qqq.questions.views',
  (r'^%s/$' % _('questions'), 'questions'),
  (r'^(\d+)/$', 'question'),
  (r'^(\d+)/([^/]+)/$', 'question'),
  (r'^%s/$' % _('vote-for-deletion'), 'vote_for_deletion'),
  (r'^%s/$' % _('add-question'), 'add_question'),
  (r'^%s/(\d+)/$' % _('update-tags'), 'update_tags'),
)
