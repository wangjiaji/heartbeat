from django.db import models
from accounts.models import User

class Notification(models.Model):
    note_type_choices = (
        (0, 'friend'),
        (1, 'comment'),
        (2, 'heart')
    )

    sender = models.ForeignKey(User, related_name='+')
    note_type = models.SmallIntegerField()
    recipient = models.ForeignKey(User, related_name='notifications')
    subject_id = models.PositiveIntegerField()
    content = models.CharField(max_length=20, null=True, blank=True)
    is_read = models.BooleanField(default=False)

    def __unicode__(self):
        return "note %d" % self.id
