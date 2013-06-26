from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from heartbeat.models import BaseModel

class User(AbstractUser, BaseModel):
    _GENER_CHOICES = (
        ('M', 'Male'),
        ('F', 'Female'),
    )
    
    # Profile
    display_name = models.CharField(max_length=64, blank=True)
    avatar = models.ImageField(upload_to='avatars', blank=True, null=True)

    gender = models.CharField(max_length=1, choices=_GENER_CHOICES, null=True)
    birthdate = models.DateField(null=True)
    country = models.CharField(max_length=3, blank=True)
    state = models.CharField(max_length=20, blank=True)
    city = models.CharField(max_length=30, blank=True)
    address = models.CharField(max_length=200, blank=True)
    zipcode = models.CharField(max_length=15, blank=True)

    followed_users = models.ManyToManyField('self', related_name='followers', editable=False, blank=True, symmetrical=False, null=True)
    level_points = models.PositiveIntegerField(default=0, editable=False)
    introduction = models.CharField(max_length=140, blank=True)

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
        return list(self.get_redis_set('followed_users'))

    def get_followers(self):
        return list(self.get_redis_set('followers'))

    def get_beats(self):
        return self.get_redis_list('beats')

    def get_heartbeats(self):
        return list(self.get_redis_set('heartbeats'))

    def is_following(self, user):
        return user.is_member('followers', self.id)

    def follow(self, user):
        self.followed_users.add(user)
        self.add_redis_set('followed_users', user.id)
        user.add_redis_set('followers', self.id)

    def unfollow(self, user):
        self.followed_users.remove(user)
        self.remove_redis_set.delay('followed_users', user.id)
        user.remove_redis_set.delay('followers', self.id)

    def get_feeds(self, *args, **kwargs):
        feeds = self.get_redis_list('feeds', *args, **kwargs)
        return feeds

    def distribute_feed(self, beatid, feed_type=0):
        followers_pks = self.get_followers()
        followers_pks.append(str(self.id))
        keys = [':'.join((self.__class__.__name__, pk, 'feeds')) for pk in followers_pks]
        feed = ':'.join((str(self.id), str(feed_type), str(beatid)))
        self.distribute_redis_value.delay(keys, feed)

    def add_heart(self, beat):
        self.add_redis_set('heartbeats', beat.id)
        self.distribute_feed(beat.id, 1)

    def del_heart(self, beat):
        self.remove_redis_set.delay('heartbeats', beat.id)

    def get_places(self):
        return list(self.get_redis_set('places'))

    def add_place(self, placeid):
        self.add_redis_set('places', placeid)
        
    def send_notification(self, recepient, title, text):
        pass


    @models.permalink
    def get_absolute_url(self):
        return ('accounts.views.details', [str(self.id)])


