from django.db import models
from django.contrib.auth.models import User

class Conversation(models.Model):
    participants = models.ManyToManyField(User)
    is_group = models.BooleanField(default=False)
    name = models.CharField(max_length=255, blank=True, null=True) 

    def __str__(self):
        if self.is_group:
            return self.name
        users = self.participants.exclude(id=self.participants.first().id)
        return ", ".join([u.username for u in users])

class Message(models.Model):
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    read_by = models.ManyToManyField(User, related_name='read_messages', blank=True)

    def __str__(self):
        return f"{self.sender.username}: {self.content[:30]}"
