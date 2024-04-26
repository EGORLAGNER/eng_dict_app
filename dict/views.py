from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.views.generic import View
# from django.http import HttpResponse

from dict.models import *
from dict.services.learn_words import learn_words, change_rating, get_it_words, get_all_words, get_popular_words
from dict.services.json_import_export import save_backup_json

from .forms import CreatePostForm


class Index(View):
    """Заглавная страница приложения"""

    def get(self, request):
        text = 'Приложение для изучения английских слов'
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
        word = user.word_set.filter(eng__icontains=search_query)
    else:
        word = user.words.all()

    return render(request, 'dict/all_words.html', {'words': word})


def hello_user(request):
    user = request.user
    return render(request, 'dict/hello_user.html', {'user': user})


class SettingLearn(View):
    """Настройки изучения слов"""

    def get(self, request):
        type_learn = request.COOKIES.get('type_learn')

        if type_learn == 'None' or not type_learn:
            settings = []
            all_words_count = Word.objects.all().count()
            if all_words_count > 5:
                settings.append('all')
            it_word_count = Word.objects.filter(is_it=True).count()
            if it_word_count > 5:
                settings.append('it')
            popular_word_count = Word.objects.filter(is_popular=True).count()
            if popular_word_count > 5:
                settings.append('popular')

            return render(request, 'dict/setting_learn.html', {'settings': settings})
        else:
            return redirect('learn_word_url')

    def post(self, request):
        type_learn = request.POST.get('type_learn')

        response = redirect('learn_word_url')  # сохранение куки
        response.set_cookie('type_learn', type_learn)
        return response


class LearnWords(View):
    """Изучение слов"""

    def get(self, request):
        user = request.user
        setting = request.COOKIES.get('type_learn')
        options = {
            'all': get_all_words,
            'it': get_it_words,
            'popular': get_popular_words,
        }
        user_setting_learn = options.get(setting)

        question, correct_answer, all_answers = learn_words(user, user_setting_learn)
        request.session['question'] = question
        request.session['correct_answer'] = correct_answer

        context = {
            'question': question,
            'correct_answer': correct_answer,
            'all_answers': all_answers,
        }

        # return render(request, 'dict/learn_word.html', context)
        return render(request, 'dict/learn_words.html', context)

    def post(self, request):
        answer_user = request.POST.get('answer')
        correct_answer = request.session.get('correct_answer')
        question = request.session.get('question')

        if answer_user == correct_answer:
            change_rating(correct_answer, True)

            return redirect('learn_word_url')
        else:
            change_rating(correct_answer)
            context = {
                'correct_answer': correct_answer,
                'question': question,
            }
            return render(request, 'dict/answer.html', context=context)


# class MyFunc(View):
#     def get(self, request):
#         name_from_cookie = request.COOKIES.get('name', False)   # чтение куки
#
#         if name_from_cookie:
#             response = redirect('learn_word_url')
#             return response
#
#         else:
#             context = {
#                 'name': name_from_cookie
#             }
#             response = render(request, 'core/learn_words.html', context)    # сохранение куки
#             response.set_cookie('name', 'Alex')
#             return response
#

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
        return render(request,
                      'dict/create_word.html',
                      {'form': form})

