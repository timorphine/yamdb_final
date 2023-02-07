from django.contrib import admin

from .models import User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    """Настройка User для панели Admin"""

    list_display = (
        'pk',
        'username',
        'email',
        'role',
        'first_name',
        'last_name',
        'bio',
        'confirmation_code',
    )
    list_filter = ('username', 'role',)
    search_fields = ('username', 'role',)
    list_editable = ('role',)
