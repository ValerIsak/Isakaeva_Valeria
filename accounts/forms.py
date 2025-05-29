from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.forms import AuthenticationForm
from .models import CustomUser


# Форма регистрации нового пользователя
class CustomUserCreationForm(forms.ModelForm):
    # Поле username с индивидуальными параметрами отображения
    username = forms.CharField(
        label='', # скрываем стандартную метку
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={
            'placeholder': 'Фамилия Имя',
            'class': 'transparent-centered-input',
            'autocomplete': 'off'
        })
    )

    # Первое поле пароля
    password1 = forms.CharField(
        label='',
        required=True,
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Пароль',
            'class': 'transparent-centered-input',
            'autocomplete': 'off'
        })
    )

    # Повторное поле пароля для проверки совпадения
    password2 = forms.CharField(
        label='',
        required=True,
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Подтверждение пароля',
            'class': 'transparent-centered-input',
            'autocomplete': 'off'
        })
    )

    class Meta:
        model = CustomUser # связанная модель
        fields = ('username',) # заполняем только имя (пароли обрабатываются отдельно)

    # Проверка на уникальность имени пользователя
    def clean_username(self):
        username = self.cleaned_data['username']
        if CustomUser.objects.filter(username=username).exists():
            raise forms.ValidationError("Пользователь с таким ФИ уже существует.")
        return username

    # Проверка совпадения паролей
    def clean(self):
        cleaned = super().clean()
        p1 = cleaned.get('password1')
        p2 = cleaned.get('password2')
        if p1 and p2 and p1 != p2:
            self.add_error('password2', "Пароли не совпадают.")
        return cleaned
    
    # Устанавливаем пароль и сохраняем пользователя
    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password1'])
        if commit:
            user.save()
        return user




# Форма авторизации пользователя
class CustomLoginForm(AuthenticationForm):
    username = forms.CharField(
        label='',
        widget=forms.TextInput(attrs={
            'placeholder': 'Фамилия Имя',
            'class': 'transparent-centered-input'
        })
    )
    password = forms.CharField(
        label='',
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Пароль',
            'class': 'transparent-centered-input'
        })
    )