from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.utils.translation import ugettext_lazy as _

from .models import User, UserCA, UserCO


class UserAdmin(DjangoUserAdmin):
    """Define admin model for custom User model with no email field."""

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Personal info'), {'fields': ('username',)}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser',
                                       'groups', 'is_CA', 'is_CO', 'user_permissions')}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'is_CA', 'is_CO'),
        }),
    )
    list_display = ('email', 'username', 'is_CA', 'is_CO')
    search_fields = ('email', 'username')
    ordering = ('username',)

admin.site.register(User, UserAdmin)
admin.site.register(UserCA)
admin.site.register(UserCO)
