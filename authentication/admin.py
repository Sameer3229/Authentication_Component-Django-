
from django.contrib import admin
from .models import User, OneTimePassword


class UserAdmin(admin.ModelAdmin):
    list_display = ('email', 'username', 'is_active', 'is_staff', 'date_joined')
    search_fields = ('email', 'username')
    list_filter = ('is_active', 'is_staff')


class OneTimePasswordAdmin(admin.ModelAdmin):
    list_display = ('user', 'code', 'attempts', 'is_blocked', 'created_at')
    search_fields = ('user__email',) 
    list_filter = ('is_blocked',)


admin.site.register(User, UserAdmin)
admin.site.register(OneTimePassword, OneTimePasswordAdmin)