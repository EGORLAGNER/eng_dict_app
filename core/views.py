from django.shortcuts import render
from django.views.generic import View

from core.models import *


class Index(View):
    """Заглавная страница приложения"""

    def get(self, request):
        text = 'Приложение для изучения английских слов'
        context = {'context': text}
        return render(request, 'core/main_page.html', context)


class AllWords(View):
    """Показывает всех работников"""

    def get(self, request):
        search_query = request.GET.get('search', '')
        if search_query:
            word = Word.objects.filter(eng__icontains=search_query)
        else:
            word = Word.objects.all()
        context = {'words': word}

        return render(request, 'core/all_words.html', context)
