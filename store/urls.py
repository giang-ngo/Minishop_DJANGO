from django.urls import path
from .import views

urlpatterns = [
    path('', views.store, name='store'),
    path('search/', views.search, name='search'),

]
