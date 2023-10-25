from django.contrib import admin

from dict.models import *

"""Подключение моделей к стандартной админ панели для возможностей создания, редактирования, удаления"""
admin.site.register(Word)
admin.site.register(Part)
