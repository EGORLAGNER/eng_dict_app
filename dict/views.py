from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator
from django.shortcuts import render, redirect
from django.views.generic import View

from dict.models import *

from .forms import WordForm, CategoryForm, SelectCategoryForm

from dict.services import services
import random


class StartPage(View):
    """Заглавная страница приложения"""

    def get(self, request):
        text = 'добро пожаловать в приложение для изучения английских слов'
        current_user = request.user
        context = {'context': text, 'user': current_user}
        return render(request, 'dict/start_page.html', context)


class Profile(LoginRequiredMixin, View):
    def get(self, request):
        if request.method == 'GET':
            user_name = request.user.username

            # проверка наличия списка не корректных ответов
            incorrect_answers = request.session.get('incorrect_answers', False)

            # если списка нет, то сгенерировать сохранить
            if not incorrect_answers:
                incorrect_answers = services.generate_incorrect_answers()
                request.session['incorrect_answers'] = incorrect_answers

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
            words = user.words.filter(eng__icontains=search_query).prefetch_related('category')
        else:
            words = user.words.prefetch_related('category').all()

        paginator = Paginator(words, 15)

        page_number = request.GET.get("page")
        page_obj = paginator.get_page(page_number)
        return render(request, 'dict/word/all_user_words.html', {'words': words, 'page_obj': page_obj})

    def post(self, request):
        selected_words = request.POST.getlist('selected_words')
        if request.POST.get('flag_delete_word'):
            words = Word.objects.in_bulk(selected_words)
            for word in words.values():
                word.delete()

        if request.POST.get('flag_set_category_to_word'):
            request.session['flag_set_category_to_word'] = True
            request.session['selected_words'] = selected_words
            return redirect('select_category_url')

        return redirect('all_user_words_url')


class AddCategoriesToWords(LoginRequiredMixin, View):
    def get(self, request):
        selected_categories = request.session.get('selected_categories')
        selected_words = request.session.get('selected_words')
        changed_words = []
        for slug_category in selected_categories:
            obj_category = Category.objects.get(slug=slug_category)
            for word_id in selected_words:
                obj_word = Word.objects.get(id=word_id)
                obj_word.category.add(obj_category)
                obj_word.save()
                if obj_word not in changed_words:
                    changed_words.append(obj_word)

        del request.session['selected_categories']
        del request.session['selected_words']
        del request.session['flag_set_category_to_word']
        return render(request, 'dict/category/add_categories_to_words_confirm.html', {'words': changed_words})


class WordCreate(LoginRequiredMixin, View):

    def get(self, request):
        form = WordForm()
        form.fields['category'].queryset = Category.objects.filter(user=request.user)
        return render(request,
                      'dict/word/create_word.html',
                      {'form': form})

    def post(self, request):
        form = WordForm(request.POST)
        form.fields['category'].queryset = Category.objects.filter(user=request.user)
        if form.is_valid():
            # Создать модель на основе формы, но не сохранять в базу.
            # Позволяет выполнить дополнительные действия с объектом перед сохранением его в базе данных
            word = form.save(commit=False)
            word.user = request.user
            obj_statistics = WordStatistics.objects.create(slug=word.generate_slug())
            word.statistics = obj_statistics
            word.save()

            # валидная форма, показывает сохраненные новые слова
            return render(request,
                          'dict/word/create_word.html',
                          {'word': word})
        # если форма не валидна, то показывает заполненную форму и ошибку
        else:
            return render(request,
                          'dict/word/create_word.html',
                          {'form': form})

            # get запрос показывает пустую форму


class SelectCategory(LoginRequiredMixin, View):
    def get(self, request):
        form = SelectCategoryForm()
        form.fields['categories'].queryset = Category.objects.filter(user=request.user)
        return render(request, 'dict/select_category.html', {'form': form})

    def post(self, request):
        form = SelectCategoryForm(request.POST)
        form.fields['categories'].queryset = Category.objects.filter(user=request.user)  # Динамически задаем queryset
        if form.is_valid():
            categories_obj = form.cleaned_data['categories']
            slug_category = [obj.slug for obj in categories_obj]
            # сохранение выбранных категорий в сессии
            request.session['selected_categories'] = slug_category
        selected_categories = request.session.get('selected_categories')

        # перенаправление на страницу добавления категорий словам
        if request.session.get('flag_set_category_to_word'):
            return redirect('add_categories_to_words_url')

        # перенаправление на страницу изучения слов
        if services.get_flag(request, 'learn_words'):
            return redirect('learn_words_url')

        return render(request, 'dict/select_category.html', {'categories': selected_categories})


class WordChange(LoginRequiredMixin, View):
    def get(self, request, slug):
        word = Word.objects.get(slug=slug)
        form = WordForm(instance=word)
        form.fields['category'].queryset = Category.objects.filter(user=request.user)
        return render(request, 'dict/word/change_word.html', {'form': form})

    def post(self, request, slug):
        word = Word.objects.get(slug=slug)
        form = WordForm(request.POST, instance=word)
        form.fields['category'].queryset = Category.objects.filter(user=request.user)
        if form.is_valid():
            form.save(commit=False)

            # актуализация поля slug в Word после изменения Word
            updated_word_slug = form.instance.generate_slug()
            form.instance.slug = updated_word_slug

            # актуализация поля slug в WordStatistics после изменения Word
            obj_statistics = form.instance.statistics
            obj_statistics.slug = updated_word_slug
            obj_statistics.save()

            form.save()
            return render(request, 'dict/word/change_word.html', {'form': form})
        return render(request, 'dict/word/change_word.html', {'form': form})


