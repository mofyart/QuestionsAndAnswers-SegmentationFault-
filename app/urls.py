from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name="index"),
    path('ask/', views.newQuestion, name="ask"),
    path('question/<int:question_id>', views.newAnswer, name="question"),
    path('tag/<int:tag_id>', views.readTag, name="tag"),
    path('settings/', views.readSettings, name="settings"),
    path('login/', views.logIn, name="login"),
    path('register/', views.registrate, name="register"),
    path('hotquestion/', views.hotQuestion, name="hotquestion"),
    path('logout/', views.logOut, name="logout")
]
