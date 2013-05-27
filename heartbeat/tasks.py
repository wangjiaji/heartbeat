from celery import task
from models import rserver as redis_server

@task()
def redis_push_list(model, pk, field, data):
    key = '%s:%d:%s' % (model, pk, field)
    redis_server.lpush(key, data)

@task()
def redis_del_list(model, pk, field):
    key = '%s:%d:%s' % (model, pk, field)
    redis_server.delete(key)

@task()
def redis_update_hot_beat():
    key = hot_beats_key()
    pipe = redis.pipeline()
    pipe.delete(key)
    qs = Beat.objects.filter(upload_time__gt=now()-timedelta(days=7)).annotate(nhearts=Count('hearts')).order_by('nhearts').select_related('place')
    for beat in qs:
        pipe.lpush(key, beat.id)
    for beat in qs:
        ckey = hot_beats_by_country_key(beat.place.country)
        pipe.lpush(ckey, beat.id)           
    pipe.execute()
    hot_list_etag(set_id=True)


# Delete this in production environment!!!
@task()
def forge_feeds():
    from accounts.models import User
    pipe = redis_server.pipeline()

    for user in User.objects.only('id').prefetch_related('beats'):
        for beat in user.beats.all().only('id'):
            pipe.lpush('User:1:feeds', '%d:0:%d' % (user.id, beat.id))
    pipe.execute()
