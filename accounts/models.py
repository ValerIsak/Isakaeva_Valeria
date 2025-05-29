import random
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.urls import reverse
import uuid
from django.db.models import F
from django.contrib.auth.validators import ASCIIUsernameValidator
from django.core.validators import RegexValidator


# Валидатор: разрешаем только буквы, цифры, пробелы и дефисы в username
username_validator = RegexValidator(
    regex=r'^[\w\s\-]+$',
    message='Имя пользователя может содержать только буквы, цифры, пробелы и дефисы.'
)


class CustomUser(AbstractUser):
    # Переопределяем id на UUID вместо автонумерации
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    # Переопределяем username с нашим валидатором и уникальным ограничением
    username = models.CharField(
        max_length=150,
        unique=True,
        validators=[username_validator],
        error_messages={
            "unique": "Пользователь с таким ФИ уже существует.",
        },
    )

    # Игровые поля
    rank_points = models.PositiveIntegerField(default=0)
    lives = models.PositiveIntegerField(default=5)

    # Поля текущего состояния игры
    current_monster = models.CharField(max_length=100, null=True, blank=True)
    current_location = models.CharField(max_length=100, null=True, blank=True)
    is_fighting_boss = models.BooleanField(default=False)
    tasks_solved_in_boss_fight = models.PositiveIntegerField(default=0)

    # Связи «многие ко многим» для уже решённых задач и просмотренных теоретических вопросов
    solved_tasks = models.ManyToManyField('game.Task', blank=True)
    theory_questions_seen = models.ManyToManyField('game.TheoryQuestion', blank=True, related_name='users_seen')


    # Отображение пользователя по username
    def __str__(self):
        return self.username

    # Уменьшает количество жизней на единицу.
    # Использует F-выражение, чтобы выполнить update на уровне БД без дополнительного SELECT.
    def lose_life(self):
        type(self).objects.filter(pk=self.pk).update(lives=F('lives') - 1)


    # Добавляет одну жизнь.
    # Сохраняет новое значение и сразу обновляет экземпляр из базы.
    def gain_life(self):
        self.lives = F('lives') + 1
        self.save(update_fields=['lives'])
        self.refresh_from_db(fields=['lives'])

    # Увеличивает очки ранга на заданную величину и сохраняет изменение.
    def add_points(self, amount):
        self.rank_points += amount
        self.save(update_fields=['rank_points'])

    # Списывает очки ранга, если их хватает.
    # Возвращает True, если списание прошло успешно, иначе False.
    def spend_points(self, amount):
        if self.rank_points >= amount:
            self.rank_points -= amount
            self.save(update_fields=['rank_points'])
            return True
        return False



