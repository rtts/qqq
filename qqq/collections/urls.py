from django.conf.urls.defaults import *
from django.utils.translation import ugettext as _

urlpatterns = patterns('qqq.collections.views',
  (r'^%s/$' % _('collections'), 'collections'),
  (r'^%s/(\d+)/$' % _('collection'), 'saved_collection'),
  (r'^%s/(\d+)/([^/]+)/$' % _('collection'), 'saved_collection'),
  (r'^%s/$' % _('vote-for-collection'), 'vote_for_collection'),
  (r'^%s/$' % _('add-collection'), 'add_collection'),
  (r'^%s/$' % _('collection'), 'collection'),
  (r'^%s/%s/$' % (_('collection'), _('add-questions')) , 'add_to_saved_collection'),
  (r'^%s/%s\.(\w{3})$' % (_('collection'), _('download')), 'download'),
  (r'^%s/(\d+)/%s\.(\w{3})$' % (_('collection'), _('download')), 'download_saved_collection'),
)
