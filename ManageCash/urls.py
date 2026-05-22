from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('', views.home_view, name='home'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('profile/', views.profile, name='profile'),
    path('add-cash/', views.add_cash, name='add_cash'),
    path('add-expense/', views.add_expense, name='add_expense'),
    path('transactions/', views.transactions, name='transactions'),
]