class AllUserCategories(LoginRequiredMixin, View):
    def get(self, request):
        categories = Category.objects.filter(user=request.user)
        return render(request, 'dict/category/all_user_categories.html', {'categories': categories})

    def post(self, request):
        categories_to_delete = request.POST.getlist('categories_to_delete')
        obj_to_delete = Category.objects.in_bulk(categories_to_delete)
        for key, value in obj_to_delete.items():
            value.delete()
        return redirect('all_user_categories_url')


class CategoryCreate(LoginRequiredMixin, View):
    def get(self, request):
        form = CategoryForm()
        return render(request, 'dict/category/create_category.html', {'form': form})

    def post(self, request):
        form = CategoryForm(request.POST)
        if form.is_valid():
            category = form.save(commit=False)
            category.user = request.user
            category.save()
            return render(request, 'dict/category/create_category.html', {'category': category})
        return render(request, 'dict/category/create_category.html', {'form': form})


class CategoryChange(LoginRequiredMixin, View):
    def get(self, request, slug):
        category = Category.objects.get(slug=slug)
        form = CategoryForm(instance=category)
        words = category.words.all()
        return render(request, 'dict/category/change_category.html', {'form': form, 'words': words})

    def post(self, request, slug):
        category = Category.objects.get(slug=slug)
        bound_form = CategoryForm(request.POST, instance=category)
        if bound_form.is_valid():
            bound_form.save()
            id_list_words = request.POST.getlist('words_to_delete_from_category')
            if id_list_words:
                words_to_delete = Word.objects.in_bulk(id_list_words)
                for key, value in words_to_delete.items():
                    value.delete()
            return render(request, 'dict/category/change_category.html', {'form': bound_form})
        return render(request, 'dict/category/change_category.html', {'form': bound_form})


class LearWords(LoginRequiredMixin, View):
    """
    Отвечает за основную бизнес логику всего приложения - процесс изучения слов пользователем.

    Процесс изучения слов включает в себя следующие шаги:
    1. Пользователь (User) выбирает категории (categories) для изучения.
    2. Формируется набор данных (dataset), который хранится в сессии.
    """
    def get(self, request):
        # проверка наличия выбранных категорий
        selected_categories = request.session.get('selected_categories', False)
        if not selected_categories:
            # флаг указывает намерения учить слова, необходим для view SelectedCategory
            services.set_flag_true(request, 'learn_words')
            return redirect('select_category_url')

        # набор данных для изучения слов (dataset) не подготовлен
        # или закончились "слова" в списке для изучения
        if (not services.get_flag(request, 'data_ready') or
                services.are_words_exhausted(request)):
            services.generate_dataset(request, selected_categories)
            return redirect('learn_words_url')

        question, correct_answer, answers = services.get_question_and_answers(request)

        return render(request, 'dict/word/learn_words.html', {
            'question': question,
            'correct_answer': correct_answer,
            'answers': answers,
        })


# пользователь выбирает категорию или несколько категорий слов для изучения [храним в сессии]
# достать из базы слова пользователя в соответствии с категориями [
# в соответствии с рейтингом слов составить общий набор из которого будут браться слова для изучения
# взять из набора слово для ВОПРОСА и ПРАВИЛЬНЫЙ ОТВЕТ
# из этого же набора взять 3 слова для неправильных ответов
# увеличить счетчик на +1 в поле ПОКАЗОВ ВСЕГО
# если ответ правильный, то увеличить счетчик на +1 в поле ПРАВИЛЬНЫХ ОТВЕТОВ.
#

# пользователь выбирает категорию или несколько категорий слов для изучения [храним в сессии]
# достать из базы слова пользователя в соответствии с категориями

# достать из слов поля id, eng, rus - сохранить в словарь
# структура хранения word learning data - [ {'id': {eng: fire, rus: огонь}}, {'id': {eng: fire, rus: огонь}}, ]
# сереализивать слова в json

# сгенерировать список не правильных ответов
# сохранить в сессии в view profile, чтобы список генерировался 1 раз при логине пользователя,
# исключая лишние обращения в базу

# взять из набора слово для ВОПРОСА и ПРАВИЛЬНЫЙ ОТВЕТ
# из этого же набора взять 3 слова для неправильных ответов
# увеличить счетчик на +1 в поле ПОКАЗОВ ВСЕГО
# если ответ правильный, то увеличить счетчик на +1 в поле ПРАВИЛЬНЫХ ОТВЕТОВ.
#

# получить категории слов
# сгенерировать дата сет для изучения: generate_dataset
# отдать вопрос и варианты ответов в шаблон: question_and_answer options

def post(self, request):
    pass


class DevDeleteSession(LoginRequiredMixin, View):

    def get(self, request):
        request.session.flush()
        return redirect('start_page_url')
