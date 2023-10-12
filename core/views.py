from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.views.generic import View

from core.models import *
from core.services.learn_words import learn_words, change_rating


class Index(View):
    """Заглавная страница приложения"""

    def get(self, request):
        text = 'Приложение для изучения английских слов'
        current_user = request.user
        context = {'context': text, 'user': current_user}
        return render(request, 'core/main_page.html', context)


# class AllWords(View):
#     """Показывает все слова имеющиеся в базе данных"""
#
#     @login_required
#     def get(self, request):
#         search_query = request.GET.get('search', '')
#         if search_query:
#             word = Word.objects.filter(eng__icontains=search_query)
#         else:
#             word = Word.objects.all()
#         context = {'words': word}
#
#         return render(request, 'core/all_words.html', context)

#


# @login_required
# def all_words(request):
#     word = Word.objects.filter(user=request.user)
#     return render(request, 'core/all_words.html', {'words': word})

@login_required
def all_words(request):
    """Показывает все слова юзера имеющиеся в базе данных и реализует простой поиск в нав бар"""
    user_name = request.user
    search_query = request.GET.get('search', '')
    user = User.objects.get(username=user_name)
    if search_query:
        word = user.word_set.filter(eng__icontains=search_query)
    else:
        word = user.word_set.all()

    return render(request, 'core/all_words.html', {'words': word})


def hello_user(request):
    user = request.user
    return render(request, 'core/hello_user.html', {'user': user})


class LearnWords(View):
    """Изучение слов"""

    def get(self, request):
        user = request.user
        question, correct_answer, all_answers = learn_words(user)
        request.session['question'] = question
        request.session['correct_answer'] = correct_answer

        context = {
            'question': question,
            'correct_answer': correct_answer,
            'all_answers': all_answers,
        }

        # return render(request, 'core/learn_word.html', context)
        return render(request, 'core/learn_words.html', context)

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
            return render(request, 'core/answer.html', context=context)
