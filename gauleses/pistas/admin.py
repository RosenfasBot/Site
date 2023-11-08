from django.contrib import admin
from pistas.models import Pista, PistaLog, Senha


# Register your models here.
class PistaLogline(admin.TabularInline):
    model = PistaLog

class PistaAdmin(admin.ModelAdmin):
    inlines = [
        PistaLogline,
    ]
    
admin.site.register(Pista, PistaAdmin)
admin.site.register(PistaLog)
admin.site.register(Senha)
