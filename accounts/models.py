import random
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.urls import reverse
import uuid
from django.db.models import F
from django.contrib.auth.validators import ASCIIUsernameValidator
from django.core.validators import RegexValidator



username_validator = RegexValidator(
    regex=r'^[\w\s\-]+$',
    message='Имя пользователя может содержать только буквы, цифры, пробелы и дефисы.'
)


class CustomUser(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    username = models.CharField(
        max_length=150,
        unique=True,
        validators=[username_validator],
        error_messages={
            "unique": "Пользователь с таким ФИ уже существует.",
        },
    )

    rank_points = models.PositiveIntegerField(default=0)
    lives = models.PositiveIntegerField(default=5)

    current_monster = models.CharField(max_length=100, null=True, blank=True)
    current_location = models.CharField(max_length=100, null=True, blank=True)
    is_fighting_boss = models.BooleanField(default=False)
    tasks_solved_in_boss_fight = models.PositiveIntegerField(default=0)

    solved_tasks = models.ManyToManyField('game.Task', blank=True)
    theory_questions_seen = models.ManyToManyField('game.TheoryQuestion', blank=True, related_name='users_seen')


    def __str__(self):
        return self.username

    def lose_life(self):
        type(self).objects.filter(pk=self.pk).update(lives=F('lives') - 1)


    def gain_life(self):
        self.lives = F('lives') + 1
        self.save(update_fields=['lives'])
        self.refresh_from_db(fields=['lives'])

    def add_points(self, amount):
        self.rank_points += amount
        self.save(update_fields=['rank_points'])


    def spend_points(self, amount):
        if self.rank_points >= amount:
            self.rank_points -= amount
            self.save(update_fields=['rank_points'])
            return True
        return False


    # def get_absolute_url(self):
    #     return reverse('profile', args=[str(self.id)])
    


