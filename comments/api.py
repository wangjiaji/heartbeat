from  heartbeat.api import SessionModelResource, UserAuthentication, OwnerAuthorization
from tastypie import fields
from accounts.api import UserResource
from beats.api import BeatResource
from django.db.models import Q
from models import BeatComment

class CommentAuthorization(OwnerAuthorization):
    def apply_limits(self, request, object_list):
        if request.method == 'DELETE':
            return object_list.filter(Q(creator=request.user) |
                                      Q(beat__creator=request.user))
        else:
            return object_list
            #            return super(CommentAuthorization, self).apply_limits(request, object_list)

class BeatCommentResource(SessionModelResource):
    creator = fields.ForeignKey(UserResource, 'creator', full=True)
    reply_to = fields.ForeignKey('self', 'reply_to', null=True)
    beat = fields.ForeignKey(BeatResource, 'beat')

    class Meta:
        authentication = UserAuthentication()
        authorization = CommentAuthorization()
        queryset = BeatComment.objects.all()
