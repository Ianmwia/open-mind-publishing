from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Role


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name',)


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'pen_name', 'phone', 'is_staff', 'is_active')
    list_filter = ('is_staff', 'is_active', 'roles')
    search_fields = ('username', 'email', 'pen_name', 'phone')
    filter_horizontal = ('roles', 'groups', 'user_permissions')

    fieldsets = UserAdmin.fieldsets + (
        ('Publishing & Contributor Profile', {
            'fields': (
                'roles',
                'pen_name',
                'phone',
                'bio',
                'address',
                'specialties_or_languages',
                'portfolio_url',
                'emergency_or_agent_contact',
                'image',
                'timezone',
                'is_custom'
            )
        }),
    )