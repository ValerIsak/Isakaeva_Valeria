from django.contrib import admin
import nested_admin
from django.utils.safestring import mark_safe
from .models import Location, Task, Question, ChoiceOption, TheoryQuestion
from .forms import ChoiceOptionInlineFormSet


class ChoiceOptionInline(nested_admin.NestedTabularInline):
    model = ChoiceOption
    formset = ChoiceOptionInlineFormSet
    extra = 2
    max_num = 2
    can_delete = True



class QuestionInline(nested_admin.NestedStackedInline):
    model = Question
    inlines = [ChoiceOptionInline]
    extra = 3
    max_num = 3
    min_num = 1
    verbose_name = 'Вопрос'
    verbose_name_plural = 'Вопросы'



@admin.register(Task)
class TaskAdmin(nested_admin.NestedModelAdmin):
    list_display = ('short_text', 'location', 'difficulty', 'rank_points')
    list_filter = ('location', 'difficulty')
    search_fields = ('text', 'additional_info')
    ordering = ('location', 'difficulty')
    inlines = [QuestionInline]

    readonly_fields = ('mathjax_help', 'mathjax_preview')
    fields = (
        'mathjax_help',
        'mathjax_preview',
        'location', 'text', 'additional_info',
        'difficulty', 'rank_points', 'hint', 'hint_cost',
    )

    def short_text(self, obj):
        return obj.text[:50]
    short_text.short_description = 'Текст задачи'

    def mathjax_help(self, obj=None):
        return mark_safe(
            '<div style="padding:10px;border:1px dashed #ccc;background:#fafafa;">'
            '<strong>MathJax:</strong> \\frac, \\sum, \\sqrt и т.д.'
            '</div>'
        )
    mathjax_help.short_description = 'Подсказка по формулам'

    def mathjax_preview(self, obj=None):
        return mark_safe(
            '<div id="mathjax-preview" '
            'style="min-height:2em;border:1px dashed #ddd;padding:6px;">'
            '</div>'
        )
    mathjax_preview.short_description = 'Превью формул'

    class Media:
        js = [
            'https://polyfill.io/v3/polyfill.min.js?features=es6',
            'https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js',
            'js/preview-mathjax.js',
            'js/admin_dynamic_inlines.js',
        ]


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('short_text', 'task', 'order', 'question_type')
    list_filter = ('task__location', 'question_type')
    search_fields = ('text',)
    ordering = ('task', 'order')

    def short_text(self, obj):
        return obj.text[:50]
    short_text.short_description = 'Текст вопроса'


@admin.register(ChoiceOption)
class ChoiceOptionAdmin(admin.ModelAdmin):
    list_display = ('question', 'text', 'is_correct')
    list_filter = ('is_correct',)
    search_fields = ('text',)
    ordering = ('question',)


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ('name', 'question_count')
    search_fields = ('name',)


@admin.register(TheoryQuestion)
class TheoryQuestionAdmin(admin.ModelAdmin):
    list_display = ('question_preview', 'correct_answer')
    search_fields = ('question',)
    ordering = ('id',)

    def question_preview(self, obj):
        return obj.question[:50]
    question_preview.short_description = 'Текст вопроса'
