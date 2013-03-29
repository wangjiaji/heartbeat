from django.db import models
from django.dispatch import receiver
from django.db.models.signals import post_save
from accounts.models import User
from beats.models import Beat
from heartbeat.models import rserver as redis_server
from heartbeat.tasks import redis_push_list
from celery import task

class BeatComment(models.Model):
    creator = models.ForeignKey(User)
    beat = models.ForeignKey(Beat, related_name='comments')
    text = models.CharField(max_length=128)
    upload_time = models.DateTimeField(auto_now_add=True, editable=False)
    reply_to = models.ForeignKey('self', related_name='replies', blank=True, null=True)

@receiver(post_save, sender=BeatComment)
def update_comment_list(sender, instance, created, **kwargs):
    if created:
        redis_push_list('Beat', instance.beat_id, 'comments', instance.id)
