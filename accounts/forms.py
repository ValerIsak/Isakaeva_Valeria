from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.forms import AuthenticationForm
from .models import CustomUser

class CustomUserCreationForm(forms.ModelForm):
    username = forms.CharField(
        label='',
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={
            'placeholder': 'Фамилия Имя',
            'class': 'transparent-centered-input',
            'autocomplete': 'off'
        })
    )

    password1 = forms.CharField(
        label='',
        required=True,
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Пароль',
            'class': 'transparent-centered-input',
            'autocomplete': 'off'
        })
    )

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
        model = CustomUser
        fields = ('username',)

    def clean_username(self):
        username = self.cleaned_data['username']
        if CustomUser.objects.filter(username=username).exists():
            raise forms.ValidationError("Пользователь с таким ФИ уже существует.")
        return username

    def clean(self):
        cleaned = super().clean()
        p1 = cleaned.get('password1')
        p2 = cleaned.get('password2')
        if p1 and p2 and p1 != p2:
            self.add_error('password2', "Пароли не совпадают.")
        return cleaned

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password1'])
        if commit:
            user.save()
        return user





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