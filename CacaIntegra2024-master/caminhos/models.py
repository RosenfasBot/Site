from django.db import models
from users.models import UserCA

BOOL_CHOICES = ((True, 'Ativo'), (False, 'Cortado'))


class Caminho(models.Model):
    nome = models.CharField(max_length=200, unique=True, null=True, blank=True)
    tamanho = models.IntegerField(verbose_name='Quantidade de pistas', default=30)
    # ativo: começa como True, quando o caminho é cortado fica False
    ativo = models.BooleanField(choices=BOOL_CHOICES, default=True)
    CA_ativo = models.ForeignKey(UserCA, related_name="caminhos", blank=True, null=True, on_delete=models.SET_NULL)

    def save(self, *args, **kwargs):
        creation = False
        if not self.id:
            creation = True
        super(Caminho, self).save(*args, **kwargs)
        if creation:
            from pistas.models import Pista
            for p in Pista.objects.all():
                p.caminhos_possiveis.add(self)

    @property
    def pistas_visiveis(self):
        return self.pistas.exclude(hora_inicio__isnull=True)[:self.progresso+1]

    @property
    def pista_viva(self):
        return self.pistas.exclude(status='recolhida').first()
        
    @property
    def progresso(self):
        return len(self.pistas.filter(status='recolhida'))

    def __str__(self):
        return self.nome

    class Meta:
        ordering = ['-ativo', 'nome']

def allCaminhos():
    return Caminho.objects.all()

class Corte(models.Model):
    nivel = models.IntegerField(verbose_name='Nível em que acontece o corte')
    quantidade = models.IntegerField(verbose_name='Quantidade de caminhos que podem existir')
    caminhos_afetados = models.ManyToManyField(Caminho, related_name="cortes", blank=True, default=allCaminhos)

    def delete(self):
        self.caminhos_afetados.clear()
        super().delete()
