from django.urls import reverse

from account.models import User
from django.db import models
from django.utils.text import slugify


def gen_slug(string):
    """Генерирует slug, убирая не допустимые символы"""
    slug = slugify(string, allow_unicode=True)
    return slug


class Word(models.Model):
    """Модель описывающая слова - англ. и рус. значения"""

    user = models.ForeignKey(User,
                             on_delete=models.CASCADE,
                             related_name='words',
                             )

    category = models.ManyToManyField('Category',
                                      blank=True,
                                      related_name='words',
                                      verbose_name='категории')

    statistics = models.OneToOneField('WordStatistics',
                                      on_delete=models.CASCADE)

    eng = models.CharField(max_length=255,
                           verbose_name='Английское значение')

    rus = models.CharField(max_length=255,
                           null=True,
                           blank=True,
                           verbose_name='перевод')

    description = models.TextField(max_length=255,
                                   null=True,
                                   blank=True)

    association = models.TextField(max_length=255,
                                   null=True,
                                   blank=True)

    is_learned = models.BooleanField(default=False)
    slug = models.SlugField(max_length=150,
                            unique=True,
                            blank=True)

    def __str__(self):
        """Определяет то, как будет отображаться экземпляр в админ панели и консоли"""
        if self.rus:
            return f"{self.eng.lower()} - {self.rus}"
        if not self.rus:
            return f"{self.eng.lower()}"

    def save(self, *args, **kwargs):
        """Переопределяет метод save"""
        if not self.id:
            self.slug = self.generate_slug()
        super().save(*args, **kwargs)

    def generate_slug(self):
        return f'{self.user.custom_id}_{slugify(self.eng)}'

    def get_absolute_url(self):
        reverse_url = reverse('word_detail_url', kwargs={'slug': self.slug})
        return reverse_url

    def get_change_url(self):
        reverse_url = reverse('word_change_url', kwargs={'slug': self.slug})
        return reverse_url

    class Meta:
        """Сортировка по рейтингу. Чем ниже рейтинг, тем выше в списке"""
        ordering = ['eng']


class Category(models.Model):
    user = models.ForeignKey(User,
                             on_delete=models.CASCADE,
                             null=True,
                             related_name='categories')

    name = models.CharField(max_length=255,
                            verbose_name='название')

    slug = models.SlugField(max_length=255,
                            unique=True,
                            blank=True)

    description = models.TextField(max_length=255,
                                   blank=True,
                                   null=True,
                                   verbose_name='описание')

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        """Переопределяет метод save"""
        if not self.id:
            self.slug = f'{self.user.custom_id}_{slugify(self.name)}'
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        reverse_url = reverse('category_change_url', kwargs={'slug': self.slug})
        return reverse_url

    def get_change_url(self):
        reverse_url = reverse('category_change_url', kwargs={'slug': self.slug})
        return reverse_url


class WordStatistics(models.Model):
    # поле заполняется при сохранении Word в базу
    slug = models.SlugField(max_length=150,
                            blank=True,
                            null=True)

    learning_counter = models.PositiveIntegerField(default=1)
    correct_answer_counter = models.PositiveIntegerField(default=0)
    incorrect_answer_counter = models.PositiveIntegerField(default=0)
    date_added = models.DateField(auto_now_add=True, null=True)
    date_last_learn = models.DateField(auto_now=True, null=True)

    def __str__(self):
        return (
            f'slug: {self.slug} | {self.learning_counter}/{self.correct_answer_counter}/{self.incorrect_answer_counter}')
