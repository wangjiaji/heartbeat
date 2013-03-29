from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.core.files.storage import FileSystemStorage
from heartbeat.models import BaseModel

avatar_fs = FileSystemStorage()

class User(AbstractUser, BaseModel):
    # Profile
    display_name = models.CharField(max_length=64, blank=True)
    avatar = models.ImageField(upload_to='avatars', storage=avatar_fs, blank=True, null=True)

    country = models.CharField(max_length=3, blank=True)
    state = models.CharField(max_length=20, blank=True)
    city = models.CharField(max_length=30, blank=True)
    address = models.CharField(max_length=200, blank=True)
    zipcode = models.CharField(max_length=15, blank=True)

    followed_users = models.ManyToManyField('self', related_name='followers', editable=False, blank=True, symmetrical=False, null=True)
    level_points = models.PositiveIntegerField(default=0, editable=False)

    # Settings
    notify_new_friend = models.BooleanField(default=True)
    notify_comment = models.BooleanField(default=True)
    notify_heart = models.BooleanField(default=False)


    # Social network accounts
    facebook = models.EmailField(null=True, blank=True)

    def __unicode__(self):
        return self.username

    def clean(self):
        if not self.email:
            raise ValidationError('Email address is required')
        try:
            user = User.objects.only('id', 'email').get(email=self.email)
        except self.__class__.DoesNotExist:
            pass
        else:
            if user.id != self.id:
                raise ValidationError('Email address already used')

    def get_followed_users(self):
           return self.get_redis_list('followed_users')


    def get_followers(self):
        return self.get_redis_list('followers')

    def get_beats(self):
        return self.get_redis_list('beats')

    def get_heartbeats(self):
        return self.get_redis_list('heartbeats')

    def is_following(self, user):
        return user.id in self.get_followed_users()

    def follow(self, user):
        self.followed_users.add(user)
        self.push_redis_list('followed_users', user.id)
        user.push_redis_list('followers', self.id)

    def unfollow(self, user):
        self.followed_users.remove(user)
        self.update_redis_list.delay('followed_users')
        user.update_redis_list.delay('followers')

    def get_feeds(self):
        feeds = self.get_redis_list('feeds')
        self.del_redis_key('feeds')
        return feeds

    def distribute_feed(self, beatid, feed_type=0):
        followers_pks = self.get_followers()
        keys = [':'.join((self.__class__.__name__, pk, 'feeds')) for pk in followers_pks]
        feed = ':'.join((str(self.id), str(feed_type), str(beatid)))
        self.distribute_redis_value.delay(keys, feed)


    def add_heart(self, beat):
        self.heartbeats.add(beat)
        self.push_redis_list('heartbeats', beat.id)
        self.distribute_feed(beat.id, 1)

    def del_heart(self, beat):
        self.heartb.remove(user)
        self.update_redis_list.delay('heartbeats')


    def send_notification(self, recepient, title, text):
        pass


    @models.permalink
    def get_absolute_url(self):
        return ('accounts.views.details', [str(self.id)])


