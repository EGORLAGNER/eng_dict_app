from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator
from django.shortcuts import render, redirect
from django.views.generic import View
from .forms import SelectCategoryForm

from dict.models import *
from dict.services.json_import_export import save_backup_json

from .forms import CreateWordForm, WordDetailForm


class MainPage(View):
    """Заглавная страница приложения"""

    def get(self, request):
        text = 'Добро пожаловать в приложение для изучения английских слов'
        current_user = request.user
        context = {'context': text, 'user': current_user}
        return render(request, 'dict/main_page.html', context)


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


class WordCreate(LoginRequiredMixin, View):
    def post(self, request):
        form = CreateWordForm(request.POST)
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

    def get(self, request):
        form = CreateWordForm()
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


class Profile(LoginRequiredMixin, View):
    def get(self, request):
        if request.method == 'GET':
            user_name = request.user.username
            return render(request, 'dict/profile.html', context={'user_name': user_name})

        if request.method == 'POST':
            pass


class AllUserWords(LoginRequiredMixin, View):
    """
    В get отображает список всех слов пользователя с чекбоксами.
    В post удаляет отмеченные слова.
    """

    def get(self, request):
        user = request.user
        search_query = request.GET.get('search', '')
        if search_query:
            words = user.words.filter(eng__icontains=search_query)
        else:
            words = user.words.prefetch_related('category').all()

        paginator = Paginator(words, 15)

        page_number = request.GET.get("page")
        page_obj = paginator.get_page(page_number)

        return render(request, 'dict/all_user_words_pagination.html', {'words': words, 'page_obj': page_obj})

    def post(self, request):
        words_id_to_delete = request.POST.getlist('words_to_delete')
        obj_to_delete = Word.objects.in_bulk(words_id_to_delete)
        for key, value in obj_to_delete.items():
            value.delete()
        return redirect('all_user_words_url')


class WordDetail(LoginRequiredMixin, View):
    def get(self, request, slug):
        word = Word.objects.get(slug=slug)
        form = WordDetailForm(instance=word)
        form.fields['category'].queryset = Category.objects.filter(user=request.user)
        return render(request, 'dict/word_detail.html', {'form': form, 'word': word})


class WordChange(LoginRequiredMixin, View):
    def get(self, request, slug):
        word = Word.objects.get(slug=slug)
        form = WordDetailForm(instance=word)
        form.fields['category'].queryset = Category.objects.filter(user=request.user)
        return render(request, 'dict/word_change.html', {'form': form})

    def post(self, request, slug):
        word = Word.objects.get(slug=slug)
        form = WordDetailForm(request.POST, instance=word)
        form.fields['category'].queryset = Category.objects.filter(user=request.user)
        if form.is_valid():
            form.save()
            return render(request, 'dict/word_change.html', {'form': form})
        return render(request, 'dict/word_change.html', {'form': form})
