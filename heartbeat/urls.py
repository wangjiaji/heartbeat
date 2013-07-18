from django.conf.urls import patterns, include, url
from django.views.generic import TemplateView
from tastypie.api import Api
from accounts.api import UserResource
from beats.api import BeatResource
from places.api import PlaceResource
from comments.api import BeatCommentResource
from notifications.api import NotificationResource

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

# Api registration
v1_api = Api(api_name='v1')
v1_api.register(UserResource())
v1_api.register(BeatResource())
v1_api.register(PlaceResource())
v1_api.register(BeatCommentResource())
v1_api.register(NotificationResource())

urlpatterns = patterns('',
    # Examples:
    url(r'^$', TemplateView.as_view(template_name='index.html', name='home')),
    url(r'^accounts/', include('accounts.urls')),
    url(r'^beats/', include('beats.urls')),
    url(r'^api/', include(v1_api.urls)),
    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
)
