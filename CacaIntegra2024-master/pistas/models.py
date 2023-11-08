from django.db import models
import secrets
from django.utils import timezone
from users.models import User, allRadios
from gerencial.models import Gerencial
from caminhos.utils import check_corte
from caminhos.models import allCaminhos, Caminho
from django.utils.crypto import get_random_string
from datetime import timedelta

tiposPistas = [('Texto', 'Texto'),
               ('HTML', 'HTML'),
               ('Imagem', 'Imagem'),
               ('Áudio', 'Áudio'),
               ('Arquivo', 'Arquivo')]
            
statusPista = [('nao_plantada', "Não Plantada"),
                ('plantada', "Plantada"),
                ('extraviada', "Extraviada"),
                ('recolhida', "Recolhida")]

def hard_to_guess(_instance, filename):
    hash_caminho = secrets.token_hex(16)
    return '/'.join(['pistasFiles', hash_caminho, filename])

class Senha(models.Model):
    # valor: a senha em si (sequência de 8 caracteres)
    valor = models.CharField(max_length=30, blank=True, null=True, unique=True)
    # valida: falso se for uma senha de pré caça ou pista do roubo
    valida = models.BooleanField(default=True)
    # queimado: se a senha já foi testada por um CA (sendo certa ou errada) a CO não pode replantar
    queimada = models.BooleanField(default=False)

    def __str__(self):
        return str(self.valor)

class Pista(models.Model):
    old_senha = models.CharField(max_length=30, blank=True, null=True)
    old_status = models.CharField(choices=statusPista, default='nao_plantada', max_length=30)

    # Controle de caça
    id = models.CharField(max_length=20, primary_key=True, editable=False, unique=True)
    senha = models.OneToOneField(Senha, related_name='pista', blank=True, null=True, on_delete=models.SET_NULL)
    status = models.CharField(choices=statusPista, verbose_name='Status da pista', default='nao_plantada', max_length=30)
    caminho = models.ForeignKey(Caminho, related_name='pistas', on_delete=models.RESTRICT, null=True, blank=True)
    hora_inicio = models.DateTimeField(null=True, blank=True)
    hora_recolhida = models.DateTimeField(null=True, blank=True)
    data_ultima_modificacao = models.DateTimeField(auto_now=True)
    user_ultima_modificacao = models.CharField(max_length=30)

    # Controle de conteudo
    numero = models.IntegerField(unique=True, verbose_name='Número', help_text='Número da pista para controle interno')
    conteudo_texto = models.TextField(blank=True, verbose_name='Conteúdo',
                                      help_text="Conteúdo da pista, caso seja texto")
    tipo_conteudo = models.CharField(choices=tiposPistas, verbose_name='Tipo do conteúdo', default='Texto',
                                     max_length=20)
    arquivo = models.FileField(upload_to=hard_to_guess, blank=True, help_text="Arquivo, se houver")
    autor = models.CharField(max_length=30)

    # Gabarito
    macro = models.CharField(blank=True, verbose_name="Macro da pista", max_length=100)
    micro = models.CharField(blank=True, verbose_name="Micro da pista", max_length=100)
    solucao = models.TextField(blank=True, verbose_name="Resolução esperada")
    observacao = models.TextField(blank=True, verbose_name="Observações sobre como plantar")


    # MISC
    # seção quem pode pegar a pista
    caminhos_possiveis = models.ManyToManyField('caminhos.Caminho', related_name="possiveis_pistas", default=allCaminhos)
    usuarios_possiveis = models.ManyToManyField('users.UserCA', related_name="possiveis_pistas", default=allRadios)

    class Meta:
        ordering=['hora_inicio']

    def __str__(self):
        return "Pista " + str(self.numero)

    def save(self, *args, **kwargs):
        if not self.id:
            self.id = get_random_string(20)

        user = User.objects.filter(username=self.user_ultima_modificacao).first()
        super(Pista, self).save(*args, **kwargs)
        if str(self.senha) != str(self.old_senha):
            logText = 'Senha trocada de ' + str(self.old_senha) + ' para ' + str(self.senha)
            PistaLog(pista=self, texto=logText, user=user).save()    
            self.old_senha = str(self.senha)
            if self.senha:
                self.status = 'plantada'
                super(Pista, self).save(*args, **kwargs)
        if self.status != self.old_status:
            print(self.get_old_status_display(), self.get_status_display())
            logText = 'Status trocado de ' + self.get_old_status_display() + ' para ' + self.get_status_display()
            PistaLog(pista=self, texto=logText, user=user).save()
            self.old_status = self.status
            if self.status == 'recolhida':
                self.hora_recolhida = timezone.now()
                super(Pista, self).save(*args, **kwargs)
                # check_corte(self.papel)
            if self.status == 'extraviada':
                self.senha = None
                super(Pista, self).save(*args, **kwargs)
        elif user and user.is_CA:
            logText = 'Senha tentada pelo ' + str(user)
            PistaLog(pista=self, texto=logText, user=user).save()

    @property
    def nome_arquivo(self):
        return self.arquivo.name.split('/')[-1]

    @property
    def horas_dica(self):
        esquema_dica = [float(x) for x in Gerencial.load().tempos_dica.split(',')]
        if self.caminho.pista_viva == self and self.caminho.ativo and self.hora_inicio:
            horas_dica = [self.hora_inicio+timedelta(hours=esquema_dica[2]),self.hora_inicio+timedelta(hours=esquema_dica[1]),self.hora_inicio+timedelta(hours=esquema_dica[0])]
            return horas_dica
        else:
            return []

    @property
    def next_dicas(self):
        horas_dica = self.horas_dica
        agora = timezone.now()-timezone.timedelta(minutes=20)
        hd = []
        if horas_dica:
            for i in horas_dica:
                if i > agora:
                    hd.append(i)
        return hd
        
class PistaLog(models.Model):
    pista = models.ForeignKey(Pista, related_name='logs', on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    texto = models.CharField(max_length=100, default='')
    user = models.ForeignKey(User, related_name='logs_pista', null=True, on_delete=models.SET_NULL, default=1)

    class Meta:
        ordering = ['-timestamp']
