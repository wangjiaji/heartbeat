from django.db import models
from celery.contrib.methods import task
import redis

rserver = redis.Redis(host='localhost', db=1)

class BaseModel(models.Model):
    class Meta:
        abstract = True

    redis_server = rserver

    @classmethod
    def get_global_list(cls, field, start=0, end=-1):
        key = '%s:%s' % (cls.__name__, field)
        return cls.redis_server.lrange(key, start, end)

    def get_redis_key(self, field):
        return ':'.join((self.__class__.__name__, str(self.pk), field))

    def get_redis_set(self, field):
        key = self.get_redis_key(field)
        return list(self.__class__.redis_server.smembers(key))

    @task()
    def add_redis_set(self, field, value):
        key = self.get_redis_key(field)
        self.__class__.redis_server.sadd(key, value)
        
    @task()
    def del_redis_key(self, field):
        key = self.get_redis_key(field)
        self.__class__.redis_server.delete(key)

    def get_redis_list(self, field, start=0, end=-1):
        key = self.get_redis_key(field)
        return self.__class__.redis_server.lrange(key, start, end)

    @task()
    def update_redis_list(self, field):
        key = self.get_redis_key(field)
        manager = getattr(self, field)
        pipe = self.__class__.redis_server.pipeline()
        pipe.delete(key)
        for record in manager.only(self._meta.pk.attname):
            pipe.lpush(record.id)
        pipe.execute()

    @task()
    def push_redis_list(self, field, elt):
        key = self.get_redis_key(field)
        self.__class__.redis_server.lpush(key, elt)

    @task()
    def distribute_redis_value(self, keys, value):
        pipe = self.__class__.redis_server.pipeline()
        for key in keys:
            pipe.lpush(key, value)
        pipe.execute()
