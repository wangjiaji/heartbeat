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

    def dehydrate(self, bundle):
        bundle.data['followers'] = bundle.obj.get_followers()
        bundle.data['followed_users'] = bundle.obj.get_followed_users()
        bundle.data['beats'] = bundle.obj.get_beats()
        bundle.data['heartbeats'] = bundle.obj.get_heartbeats()
        return super(UserResource, self).dehydrate(bundle)
