from account.models import User
from django.db import models
from django.utils.text import slugify
from django.core.validators import MinValueValidator, MaxValueValidator


def gen_slug(string):
    """Генерирует slug, убирая не допустимые символы"""
    slug = slugify(string, allow_unicode=True)
    return slug


class Word(models.Model):
    """Модель описывающая слова - англ. и рус. значения"""

    user = models.ForeignKey(User,
                             on_delete=models.CASCADE,
                             related_name='words'
                             )

    category = models.ManyToManyField('Category',
                                      blank=True,
                                      related_name='words')

    eng = models.CharField(max_length=255)
    rus = models.CharField(max_length=255,
                           null=True,
                           blank=True
                           )
    description = models.TextField(max_length=255,
                                   null=True,
                                   blank=True
                                   )
    association = models.TextField(max_length=255,
                                   null=True,
                                   blank=True
                                   )
    rating = models.SmallIntegerField(default=0,
                                      validators=(MinValueValidator, MaxValueValidator,)
                                      )
    is_learned = models.BooleanField(default=False)
    slug = models.SlugField(max_length=150,
                            unique=True,
                            blank=True
                            )

    def __str__(self):
        """Определяет то, как будет отображаться экземпляр в админ панели и консоли"""
        if self.rus:
            return f"{self.eng.lower()} - {self.rus}"
        if not self.rus:
            return f"{self.eng.lower()}"

    def save(self, *args, **kwargs):
        """Переопределяет метод save"""
        if not self.id:
            self.slug = f'{self.user.custom_id}_{slugify(self.eng)}'
        super().save(*args, **kwargs)

    class Meta:
        """Сортировка по рейтингу. Чем ниже рейтинг, тем выше в списке"""
        ordering = ['eng']


class Category(models.Model):
    user = models.ForeignKey(User,
                             on_delete=models.CASCADE,
                             related_name='categories')

    name = models.CharField(max_length=255,
                            unique=True)

    slug = models.SlugField(max_length=255,
                            unique=True,
                            blank=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        """Переопределяет метод save"""
        if not self.id:
            self.slug = f'{self.user.custom_id}_{slugify(self.name)}'
        super().save(*args, **kwargs)
