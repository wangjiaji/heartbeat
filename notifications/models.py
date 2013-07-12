from django.db import models

class Notification(models.Model):
    class Meta:
        ordering = ['-id']
        
    note_type_choices = (
        (0, 'friend'),
        (1, 'comment'),
        (2, 'heart')
    )

    sender = models.ForeignKey('accounts.User', related_name='+')
    note_type = models.SmallIntegerField()
    recipient = models.ForeignKey('accounts.User', related_name='notifications')
    subject_id = models.PositiveIntegerField()
    content = models.CharField(max_length=20, null=True, blank=True)
    is_read = models.BooleanField(default=False)
    time_stamp = models.DateTimeField(auto_now_add=True, editable=False)

    def __unicode__(self):
        return "note %d" % self.id
