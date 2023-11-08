from django.db import models
from users.models import UserCA
import secrets
from django.utils import timezone
import unidecode


def hard_to_guess(instance, filename):
    hash = secrets.token_hex(16)
    return '/'.join(['artefatosFiles', hash, filename])


RARITY_CHOICES = [(0, "Comum"),
                  (1, "Raro"),
                  (2, "Epico"),
                  (3, "Lendario"),
                  (4, "Unico")]


# Create your models here.
class Artefato(models.Model):
    nome = models.CharField(max_length=100)
    raridade = models.IntegerField(choices=RARITY_CHOICES, verbose_name='Raridade')
    trivia = models.TextField()
    gaba = models.CharField(max_length=300)
    imagemGaba = models.FileField(upload_to=hard_to_guess, blank=True)
    hora_ativo = models.DateTimeField(null=True)
    CA_dono = models.ForeignKey(UserCA, related_name="artefatos", blank=True, null=True, on_delete=models.SET_NULL)
    usado = models.BooleanField(choices=((True, 'Usado'), (False, 'Não Usado')), default=False)

    def save(self, *args, **kwargs):
        if self.CA_dono and not self.CA_dono.is_radio:
            self.CA_dono = UserCA.objects.get(user__username=self.CA_dono.ca_short.lower() + '_capitao')
            if not self.usado:
                ca = self.CA_dono
                ca.timeout_artefato = timezone.now() + timezone.timedelta(hours=4)
                ca.save()
        self.gaba = unidecode.unidecode(self.gaba).lower().replace(' ', '')
        super(Artefato, self).save(*args, **kwargs)

    @property
    def ativo(self):
        if self.hora_ativo is not None:
            return timezone.now() > self.hora_ativo and not self.CA_dono
        return False

    @property
    def filename(self):
        return unidecode.unidecode(self.nome).lower().replace(' ', '') + '.jpg'

    @property
    def encerrado(self):
        return self.CA_dono

    class Meta:
        ordering = ['raridade', 'CA_dono', 'hora_ativo']
