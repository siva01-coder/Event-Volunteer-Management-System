from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .forms import UserRegisterForm
from django.contrib import messages
from volunteerhub.mongo import users_collection


def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            try:
                users_collection.insert_one({
                    'username': user.username,
                    'email': user.email,
                    'role': user.role,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'date_joined': user.date_joined.isoformat(),
                })
            except Exception as e:
                print('MongoDB insert error:', e)
            messages.success(
                request,
                'Account created successfully! Please log in.'
            )
            return redirect('accounts:login')
    else:
        form = UserRegisterForm()

    return render(request, 'accounts/register.html', {'form': form})


def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, f'Welcome back, {user.username}!')
            # Route based on role
            if user.role == 'admin':
                return redirect('events:admin_dashboard')
            else:
                return redirect('events:volunteer_dashboard')
        else:
            messages.error(request, 'Invalid username or password.')
            return render(request, 'accounts/login.html')

    return render(request, 'accounts/login.html')


@login_required(login_url='/accounts/login/')
def dashboard(request):
    return render(request, 'accounts/dashboard.html')


def user_logout(request):
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('accounts:login')
