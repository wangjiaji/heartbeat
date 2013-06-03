from tastypie.authorization import Authorization
from tastypie.authentication import Authentication
from tastypie.validation import CleanedDataFormValidation
from tastypie.resources import ModelResource

class UserAuthentication(Authentication):
    def is_authenticated(self, request, **kwargs):
        if request.method == 'GET':
            return True
        return request.user.is_authenticated()

class OwnerAuthorization(Authorization):
    limited_methods = ('PUT', 'PATCH', 'DELETE')

    def is_authorized(self, request, obj=None):
        if request.method == 'GET':
            return True
        else:
            return request.user.is_active


    def apply_limits(self, request, object_list):
        if request and request.method in self.__class__.limited_methods:
            return object_list.filter(creator=request.user)
        else:
            return object_list

class SessionModelResource(ModelResource):
    readonly_fields = []
    no_update_fields = []

    def __init__(self, api_name='v1'):
        super(SessionModelResource, self).__init__(api_name)
        for f in self.fields.values():
            if f in self.__class__.readonly_fields:
                self.f.readonly = True

    def hydrate_creator(self, bundle):
        if bundle.request.method == 'POST':
            bundle.data['creator'] =  {'pk': bundle.request.user.pk}
        return bundle

    def hydrate_user(self, bundle):
        if bundle.request.method == 'POST':
            bundle.data['user'] = {'pk': bundle.request.user.pk}
        return bundle

    def hydrate(self, bundle):
        if bundle.obj.pk:
            for f in self.__class__.no_update_fields:
                if bundle.data.get(f, None) is not None:
                    bundle.data[f].pop()
        return super(SessionModelResource, self).hydrate(bundle)
    
def get_api_resource(request, resource, instance):
    ur = resource()
    ur_bundle = ur.build_bundle(obj=instance, request=request)
    return ur.serialize(None, ur.full_dehydrate(ur_bundle), 'application/json')
