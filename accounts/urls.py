from django.conf.urls import patterns, url

urlpatterns = patterns('accounts.views',
    url(r'^register/$', 'register'),
    url(r'^login/$', 'login'),
    url(r'^logout/$', 'logout'),
    url(r'^feeds/$', 'get_feeds'),
    url(r'^(\d+)/follow/$', 'add_friend'),
    url(r'^upload_avatar', 'upload_avatar'),
)

urlpatterns += patterns('',
    url(r'^password_reset/', 'django.contrib.auth.views.password_reset'),
)
