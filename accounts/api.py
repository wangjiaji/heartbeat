from django.conf.urls import url
from tastypie import fields
from models import User
from heartbeat.api import SessionModelResource, OwnerAuthorization, UserAuthentication

class AccountAuthorization(OwnerAuthorization):
    limited_methods = ('PUT', 'PATCH')

    def apply_limits(self, request, object_list):
        if request and request.method in self.__class__.limited_methods:
            return object_list.filter(id=request.user.id)
        else:
            return object_list


class UserResource(SessionModelResource):
    class Meta:
        authorization = AccountAuthorization()
        authentication = UserAuthentication()
        queryset = User.objects.all()
        excludes = ['password', 'is_active', 'is_staff', 'is_superuser', 'followed_users']
        allowed_methods = ['get', 'put', 'patch']
        filtering = {
            'username': ('startwith', 'exact'),
        }

    def dehydrate(self, bundle):
        bundle.data['followers'] = bundle.obj.get_followers()
        bundle.data['followed_users'] = bundle.obj.get_followed_users()
        bundle.data['beats'] = bundle.obj.get_beats()
        bundle.data['heartbeats'] = bundle.obj.get_heartbeats()
        bundle.data['places'] = bundle.obj.get_places()
        return super(UserResource, self).dehydrate(bundle)

    def prepend_urls(self):
        return [url(r'^(?P<resource_name>%s)/search/(?P<username>[\w\d_.-]+)/$' %
                    self._meta.resource_name,
                    self.wrap_view('dispatch_detail'),
                    name='api_dispatch_detail')]
