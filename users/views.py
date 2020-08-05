from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import UserRegisterForm, LoginForm
from django.contrib.auth import logout, authenticate, login
from django.contrib.auth.models import User
from .models import Trader


# Create your views here.
def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            new_user = User.objects.get(username=username)
            new_trader = Trader(trader=new_user, cash=10000)
            new_trader.save()
            messages.success(request, f'Trading account created for {username}')
            login(request, new_user)
            return redirect('/index')
    else:
        form = UserRegisterForm()
    return render(request, 'users/register.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        form = LoginForm(data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'You are logged in as {username}')
                return redirect('/index')
        else:
            messages.warning(request, 'Your password or username is incorrect.')
    else:
        form = LoginForm()
    return render(request, 'users/login.html', {'form': form})


def logout_view(request):
    logout(request)
    messages.success(request, 'You have successfully logged out.')
    return redirect('/index')
