
from django.db import models


# Модель, представляющая игровую локацию
class Location(models.Model):
    name = models.CharField('Название локации', max_length=255)
    background_image = models.ImageField('Фоновое изображение', upload_to='locations/', blank=True, null=True)
    question_count = models.PositiveSmallIntegerField('Число вопросов в локации', choices=[(1, '1 вопрос'), (2, '2 вопроса'), (3, '3 вопроса')], default=1)

    class Meta:
        verbose_name = 'Локация'
        verbose_name_plural = 'Локации'

    # Возвращает строковое представление с учётом правильного окончания слова "вопрос"
    def __str__(self):
        return f"{self.name} ({self.question_count} вопрос{'а' if self.question_count==2 else 'ов' if self.question_count>2 else ''})"

# Модель задачи, которая решается игроком
class Task(models.Model):
    # Варианты сложности
    DIFFICULTY_CHOICES = [
        ('easy',   'Лёгкий'),
        ('medium', 'Средний'),
        ('boss',   'Босс'),
    ]

    location = models.ForeignKey(Location, on_delete=models.CASCADE, related_name='tasks', verbose_name='Локация')
    text = models.TextField('Текст задачи')
    additional_info = models.TextField('Доп. информация', blank=True, null=True)
    difficulty = models.CharField('Сложность', max_length=10, choices=DIFFICULTY_CHOICES, default='easy')
    is_for_boss = models.BooleanField('Для босса', default=False)
    rank_points = models.PositiveIntegerField('Очки за прохождение')
    hint = models.TextField('Подсказка', blank=True, null=True)
    hint_cost = models.PositiveIntegerField('Стоимость подсказки',default=2)

    class Meta:
        verbose_name = 'Задача'
        verbose_name_plural = 'Задачи'
        ordering = ['location', 'difficulty'] # Сортировка задач по локации и сложности

    def __str__(self):
        # Строковое представление задачи
        return f"{self.location.name}: {self.text[:50]}"

    # Возвращает первые N вопросов, где N = question_count локации.
    def get_questions(self):
        return (self.questions.all().order_by('order')[:self.location.question_count])

# Модель вопроса, связанного с задачей
class Question(models.Model):
    QUESTION_TYPE_CHOICES = [
        ('choice', 'Выбор варианта'), # Вопрос с выбором ответа
        ('input',  'Свободный ввод'), # Вопрос со свободным вводом
    ]

    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='questions', verbose_name='Задача')
    order = models.PositiveIntegerField('Порядок', help_text='Порядковый номер шага в цепочке')
    text = models.TextField('Текст вопроса')
    question_type = models.CharField('Тип вопроса', max_length=10, choices=QUESTION_TYPE_CHOICES, default='choice')
    correct_input = models.CharField('Правильный ответ (для ввода)', max_length=255, blank=True, null=True, help_text='Точное совпадение при вводе')

    class Meta:
        ordering = ['order']
        verbose_name = 'Вопрос'
        verbose_name_plural = 'Вопросы'

    def __str__(self):
        return f"{self.task}: вопрос {self.order}"


# Модель вариантов ответа для вопроса типа "choice"
class ChoiceOption(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='options', verbose_name='Вопрос')
    text = models.CharField('Текст варианта', max_length=255)
    is_correct = models.BooleanField('Правильный вариант', default=False)

    class Meta:
        verbose_name = 'Вариант ответа'
        verbose_name_plural = 'Варианты ответов'

    def __str__(self):
        return self.text

# Модель теоретического вопроса, показываемого между локациями
class TheoryQuestion(models.Model):
    question = models.TextField('Текст теоретического вопроса')
    answer1 = models.CharField('Вариант 1', max_length=255, blank=True, null=True)
    answer2 = models.CharField('Вариант 2', max_length=255, blank=True, null=True)
    answer3 = models.CharField('Вариант 3', max_length=255, blank=True, null=True)
    correct_answer = models.PositiveSmallIntegerField(
        'Правильный вариант',
        choices=[(1, '1'), (2, '2'), (3, '3')],
        default=1
    )

    class Meta:
        ordering = ['id']
        verbose_name = 'Теоретический вопрос'
        verbose_name_plural = 'Теоретические вопросы'

    def __str__(self):
        return self.question[:50] # Показываем первые 50 символов вопроса