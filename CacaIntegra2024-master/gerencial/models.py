from django.db import models
from django.utils import timezone

class WebSiteLock(models.Model):
    lock_type = models.IntegerField(choices=[(0,'Soft'), (1,'Hard')], default=0, help_text="Soft bloqueia só CAs, Hard bloqueia a CO inteira")
    start_time = models.DateTimeField(null=True, blank=True)
    end_time = models.DateTimeField(null=True, blank=True)
    def save(self, *args, **kwargs):
        if not self.start_time:
            self.start_time = timezone.now()
        super(WebSiteLock, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        self.end_time = timezone.now()
        super().save()


    class Meta:
        verbose_name_plural = "WebSiteStatus"


class SingletonModel(models.Model):
    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        self.pk = 1
        super(SingletonModel, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        pass

    @classmethod
    def load(cls):
        obj, created = cls.objects.get_or_create(pk=1)
        return obj

class Gerencial(SingletonModel):
    _singleton = models.BooleanField(default=True, editable=False, unique=True)
    _old_caca_start = models.BooleanField(default=False)
    caca_start = models.BooleanField(default=False, verbose_name="Caça começou")
    tempos_dica = models.CharField(default="5, 9, 12", max_length=20, verbose_name="Horários de dica", help_text="Separados por vírgula e contados do início da pista em horas (ex.: 5, 9, 12)")
    timeout_extravio = models.IntegerField(default=2,verbose_name="Timeout por Extravio",  help_text="Tempo em minutos")
    timeout_typo = models.IntegerField(default=2,verbose_name="Timeout por Typo", help_text="Tempo em minutos")
    timeout_merda = models.IntegerField(default=20,verbose_name='Timeout por "Fazer Merda"', help_text="Tempo em minutos")
    timeout_precaca = models.IntegerField(default=24*60,verbose_name="Timeout por Pré-Caça", help_text="Tempo em minutos")
    telegram_bottoken = models.CharField(default='', max_length=200, verbose_name="Token do Bot do Telegram", blank=True)
    telegram_group = models.IntegerField(default=0, verbose_name="ID da conversa do Telegram")
    
    class Meta:
        verbose_name_plural = "Gerencial"
    
    def save(self, *args, **kwargs):
        if self.caca_start and not self._old_caca_start:
            from caminhos.models import Caminho
            from fila.models import Fila
            for cam in Caminho.objects.all():
                fp = cam.pistas.first()
                if not fp:
                    fila = Fila.load()
                    proxima_pista = fila.get_proxima_pista(cam)
                    proxima_pista.hora_inicio = timezone.now()
                    proxima_pista.caminho = cam
                    proxima_pista.save()
                    fp = proxima_pista
                if not fp.hora_inicio:
                    fp.hora_inicio = timezone.now()
                    fp.save()
        if not self.caca_start and self._old_caca_start:
            from caminhos.models import Caminho
            for cam in Caminho.objects.all():
                fp =cam.pistas.first()
                if fp:
                    fp.hora_inicio = None
                    fp.save()
        
        self._old_caca_start=self.caca_start
        super(Gerencial, self).save(*args, **kwargs)
