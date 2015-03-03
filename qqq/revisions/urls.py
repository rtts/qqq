from django.conf.urls.defaults import *
from django.utils.translation import ugettext as _

urlpatterns = patterns('qqq.revisions.views',
  (r'^(\d+)/(\d+)/$', 'revision'),
  (r'^(\d+)/(\d+)/([^/]+)/$', 'revision'), # genius!
  (r'^vote_for_improvement/$', 'vote_for_revision'),
  (r'^improve/$', 'add_revision'),
)
