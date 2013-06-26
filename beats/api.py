from django.db.models import Q
from heartbeat.api import SessionModelResource, UserAuthentication, OwnerAuthorization
from tastypie.validation import CleanedDataFormValidation
from tastypie import fields
from tastypie.constants import ALL
from places.api import PlaceResource
from accounts.api import UserResource
from forms import BeatForm
from models import Beat
import geohash

class BeatResource(SessionModelResource):
    validation = CleanedDataFormValidation(form_class=BeatForm)
    readonly_fields = ['upload_time']
    creator = fields.ForeignKey(UserResource, 'creator', full=True)
    place = fields.ForeignKey(PlaceResource, 'place', full=True)
    comments = fields.ToManyField('comments.api.BeatCommentResource', 'comments', full=True, null=True, blank=True)

    class Meta:
        authentication = UserAuthentication()
        authorization = OwnerAuthorization()

        queryset = Beat.objects.all().prefetch_related('comments')
        excludes = ['hearts']

        filtering = {
            'lat': ['exact'],
            'lng': ['exact'],
            'range': ['exact'],
            'geohash': ['exact'],
        }

    def dehydrate(self, bundle):
        # comment_key = beat_comments_key(bundle.obj.id)
        # bundle.data['comments'] = redis.lrange(comment_key, 0, -1)
        heart_key = beat_hearts_key(bundle.obj.id)
        bundle.data['hearts'] = redis.lrange(heart_key, 0, -1)
        return super(BeatResource, self).dehydrate(bundle)

    # def obj_create(self, bundle, request=None, **kwargs):
    #     bundle = super(BeatResource, self).obj_create(bundle, request, **kwargs)
    #     return bundle

    def prepend_urls(self):
        return [url(r'^(?P<resource_name>%s)/(?P<id>\d+)/flag/$' %
                    self._meta.resource_name,
                    self.wrap_view('

    def build_filters(self, filters=None):
        if filters is None:
            filters = {}
        if 'range' in filters:
            ran = int(filters.pop('range')[0])
        else:
            ran = 30
        orm_filters = super(BeatResource, self).build_filters(filters)

        # QueryDict values are always list, get the first item
        lat = orm_filters.pop('lat__exact', (None,))[0]
        lng = orm_filters.pop('lng__exact', (None,))[0]

        if (lat is not None) and (lng is not None):
            gh = geohash.encode_uint64(float(lat), float(lng))
            orm_filters.update({'geohash_exact': gh})

        orm_filters.update({'range': ran})
        return orm_filters

    def apply_filters(self, request, applicable_filters):
        r = applicable_filters.pop('range')
        if not 'geohash__exact' in applicable_filters:
            return super(BeatResource, self).apply_filters(request, applicable_filters)
        gh = long(applicable_filters.pop('geohash__exact'))

        # Use Q object to query the neighbors of the geohash
        qobj = Q()
        for nb in geohash.expand_uint64(gh, r):
            qobj |= Q(geohash__gt=nb[0], geohash__lt=nb[1])
        return super(BeatResource, self).apply_filters(request, applicable_filters).filter(qobj)
