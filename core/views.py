from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.views.generic import View

from core.models import *
from core.services.learn_words import learn_words


class Index(View):
    """Заглавная страница приложения"""

    def get(self, request):
        text = 'Приложение для изучения английских слов'
        context = {'context': text}
        return render(request, 'core/main_page.html', context)


# class AllWords(View):
#     """Показывает все слова имеющиеся в базе данных"""
#
#     def get(self, request):
#         search_query = request.GET.get('search', '')
#         if search_query:
#             word = Word.objects.filter(eng__icontains=search_query)
#         else:
#             word = Word.objects.all()
#         context = {'words': word}
#
#         return render(request, 'core/all_words.html', context)

@login_required
def all_words(request):
    word = Word.objects.filter(user=request.user)
    print(request)
    return render(request, 'core/all_words.html', {'words': word})


def hello_user(request):
    user = request.user
    print(request)
    return render(request, 'core/hello_user.html', {'user': user})


class LearnWords(View):
    """Изучение слов"""

    @login_required
    def get(self, request):
        question, correct_answer, all_answers = learn_words()
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

        if answer_user == correct_answer:
            context = {
                'result': 'Правильный ответ',
            }
        else:
            context = {
                'result': 'НЕ правильный ответ',
            }
        return render(request, 'core/answer.html', context=context)
