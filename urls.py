from django.conf.urls.defaults import *
from settings import MEDIA_ROOT

urlpatterns = patterns('',
  (r'', include('qqq.urls')),
  (r'', include('debate.urls')),
  (r'', include('user_profile.urls')),

  (r'^files/(?P<path>.*)$', 'django.views.static.serve', {'document_root': MEDIA_ROOT}),
  (r'^logout/$', 'django.contrib.auth.views.logout'),
  (r'^login/$', 'django.contrib.auth.views.login'),

  (r'^activate/(?P<activation_key>[\w=]+)/$', 'registration.views.activate'),
  (r'^register/$', 'registration.views.register'),
  (r'^account/', include('registration.urls')),
)
