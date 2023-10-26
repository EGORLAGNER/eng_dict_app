from django.urls import path
from dict.views import Index, LearnWords, all_words, hello_user
from django.contrib.auth.views import LoginView, LogoutView

urlpatterns = [
    path('', Index.as_view(), name='main_page_url'),
    path('all_words/', all_words, name='all_words_url'),
    path('learn_word/', LearnWords.as_view(), name='learn_word_url'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('accounts/profile/', hello_user, name='hello_user_url'),
]
