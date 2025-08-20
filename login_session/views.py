from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from chat_app.models import Conversation
from .forms import CustomUserCreationForm

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('chat_app:chat_home')
        else:
            return render(request, 'login_session/authentification.html', {'error': 'Identifiants invalides'})
    return render(request, 'login_session/authentification.html')

def register_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('chat_app:chat_home')
        else:
            return render(request, 'login_session/register.html', {'form': form})
    else:
        form = CustomUserCreationForm()
    return render(request, 'login_session/register.html', {'form': form})