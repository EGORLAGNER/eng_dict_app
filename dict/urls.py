from django.urls import path
from dict.views import *
from django.contrib.auth.views import LoginView, LogoutView

urlpatterns = [
    path('', MainPage.as_view(), name='main_page_url'),
    path('all_words/', all_words, name='all_words_url'),
    # path('setting_learn/', SettingLearn.as_view(), name='setting_learn_url'),
    # path('learn_word/', LearnWords.as_view(), name='learn_word_url'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('profile/', profile, name='profile_url'),
    path('json_backup/', save_json, name='save_json_url'),
    path('del_setting/', del_setting, name='del_setting_url'),
    path('create_word/', create_word, name='create_word_url'),
    path('select_category/', SelectCategory.as_view(), name='select_category_url'),


]
