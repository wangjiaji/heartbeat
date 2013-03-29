from celery import task
from celery.task import periodic_task
from celery.schedules import crontab
from models import rserver as redis_server

@task()
def redis_push_list(model, pk, field, data):
    key = '%s:%d:%s' % (model, pk, field)
    redis_server.lpush(key, data)

@task()
def redis_del_list(model, pk, field):
    key = '%s:%d:%s' % (model, pk, field)
    redis_server.delete(key)


# Delete this in production environment!!!
@periodic_task(run_every=crontab(minute='*/1'))
def forge_feeds():
    from accounts.models import User
    pipe = redis_server.pipeline()

    for user in User.objects.only('id').prefetch_related('beats'):
        for beat in user.beats:
            pipe.lpush('User:7:feeds', '%d:0:%d' % (user.id, beat.id))
    pipe.execute()
