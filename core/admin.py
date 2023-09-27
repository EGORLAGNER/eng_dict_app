from django.contrib import admin

from core.models import *

"""Подключение моделей к стандартной админ панели для возможностей создания, редактирования, удаления"""
admin.site.register(Word)
admin.site.register(Part)
