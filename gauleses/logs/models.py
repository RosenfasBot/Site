from django.db import models
from users.models import User


class Log(models.Model):
    timestamp = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(User, related_name='ações', null=True, on_delete=models.SET_NULL, default=1)
    ip = models.CharField(max_length=100)
    request = models.TextField()
    safe = models.BooleanField(default=False)

    class Meta:
        ordering = ['-timestamp']
