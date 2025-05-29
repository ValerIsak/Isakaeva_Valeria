from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ('username', 'rank_points', 'lives', 'is_staff', 'is_active')
    list_filter = ('is_staff', 'is_active')

    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Game info', {
            'fields': (
                'rank_points', 'lives',
                'current_monster', 'current_location',
                'is_fighting_boss', 'tasks_solved_in_boss_fight',
                'solved_tasks', 
                'theory_questions_seen',
            )
        }),
        ('Permissions', {
            'fields': (
                'is_staff', 'is_active', 'is_superuser',
                'groups', 'user_permissions'
            )
        }),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'username', 'password1', 'password2',
                'rank_points', 'lives',
                'current_monster', 'current_location',
                'is_fighting_boss', 'tasks_solved_in_boss_fight',
                'is_staff', 'is_active'
            )
        }),
    )

    search_fields = ('username',)
    ordering = ('username',)
