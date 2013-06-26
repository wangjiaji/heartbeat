from django.db import models
from heartbeat.models import BaseModel
import geohash as geo_hash

class Place(BaseModel):
    places_id = models.CharField(max_length=64, unique=True, primary_key=True)
    places_ref = models.CharField(max_length=256, blank=True)
    lng = models.DecimalField(max_digits=10, decimal_places=7, db_index=True)
    lat = models.DecimalField(max_digits=10, decimal_places=7, db_index=True)
    country = models.CharField(max_length=3, blank=True)
    city = models.CharField(max_length=30, blank=True)
    location = models.CharField(max_length=512, blank=True)
    name = models.CharField(max_length=256, blank=True)
    geohash = models.BigIntegerField(null=True, db_index=True, blank=True)

    def __unicode__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.geohash:
            self.geohash = geo_hash.encode_uint64(self.lat, self.lng)
        super(Place, self).save(*args, **kwargs)

    def add_beat(self, beatid):
        self.add_redis_set('beats', beatid)

    def get_beats(self):
        return list(self.get_redis_set('beats'))
