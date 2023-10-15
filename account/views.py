from django.shortcuts import render, redirect
from django.contrib import auth, messages
from .models import Account

# Create your views here.


def loginPage(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        try:
            user = Account.objects.get(email=email)
        except:
            messages.error(request, 'User does not existed.')

        user = auth.authenticate(email=email, password=password)

        if user is not None:
            auth.login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'Invalid login credentials.')
            return redirect('login')
    return render(request, 'account/login.html')


def logoutUser(request):
    auth.logout(request)
    return redirect('home')