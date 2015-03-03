from django.conf.urls.defaults import *
from django.utils.translation import ugettext as _

urlpatterns = patterns('user_profile.views',
  (r'^%s/$' % _('user'), 'edit_profile'),
  (r'^%s/(\w+)/$' % _('user'), 'view_profile'),
  (r'^%s/$' % _('pm-delete'), 'delete'), # this should be implemented as a POST request
  (r'^%s/(\d+)/$' % _('pm'), 'view_message'),
  (r'^%s/(\w+)/$' % _('pm'), 'compose'),
  (r'^%s/$' % _('pm-sent'), 'sent'),
)
