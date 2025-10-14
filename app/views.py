from django.shortcuts import render
from django.http import HttpResponse

def index(request):
    return render(request, 'main/index.html')

def newQuestion(request):
    return render(request, 'main/ask.html')

def newAnswer(request):
    return render(request, 'main/question.html')

def readTag(request):
    return render(request, 'main/tag.html')

def readSettings(request):
    return render(request, 'main/settings.html')

def logIn(request):
    return render(request, 'main/login.html')

def registrate(request):
    return render(request, 'main/register.html')
