from django.db import models
from django.contrib.auth.models import User
from django.db import models

class Conversation(models.Model):
    participants = models.ManyToManyField(User)
    is_group = models.BooleanField(default=False)
    name = models.CharField(max_length=255, blank=True, null=True) 

    def __str__(self):
        return self.name if self.is_group else "Conversation privée"

class Message(models.Model):
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    read_by = models.ManyToManyField(User, related_name='read_messages', blank=True)

    def __str__(self):
        return f"{self.sender.username}: {self.content[:30]}"