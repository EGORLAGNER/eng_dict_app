from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator
from django.shortcuts import render, redirect
from django.views.generic import View

from dict.models import *

from .forms import WordForm, CategoryForm, SelectCategoryForm


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
        words = Word.objects.in_bulk(selected_words)
        print()
        if request.POST.get('delete'):
            for word in words.values():
                word.delete()
        if request.POST.get('set_category'):
            print('присвоить категорию')

        return redirect('all_user_words_url')


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

# def del_setting(request):
#     """Удаление настроек изучения."""
#     response = redirect('main_page_url')
#     response.set_cookie('type_learn', 'None')
#     return response
#
#
# def save_json(request):
#     save_backup_json(True)
#     return render(request, 'dict/json_save_confirm.html')
