from django.db import models
from accounts.models import User

class MessageManager(models.Manager):
    def inbox(self, user):
        return self.filter(recipient=user, recipient_deleted=False).defer('sender_deleted')

    def outbox(self, user):
        return self.filter(sender=user, sender_deleted=False).defer('is_read', 'recipient_deleted')

class Message(models.Model):
    creator = models.ForeignKey(User, related_name='sent_messages')
    recipient = models.ForeignKey(User, related_name='received_messages')


