from email.policy import default
from django.db import models
from django.utils import timezone


# Create your models here.
class Desejo(models.Model):
    start_time = models.DateTimeField(null=True, blank=True, verbose_name='Hora de início')
    end_time = models.DateTimeField(null=True, blank=True, verbose_name='Hora de fim')
    texto = models.TextField(verbose_name="Texto")
    pontos = models.IntegerField(default=1)

    def __str__(self):
        return self.texto
