from django.urls import path
from . import views

urlpatterns = [
    path('', views.index),
    path('ask/', views.newQuestion),
    path('question/', views.newAnswer),
    path('tag/', views.readTag),
    path('settings/', views.readSettings),
    path('login/', views.logIn),
    path('register/', views.registrate),
]
