import json
from django.db.models import Sum
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
from django.shortcuts import render, redirect
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth import login, logout
from django.contrib.auth.models import User
from django.urls import reverse
from django.contrib.contenttypes.models import ContentType
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required


from app.forms import AnswerForm, QuestionForm, LoginForm, RegisterForm, SettingsForm
from app.models import Like, Profile, Question, Answer, Tag

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
    all_questions = Question.objects.new().prefetch_related('tags').add_vote(request.user)

    page = paginate(request, all_questions)

    return render(request, 'index.html', context={
        'questions': page.object_list,
        'page_obj': page,
        'tags' : Tag.objects.all(),
    })

def newQuestion(request):
    if request.method == 'POST':
        form = QuestionForm(request.POST)

        if form.is_valid():
            data = form.cleaned_data

            question = Question.objects.create(
                title=data['title'],
                text=data['text'],
                user=request.user.profile,
            )

            tags_list = data['tags']

            for tag in tags_list:
                tag_obj, _ = Tag.objects.get_or_create(name=tag)
                question.tags.add(tag_obj)

            return redirect(question)
    else:
        form = QuestionForm()

    return render(request, 'ask.html', {'form': form})


def newAnswer(request, question_id):
    question = get_object_or_404(Question, pk=question_id)

    if request.method == 'POST':
        form = AnswerForm(request.POST)

        if form.is_valid():
            data = form.cleaned_data

            answer = Answer.objects.create(
                text=data['text'],
                user=request.user.profile,
                question=question
            )

            all_answers_count = question.answers.count()
            page_size = 5

            last_page = (all_answers_count + page_size - 1) // page_size

            if last_page < 1: last_page = 1

            question_url = reverse('question', kwargs={'question_id': question.pk})

            redirect_url = f"{question_url}?page={last_page}#answer-{answer.id}"

            return redirect(redirect_url)
    else:
        form = AnswerForm()

    query_set = Question.objects.add_likes().add_vote(request.user)

    question_for_render = get_object_or_404(query_set, pk=question_id)

    answers = question_for_render.answers.new().add_vote(request.user)

    tags = question_for_render.tags.all()

    page = paginate(request, answers)

    return render(request, 'question.html', context={
        'form': form,
        'answers': page.object_list,
        'page_obj': page,
        'question': question_for_render,
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
    user = request.user
    if request.method == 'POST':
        form = SettingsForm(request.POST,request.FILES, user=request.user)

        if form.is_valid():
            data = form.cleaned_data

            if data['username']:
                user.username = data['username']

            if data['email']:
                user.email = data['email']

            user.save()

            if data['nick_name']:
                user.profile.nick_name = data['nick_name']

            if data['avatar']:
                user.profile.avatar = data['avatar']

            user.profile.save()

            return redirect('settings')
    else:
        initial_data = {
            'username': user.username,
            'email': user.email,
            'nick_name': user.profile.nick_name,
        }

        form = SettingsForm(initial=initial_data)
    return render(request, 'settings.html', {'form': form})

def logIn(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)

        if form.is_valid():
            user = form.get_user()

            if user:
                login(request, user)
                return redirect('index')
    else:
        form = LoginForm()

    return render(request, 'login.html', {'form': form})

def logOut(request):
    logout(request)

    return redirect('index')

def registrate(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST, request.FILES)

        if form.is_valid():
            data = form.cleaned_data

            user = User.objects.create_user(
                username=data['username'],
                email=data['email'],
                password=data['password']
            )

            profile = Profile.objects.create(
                user=user,
                nick_name=data['nick_name']
            )

            if data['avatar']:
                profile.avatar = data['avatar']
                profile.save()

            login(request, user)
            return redirect('index')
    else:
        form = RegisterForm()

    return render(request, 'register.html', {'form': form})

def hotQuestion(request):
    hot_questions = Question.objects.best().prefetch_related('tags').add_vote(request.user)

    page = paginate(request, hot_questions)

    return render(request, 'hotquestion.html', context={
        'questions': page.object_list,
        'page_obj': page,
    })

@require_POST
@login_required
def updateLike(request):
    try:
        data = json.loads(request.body)
        object_id = data.get('object_id')
        object_type = data.get('object_type')
        action = data.get('action')
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)

    model_map = {
        'question' : Question,
        'answer' : Answer
    }

    Model = model_map.get(object_type)

    if not Model:
        return JsonResponse({'error': 'Wrong object type'}, status=400)

    user = request.user.profile
    obj = get_object_or_404(Model, pk=object_id)

    content_type = ContentType.objects.get_for_model(obj)

    existing_like = Like.objects.filter(
        user=user,
        content_type=content_type,
        object_id=obj.id,
    ).first()

    new_value = 1 if action == 'like' else -1

    if existing_like:
        if existing_like.value == new_value:
            existing_like.delete()
        else:
            existing_like.value = new_value
            existing_like.save()
    else:
        Like.objects.create(
            content_type=content_type,
            user=user,
            object_id=obj.id,
            value=new_value
        )

    new_rating = obj.likes.aggregate(total = Sum('value'))['total'] or 0
    return JsonResponse({'rating': new_rating})

@require_POST
@login_required
def updateCorrect(request):
    try:
        data = json.loads(request.body)
        answer_id = data.get('answer_id')
        is_correct = data.get('is_correct')
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Wrong object type'}, status=400)

    answer = get_object_or_404(Answer, pk=answer_id)

    question = answer.question

    if (question.user.user != request.user):
        return JsonResponse({'error': 'No permission'}, status=403)

    answer.is_correct = is_correct
    answer.save()

    return JsonResponse({'status': 'ok'}, status=200)
