from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from app.models import Question, Answer, Tag


def paginate(request, objects, per_page=5):
    page_num = request.GET.get('page', 1)
    paginator = Paginator(objects, per_page)

    try:
        page = paginator.page(page_num)
    except PageNotAnInteger:
        page = paginator.page(1)
    except EmptyPage:
        page = paginator.page(paginator.num_pages)
    return page


def index(request):
    all_questions = Question.objects.new().prefetch_related('tags')

    page = paginate(request, all_questions)

    return render(request, 'index.html', context={
        'questions': page.object_list,
        'page_obj': page,
        'tags' : Tag.objects.all(),
    })

def newQuestion(request):
    return render(request, 'ask.html')

def newAnswer(request, question_id):
    query_set = Question.objects.add_likes()

    question = get_object_or_404(query_set, pk=question_id)

    answers = question.answers.best()

    tags = question.tags.all()

    page = paginate(request, answers)

    return render(request, 'question.html', context={
        'answers': page.object_list,
        'page_obj': page,
        'question': question,
        'tags' : tags
    })

def readTag(request, tag_id):
    tag = get_object_or_404(Tag, pk=tag_id)

    questions_tag = tag.questions.best().prefetch_related('tags')

    page = paginate(request, questions_tag)

    return render(request, 'tag.html', context={
        'questions': page.object_list,
        'page_obj': page,
        'tag_title': tag.name,
    })

def readSettings(request):
    return render(request, 'settings.html')

def logIn(request):
    return render(request, 'login.html')

def registrate(request):
    return render(request, 'register.html')

def hotQuestion(request):
    hot_questions = Question.objects.best().prefetch_related('tags')

    page = paginate(request, hot_questions)

    return render(request, 'hotquestion.html', context={
        'questions': page.object_list,
        'page_obj': page,
    })
