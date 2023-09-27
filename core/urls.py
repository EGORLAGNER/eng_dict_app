from django.urls import path
from core.views import Index, AllWords

urlpatterns = [
    path('', Index.as_view(), name='main_page_url'),
    path('all_words/', AllWords.as_view(), name='all_words_url'),
]
