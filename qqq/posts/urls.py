from django.conf.urls.defaults import *
from django.utils.translation import ugettext as _

urlpatterns = patterns('qqq.posts.views',
  (r'^%s/(\d+)/$' % _('post'), 'view_post'),
  (r'^%s/$' % _('new-post'), 'new_post'),
  (r'^%s/(\d+)/$' % _('edit-post'), 'edit_post'),
)
