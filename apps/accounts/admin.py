from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ['username', 'email', 'first_name', 'last_name', 'profession', 'is_author', 'is_staff']
    list_filter = UserAdmin.list_filter + ('is_author',)
    list_editable = ['is_author']
    fieldsets = UserAdmin.fieldsets + (
        ('Muallif huquqi', {
            'fields': ('is_author',)
        }),
        ('Portfolio', {
            'fields': (
                'bio', 'avatar', 'profession', 'phone', 'location', 'skills',
                'github', 'telegram', 'linkedin', 'facebook', 'instagram', 'twitter', 'website',
            )
        }),
    )
