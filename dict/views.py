from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.views.generic import View
# from django.http import HttpResponse
from .forms import SelectCategoryForm

from dict.models import *
from dict.services.learn_words import learn_words, change_rating, get_it_words, get_all_words, get_popular_words
from dict.services.json_import_export import save_backup_json

from .forms import CreatePostForm


class MainPage(View):
    """Заглавная страница приложения"""

    def get(self, request):
        text = 'Добро пожаловать в приложение для изучения английских слов'
        current_user = request.user
        context = {'context': text, 'user': current_user}
        return render(request, 'dict/main_page.html', context)


@login_required
def all_words(request):
    """Показывает все слова юзера имеющиеся в базе данных и реализует простой поиск в нав бар"""
    user_email = request.user
    search_query = request.GET.get('search', '')
    user = User.objects.get(email=user_email)
    if search_query:
        word = user.words.filter(eng__icontains=search_query)
    else:
        word = user.words.prefetch_related('category').all()

    return render(request, 'dict/all_words.html', {'words': word})


def hello_user(request):
    user = request.user
    return render(request, 'dict/hello_user.html', {'user': user})


def del_setting(request):
    """Удаление настроек изучения."""
    response = redirect('main_page_url')
    response.set_cookie('type_learn', 'None')
    return response


def save_json(request):
    save_backup_json(True)
    return render(request, 'dict/json_save_confirm.html')


def create_word(request):
    if request.method == 'POST':
        form = CreatePostForm(request.POST)
        form.fields['category'].queryset = Category.objects.filter(user=request.user)
        if form.is_valid():
            # Создать модель на основе формы, но не сохранять в базу.
            # Позволяет выполнить дополнительные действия с объектом перед сохранением его в базе данных
            word = form.save(commit=False)
            word.user = request.user
            word.save()

            # валидная форма, показывает сохраненные новые слова
            return render(request,
                          'dict/create_word.html',
                          {'word': word})
        # если форма не валидна, то показывает заполненную форму и ошибку
        else:
            return render(request,
                          'dict/create_word.html',
                          {'form': form})

            # get запрос показывает пустую форму

    else:
        form = CreatePostForm()
        form.fields['category'].queryset = Category.objects.filter(user=request.user)
        return render(request,
                      'dict/create_word.html',
                      {'form': form})


class SelectCategory(View):
    def get(self, request):
        form = SelectCategoryForm()
        form.fields['categories'].queryset = Category.objects.filter(user=request.user)
        return render(request, 'dict/select_category.html', {'form': form})

    def post(self, request):
        form = SelectCategoryForm(request.POST)
        form.fields['categories'].queryset = Category.objects.filter(user=request.user)  # Динамически задаем queryset
        if form.is_valid():
            categories_obj = form.cleaned_data['categories']
            name_category = [obj.name for obj in categories_obj]
            request.session['categories'] = name_category

        return render(request, 'dict/select_category.html')


# class LearnWords(View):
#     """Изучение слов"""
#
#     def get(self, request):
#         user = request.user
#
#         return render(request, 'dict/learn_words.html', context)
#
#     def post(self, request):
#         answer_user = request.POST.get('answer')
#         correct_answer = request.session.get('correct_answer')
#         question = request.session.get('question')
#
#         if answer_user == correct_answer:
#             change_rating(correct_answer, True)
#
#             return redirect('learn_word_url')
#         else:
#             change_rating(correct_answer)
#             context = {
#                 'correct_answer': correct_answer,
#                 'question': question,
#             }
#             return render(request, 'dict/answer.html', context=context)


# class LearnWords(View):
#     """Изучение слов"""
#
#     def get(self, request):
#         user = request.user
#         setting = request.COOKIES.get('type_learn')
#         options = {
#             'all': get_all_words,
#             'it': get_it_words,
#             'popular': get_popular_words,
#         }
#         user_setting_learn = options.get(setting)
#
#         question, correct_answer, all_answers = learn_words(user, user_setting_learn)
#         request.session['question'] = question
#         request.session['correct_answer'] = correct_answer
#
#         context = {
#             'question': question,
#             'correct_answer': correct_answer,
#             'all_answers': all_answers,
#         }
#
#         # return render(request, 'dict/learn_word.html', context)
#         return render(request, 'dict/learn_words.html', context)
#
#     def post(self, request):
#         answer_user = request.POST.get('answer')
#         correct_answer = request.session.get('correct_answer')
#         question = request.session.get('question')
#
#         if answer_user == correct_answer:
#             change_rating(correct_answer, True)
#
#             return redirect('learn_word_url')
#         else:
#             change_rating(correct_answer)
#             context = {
#                 'correct_answer': correct_answer,
#                 'question': question,
#             }
#             return render(request, 'dict/answer.html', context=context)


@login_required
def profile(request):
    if request.method == 'GET':
        user_name = request.user.username
        return render(request, 'dict/profile.html', context={'user_name': user_name})

    if request.method == 'POST':
        pass
