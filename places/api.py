from heartbeat.api import SessionModelResource, UserAuthentication, OwnerAuthorization
from models import Place
from django.conf.urls import url
from tastypie.exceptions import BadRequest

class PlaceResource(SessionModelResource):  
    class Meta:
        authentication = UserAuthentication()
        authorization = OwnerAuthorization()

        queryset = Place.objects.all()
        filtering = {
            'lng': ['lt', 'gt'],
            'lat': ['lt', 'gt'],
        }

    def dehydrate(self, bundle):
        bundle.data['beats'] = bundle.obj.get_beats()
        return super(PlaceResource, self).dehydrate(bundle)

    def prepend_urls(self):
        return [url(r'^(?P<resource_name>%s)/(?P<places_id>[\w\d_.-]+)/$' %
                    self._meta.resource_name,
                    self.wrap_view('dispatch_detail'),
                    name='api_dispatch_detail')]

    def build_filters(self, filters=None):
        if filters is None:
            return super(PlaceResource, self).build_filters({})
        #geo_filters = super(PlaceResource, self).build_filters(filters)
        print(filters)
        lat1 = filters.get('lat__gt', None)
        lat2 = filters.get('lat__lt', None)
        lng1 = filters.get('lng__gt', None)
        lng2 = filters.get('lng__lt', None)
        print(lat1, lat2, lng1, lng2)
        if (lat1 is None) or (lat2 is None) or (lng1 is None) or (lng2 is None):
            raise BadRequest('All 4 parameters must be supplied')

        # if abs(float(lat2) - float(lat1)) > 0.05 or abs(float(lng2) - float(lng1)) > 0.05:
        #     raise BadRequest('Range for the search is too big')

        return super(PlaceResource, self).build_filters(filters)
