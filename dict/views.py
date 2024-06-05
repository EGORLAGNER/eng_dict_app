from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator
from django.shortcuts import render, redirect
from django.views.generic import View

from dict.models import *
from .forms import WordForm, CategoryForm, SelectCategoryForm
from dict.services.learn_words import services


class StartPage(View):
    """Заглавная страница приложения"""

    def get(self, request):
        text = 'добро пожаловать в приложение для изучения английских слов'
        current_user = request.user
        context = {'context': text, 'user': current_user}
        return render(request, 'dict/start_page.html', context)


class Profile(LoginRequiredMixin, View):
    def get(self, request):
        user_name = request.user.username

        return render(request, 'dict/profile.html', context={'user_name': user_name})


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
            id_words = request.POST.getlist('words_to_delete_from_category')
            if id_words:
                words_to_delete = Word.objects.in_bulk(id_words)
                for key, value in words_to_delete.items():
                    value.delete()
            return render(request, 'dict/category/change_category.html', {'form': bound_form})
        return render(request, 'dict/category/change_category.html', {'form': bound_form})


class LearWords(LoginRequiredMixin, View):
    """
    Отвечает за основную бизнес логику всего приложения - процесс изучения слов пользователем.

    Процесс изучения слов включает в себя следующие шаги:
    При первом обращении к view LearWords:
        - пользователь переадресовывается для выбора категорий/тем слов.
        - на основе выбранных категорий формируется набор данных (dataset),
         который включает в себя:
         - json_words: все изучаемые слова (объекты модели Word) преобразованные в JSON;
         - words_data: список со словарями, что хранят необходимые данные для изучения слов;
         - unsaved_words_statistics: список со словарями, что хранят статистику слов,
           правильных и не правильных ответов данных пользователем.

    При каждом GET запросе проверяется наличие еще не изученных, не показанных слов и наличие набора данных (dataset).
    Если все слова изучены, то статистика по словам обновляется, сохраняется в базе данных.

    Если имеются не изученные слова, то пользователь видит страницу, где имеются:
        - значение слова на изучаемом языке (question)
        - несколько вариантов ответов(в зависимости от выбранной пользователем сложности).
        - возможность увидеть правильный ответ.
    """

    def get(self, request):
        # dataset не создан или закончились "слова"
        if not services.is_created_dataset(request):

            # выбранные пользователем категории слов для изучения
            selected_categories = services.get_selected_categories(request)
            if not selected_categories:
                # флаг используется в view SelectedCategory
                services.set_flag_true(request, 'learn_words')
                return redirect('select_category_url')

            services.create_dataset(request, selected_categories)
            return redirect('learn_words_url')

        if services.is_are_words_exhausted(request):
            redirect('learn_words_completed_url')

        question, correct_answer, answers = services.get_question_and_answers(request)
        services.save_question_and_correct_answer_in_session(request, question, correct_answer)

        return render(request, 'dict/word/learn_words.html', {
            'question': question,
            'correct_answer': correct_answer,
            'answers': answers,
        })

    def post(self, request):
        services.change_words_statistics(request)
        question, correct_answer = services.get_question_and_correct_answer_from_session(request)
        if services.is_user_give_correct_answer(request):
            return render(request, 'dict/word/learn_words_evaluation.html',
                          {'evaluation': 'правильно', 'question': question, 'correct_answer': correct_answer})
        return render(request, 'dict/word/learn_words_evaluation.html',
                      {'evaluation': 'не правильно', 'question': question, 'correct_answer': correct_answer})


class DevDeleteSession(LoginRequiredMixin, View):

    def get(self, request):
        request.session.flush()
        return redirect('start_page_url')


class LearWordsCompleted(LoginRequiredMixin, View):
    """
    Отвечает за сохранение статистики изучения слов в базе данных и вывод результатов обучения.
    Используется, когда:
    - слова закончились или пользователь принудительно завершил процесс;
    - основную бизнес логику всего приложения - процесс изучения слов пользователем;
    """
    def get(self, request):
        if not services.is_created_dataset(request):
            return render(request, 'dict/word/learn_words_result.html',
                          {'message': 'нечего сохранять'})
        (amount_learn_words,
         amount_correct_answers,
         amount_incorrect_answers) = services.updates_words_statistics_in_db(request)
        print('сохранить слова в базе')
        services.set_flag_false(request, 'is_dataset_created')

        return render(request, 'dict/word/learn_words_result.html',
                      {'amount_learn_words': amount_learn_words,
                       'amount_correct_answers': amount_correct_answers,
                       'amount_incorrect_answers': amount_incorrect_answers})
