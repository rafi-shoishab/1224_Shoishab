from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Sum
from django.contrib import messages
from decimal import Decimal, InvalidOperation

from .models import AddCash, Expense


def register_view(request):
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')
        confirm = request.POST.get('confirm_password', '')

        if not username or not password or not confirm:
            messages.error(request, 'Please fill all required fields.')
        elif password != confirm:
            messages.error(request, 'Passwords do not match.')
        elif User.objects.filter(username=username).exists():
            messages.error(request, 'Username already taken.')
        else:
            user = User.objects.create_user(username=username, email=email, password=password)
            messages.success(request, 'Account created. Welcome!')
            
            return redirect('login')

    return render(request, 'ManageCash/register.html')


def home_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    return redirect('register')


def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        user_input = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')

        
        try:
            user_obj = User.objects.get(email = user_input)
            user_name = user_obj.username 
        
        except User.DoesNotExist:
            user_name = user_input

        user = authenticate(request, username=user_name, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, f'Welcome back, {user.first_name or user.username}!')
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid username or password.')

    return render(request, 'ManageCash/login.html')


def logout_view(request):
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('login')


@login_required
def dashboard(request):
    user = request.user
    total_cash = AddCash.objects.filter(user=user).aggregate(total=Sum('amount'))['total'] or 0
    total_expense = Expense.objects.filter(user=user).aggregate(total=Sum('amount'))['total'] or 0
    balance = total_cash - total_expense

    # Build unified recent transactions list
    entries = []
    for c in AddCash.objects.filter(user=user).order_by('-datetime')[:10]:
        entries.append({'type': 'income', 'amount': c.amount, 'source': c.source, 'description': c.description or '', 'datetime': c.datetime})
    for e in Expense.objects.filter(user=user).order_by('-datetime')[:10]:
        entries.append({'type': 'expense', 'amount': e.amount, 'description': e.description, 'datetime': e.datetime})
    entries = sorted(entries, key=lambda x: x['datetime'], reverse=True)[:10]

    return render(request, 'ManageCash/dashboard.html', {'total_cash': total_cash, 'total_expense': total_expense, 'balance': balance, 'entries': entries})


@login_required
def profile(request):
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        user = request.user
        if not username:
            messages.error(request, 'Username cannot be empty.')
        elif User.objects.exclude(pk=user.pk).filter(username=username).exists():
            messages.error(request, 'Username already taken.')
        else:
            user.username = username
            user.email = email
            user.save()
            messages.success(request, 'Profile updated.')
            return redirect('profile')

    return render(request, 'ManageCash/profile.html', {'user': request.user})


@login_required
def add_cash(request):
    if request.method == 'POST':
        source = request.POST.get('source', '').strip()
        amount_raw = request.POST.get('amount', '').strip()
        description = request.POST.get('description', '').strip()

        if not source or not amount_raw:
            messages.error(request, 'Source and amount are required.')
        else:
            try:
                amount = Decimal(amount_raw)
            except InvalidOperation:
                messages.error(request, 'Invalid amount format.')
            else:
                AddCash.objects.create(user=request.user, source=source, amount=amount, description=description)
                messages.success(request, 'Cash added successfully.')
                return redirect('dashboard')

    return render(request, 'ManageCash/add_cash.html')


@login_required
def add_expense(request):
    if request.method == 'POST':
        description = request.POST.get('description', '').strip()
        amount_raw = request.POST.get('amount', '').strip()

        if not description or not amount_raw:
            messages.error(request, 'Description and amount are required.')
        else:
            try:
                amount = Decimal(amount_raw)
            except InvalidOperation:
                messages.error(request, 'Invalid amount format.')
            else:
                Expense.objects.create(user=request.user, description=description, amount=amount)
                messages.success(request, 'Expense recorded successfully.')
                return redirect('dashboard')

    return render(request, 'ManageCash/add_expense.html')


@login_required
def transactions(request):
    user = request.user
    items = []
    for c in AddCash.objects.filter(user=user).order_by('-datetime'):
        items.append({'type': 'income', 'amount': c.amount, 'source': c.source, 'description': c.description or '', 'datetime': c.datetime})
    for e in Expense.objects.filter(user=user).order_by('-datetime'):
        items.append({'type': 'expense', 'amount': e.amount, 'description': e.description, 'datetime': e.datetime})
    items = sorted(items, key=lambda x: x['datetime'], reverse=True)
    return render(request, 'ManageCash/transactions.html', {'items': items})
