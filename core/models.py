from django.db import models
from django.utils.text import slugify


def gen_slug(string):
    """Генерирует slug, убирая не допустимые символы"""
    slug = slugify(string, allow_unicode=True)
    return slug


class Part(models.Model):
    """Модель описывающая часть речи"""
    name_eng = models.CharField(max_length=255, unique=True)
    name_rus = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return f'{self.name_eng} - {self.name_rus}'


class Word(models.Model):
    """Модель описывающая слова - англ. и рус. значения"""

    eng = models.CharField(max_length=255)
    rus = models.CharField(max_length=255)
    rating = models.SmallIntegerField(default=-1)

    slug = models.SlugField(max_length=150, unique=True, blank=True)

    notes = models.CharField(max_length=255, null=True, blank=True)

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
