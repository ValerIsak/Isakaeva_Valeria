from django.contrib.auth import login, logout
from django.shortcuts import redirect

from django.views.generic import CreateView
from django.contrib.auth.views import LoginView
from .forms import CustomUserCreationForm, CustomLoginForm
from .models import CustomUser


class SignupPageView(CreateView):
    model = CustomUser
    form_class = CustomUserCreationForm
    template_name = 'accounts/signup.html'
    
    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        return redirect('rules')


class CustomLoginView(LoginView):
    form_class = CustomLoginForm
    template_name = 'accounts/login.html'


def logout_view(request):
    logout(request)
    return redirect('welcome')
