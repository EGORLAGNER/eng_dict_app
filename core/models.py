from django.contrib.auth.models import User
from django.db import models
from django.utils.text import slugify


def gen_slug(string):
    """Генерирует slug, убирая не допустимые символы"""
    slug = slugify(string, allow_unicode=True)
    return slug


class Part(models.Model):
    """Модель описывающая часть речи"""
    eng = models.CharField(max_length=255, unique=True)
    rus = models.CharField(max_length=255, unique=True)
    description = models.CharField(max_length=255, null=True, blank=True)
    slug = models.SlugField(max_length=150, unique=True, blank=True)

    def __str__(self):
        return f'{self.eng} - {self.rus}'

    def save(self, *args, **kwargs):
        """Переопределяет метод save"""
        if not self.id:
            self.slug = slugify(self.eng)
        super().save(*args, **kwargs)


class Word(models.Model):
    """Модель описывающая слова - англ. и рус. значения"""

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    eng = models.CharField(max_length=255)
    rus = models.CharField(max_length=255)
    description = models.CharField(max_length=255, null=True, blank=True)
    rating = models.SmallIntegerField(default=-1)
    is_popular = models.BooleanField(default=False, blank=True)
    is_visible = models.BooleanField(default=True, blank=True)
    slug = models.SlugField(max_length=150, unique=True, blank=True)

    """Отношения между моделями"""
    part = models.ForeignKey(
        'Part',  # главная модель с которой строятся отношения One to Many
        on_delete=models.SET_NULL,  # обязательный аргумент, поведение при удалении связанного экземпляра
        null=True,
        blank=True,
        related_name='words'  # присваивает связанное имя (если явно не указывать, то сгенерируется автоматически)
    )

    def __str__(self):
        """Определяет то, как будет отображаться экземпляр в админ панели и консоли"""
        return f"({self.eng.title()} - {self.rus.title()})"

    def save(self, *args, **kwargs):
        """Переопределяет метод save"""
        if not self.id:
            self.slug = slugify(self.eng)
        super().save(*args, **kwargs)

    class Meta:
        """Сортировка по рейтингу. Чем ниже рейтинг, тем выше в списке"""
        ordering = ['rating']
