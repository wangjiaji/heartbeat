from django.conf.urls import patterns, url

urlpatterns = patterns('beats.views',
    url(r'^upload/$', 'upload_beat'),
    url(r'^(\d+)/heartbeat/$', 'add_heart'),
    url(r'^hot/$', 'get_hot_beats'),
)
