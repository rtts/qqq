from django.conf.urls.defaults import *
from django.utils.translation import ugettext as _

urlpatterns = patterns('debate.views',
  (r'^%s/$' % _('post-reply'), 'post_reply'),
  (r'^%s/(\d+)/$' % _('edit-reply'), 'edit_reply'),
)
