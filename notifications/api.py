from tastypie.authorization import DjangoAuthorization
from tastypie.authentication import Authentication
from tastypie.resources import ModelResource
from tastypie import fields
from models import Notification
from accounts.api import UserResource

class NotificationAuthentication(Authentication):
    def is_authenticated(self, request, **kwargs):
        return request.user.is_active

class NotificationResource(ModelResource):
    sender = fields.ForeignKey(UserResource, 'sender', full=True)

    class Meta:
        queryset = Notification.objects.all()
        allowed_methods = ['get', 'patch', 'delete']

    def get_object_list(self, request):
        return super(NotificationResource, self).get_object_list(request).filter(recipient=request.user, is_read=False)