from django.conf.urls.defaults import *

urlpatterns = patterns('',
    (r'^$', 'qqq.views.home'),
    (r'', include('qqq.questions.urls')),
    (r'', include('qqq.revisions.urls')),
    (r'', include('qqq.collections.urls')),
    (r'', include('qqq.posts.urls')),
)
