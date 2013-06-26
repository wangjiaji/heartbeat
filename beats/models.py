from django.db import models
from accounts.models import User
from places.models import Place
from heartbeat.models import BaseModel
from django.db.models.signals import post_save
from django.dispatch import receiver
from heartbeat.tasks import redis_push_list

class Beat(BaseModel):
    creator = models.ForeignKey(User, related_name='beats') # User who created this beat
    title = models.CharField(max_length=128)
    price = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    currency = models.CharField(max_length=3)
    description = models.TextField(blank=True)
    upload_time = models.DateTimeField(auto_now_add=True, editable=False, db_index=True)
    hearts = models.ManyToManyField(User, related_name='heartbeats', blank=True, editable=False)
    place = models.ForeignKey(Place)
    thumbnail = models.ImageField(upload_to='beat_thumb')
    image = models.ImageField(upload_to='beat')
    geohash = models.BigIntegerField(blank=True, db_index=True)

    def __unicode__(self):
        return self.title

    @models.permalink
    def get_absolute_url(self):
        return ('beats.views.details', [str(self.id)])

    def save(self, *args, **kwargs):
        if not self.geohash:
            self.geohash = self.place.geohash
        self.currency = self.currency.upper()
        super(Beat, self).save(*args, **kwargs)

    def add_heart(self, user):
        self.hearts.add(user)
        self.add_redis_set('hearts', user.id)
        user.distribute_feed(self.id, 1)

    def get_hearts(self):
        return list(self.get_redis_set('hearts'))

    def del_heart(self, user):
        self.hearts.remove(user)
        self.remove_redis_set('hearts', user.id)

    def update_tags(self):
        from re import findall
        tags = set(findall(r'(?<=#)\w+\b', self.description))
        keys = ['tag:%s' % tag for tag in tags]
        self.distribute_redis_value(keys, self.id)

@receiver(post_save, sender=Beat)
def update_beat_list(sender, instance, created, **kwargs):
    if created:
        redis_push_list('User', instance.creator_id, 'beats', instance.id)

class Flag(models.Model):
    creator = models.ForeignKey(User, related_name='+')
    beat = models.ForeignKey(Beat, related_name='+')
    reason = models.CharField(max_length=20)
