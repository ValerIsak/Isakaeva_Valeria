from django.forms.models import BaseInlineFormSet
from django.core.exceptions import ValidationError

class ChoiceOptionInlineFormSet(BaseInlineFormSet):
    def clean(self):
        super().clean()

        if not hasattr(self.instance, 'question_type'):
            return  # ещё не выбран тип вопроса

        if self.instance.question_type == 'choice':
            count = 0
            for form in self.forms:
                if form.cleaned_data and not form.cleaned_data.get('DELETE', False):
                    if form.cleaned_data.get('text'):
                        count += 1

            if count != 2:
                raise ValidationError('Для типа "Выбор варианта" нужно указать ровно 2 варианта ответа.')
