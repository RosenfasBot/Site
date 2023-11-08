from django.contrib import admin
from .models import Gerencial, WebSiteLock

# Register your models here.
admin.site.register(WebSiteLock)
admin.site.register(Gerencial)