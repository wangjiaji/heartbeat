from django.conf.urls import patterns, url

urlpatterns = patterns('beats.views',
    url(r'^upload/$', 'upload_beat'),
    url(r'^(\d+)/heartbeat/$', 'add_heart'),
    url(r'^(\d+)/flag/$', 'flag_beat'),
    url(r'^hot/$', 'get_hot_beats'),
    url(r'^search/(w+)/$', 'search_beat_by_keyword')
)
