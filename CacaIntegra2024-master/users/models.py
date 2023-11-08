from django.contrib.auth.models import AbstractUser
from django.db import models
from itsdangerous import exc
from .managers import UserManager
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone

class User(AbstractUser):
    first_name = None
    last_name = None
    email = models.EmailField(_('email address'), unique=True)

    is_CA = models.BooleanField(verbose_name='Conta de CA',default=False)
    is_CO = models.BooleanField(verbose_name='Conta da CO',default=False)

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    objects = UserManager()

    def __str__(self):
        try:
            if self.is_CA:
                return str(self.userca)
            else:
                return str(self.userco)
        except:
            return self.username

    def save(self, *args, **kwargs):
        if ((not self.is_CA and not self.is_CO) or (self.is_CA and self.is_CO)) and not self.is_superuser and not self.is_staff:
            print('Usuário não criado', self.username, self.is_CA, self.is_CO, self.is_superuser)
        else:
            creation = not self.id
            super(User, self).save(*args, **kwargs)
            if (self.is_CO or self.is_superuser) and creation:
                self.is_CO = True
                UserCO(user=self).save()
                super(User, self).save(*args, **kwargs)
            elif creation:
                self.is_CA = True
                UserCA(user=self).save()
                super(User, self).save(*args, **kwargs)
                from pistas.models import Pista
                for p in Pista.objects.all():
                    p.usuarios_possiveis.add(self)

            try:
                if self.is_CA and self.is_radio:
                    uca = UserCA.objects.get(user=self)
                    uca.is_radio = True
                    uca.radio = uca
                    uca.save()
                if self.is_CA and not self.is_radio and self.radio:
                    uca = UserCA.objects.get(user=self)
                    uca.radio = self.radio
                    uca.save()
            except:
                pass

def allRadios():
    return UserCA.objects.filter(is_radio=True)

class UserCA(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    timeout_until = models.DateTimeField(auto_now_add=True)
    timeout_artefato = models.DateTimeField(auto_now_add=True)

    is_radio = models.BooleanField(default=False)
    radio = models.ForeignKey('users.UserCA', on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        nome = self.user.username.upper().split('_')
        return ' '.join(nome)
    
    @property
    def ca_short(self):
        return str(self).split(' ')[0]
    
    class Meta:
        verbose_name_plural = "Usuários dos CAs"
        verbose_name = "Usuário de CA"
        ordering = ['user__username']

class UserCO(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)

    def __str__(self):
        nome = self.user.username.split('_')
        nome = ' '.join([p.capitalize() for p in nome]).replace('Co', 'CO')
        return nome

    class Meta:
        verbose_name_plural = "Usuários da CO"
        verbose_name = "Usuário da CO"
        ordering = ['user__username']