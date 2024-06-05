from django.urls import path
from dict.views import *

urlpatterns = [
    path('', StartPage.as_view(), name='start_page_url'),

    path('profile/', Profile.as_view(), name='profile_url'),

    path('all_user_words/', AllUserWords.as_view(), name='all_user_words_url'),
    path('create_word/', WordCreate.as_view(), name='create_word_url'),
    path('word/<str:slug>/change/', WordChange.as_view(), name='word_change_url'),

    path('all_user_categories/', AllUserCategories.as_view(), name='all_user_categories_url'),
    path('create_category/', CategoryCreate.as_view(), name='create_category_url'),
    path('category/<str:slug>/change/', CategoryChange.as_view(), name='category_change_url'),

    path('select_category/', SelectCategory.as_view(), name='select_category_url'),
    path('add_categories_to_words/', AddCategoriesToWords.as_view(), name='add_categories_to_words_url'),

    path('learn_words/', LearWords.as_view(), name='learn_words_url'),
    path('learn_words_completed/', LearWordsCompleted.as_view(), name='learn_words_completed_url'),

    path('delete_session/', DevDeleteSession.as_view(), name='delete_session_url'),
]