from django.shortcuts import render
from django.contrib.auth.decorators import login_required

def welcome_view(request):
    return render(request, 'pages/welcome.html')

def lore_view(request):
    return render(request, 'pages/lore.html')

def rules_view(request):
    return render(request, 'pages/rules.html')
