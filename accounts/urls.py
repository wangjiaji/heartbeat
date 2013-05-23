from django.conf.urls import patterns, url

urlpatterns = patterns('accounts.views',
    url(r'^register/$', 'register'),
    url(r'^login/$', 'login'),
    url(r'^logout/$', 'logout'),
    url(r'^password_reset/$', 'reset_password'),
    url(r'^pw_reset_done/$', 'password_reset_done'),
    url(r'^password_change/$', 'change_password'),
    url(r'^feeds/$', 'get_feeds'),
    url(r'^(\d+)/follow/$', 'add_friend'),
    url(r'^upload_avatar', 'upload_avatar'),
)
