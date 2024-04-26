from django.contrib import admin

from dict.models import *

"""Подключение моделей к стандартной админ панели для возможностей создания, редактирования, удаления"""
# admin.site.register(Part)
admin.site.register(Category)


class CategoryInline(admin.TabularInline):
    model = Category.words.through
    extra = 1


@admin.register(Word)
class WordAdmin(admin.ModelAdmin):
    list_display = ['user', 'eng', 'rus', 'slug', 'description', 'rating', 'is_learned', 'display_categories', 'association']
    list_filter = ['user']
    search_fields = ['user', 'rus', 'eng', 'description',]
    ordering = ['eng', 'rating']

    inlines = [CategoryInline]

    def display_categories(self, obj):
        return ", ".join([category.name for category in obj.category.all()])

    # prepopulated_fields = {'slug': ('title',)}
    # raw_id_fields = ['author']
    # date_hierarchy = 'publish'
    # ordering = ['status', 'publish']
