from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser


# Регистрируем кастомного пользователя в административной панели
@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    model = CustomUser # указываем связанную модель
    # Отображаемые поля в списке пользователей
    list_display = ('username', 'rank_points', 'lives', 'is_staff', 'is_active')
     # Фильтры справа
    list_filter = ('is_staff', 'is_active')

    # Группировка полей при редактировании пользователя
    fieldsets = (
        # Стандартные поля авторизации
        (None, {'fields': ('username', 'password')}),
        # Блок с игровыми данными
        ('Game info', {
            'fields': (
                'rank_points', 'lives',
                'current_monster', 'current_location',
                'is_fighting_boss', 'tasks_solved_in_boss_fight',
                'solved_tasks', 
                'theory_questions_seen',
            )
        }),
        # Стандартные разрешения
        ('Permissions', {
            'fields': (
                'is_staff', 'is_active', 'is_superuser',
                'groups', 'user_permissions'
            )
        }),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )

    # Конфигурация формы создания нового пользователя в админке
    add_fieldsets = (
        (None, {
            'classes': ('wide',), # применяем css-класс wide для широкой формы
            'fields': (
                'username', 'password1', 'password2',
                'rank_points', 'lives',
                'current_monster', 'current_location',
                'is_fighting_boss', 'tasks_solved_in_boss_fight',
                'is_staff', 'is_active'
            )
        }),
    )

    # Поиск пользователей по имени
    search_fields = ('username',)
    # Сортировка по имени пользователя
    ordering = ('username',)
