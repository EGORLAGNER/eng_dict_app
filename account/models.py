from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _

from time import time
from random import randint


def _generate_uniq_custom_id():
    """
    Генерирует уникальный ID на основе
    """
    current_time = str(int(time()))
    random_numbers = []

    for _ in range(3):
        random_number = str(randint(0, 9))
        random_numbers.append(random_number)

    custom_id = (current_time +
                 random_numbers[0] +
                 random_numbers[1] +
                 random_numbers[2])

    return custom_id


class User(AbstractUser):
    email = models.EmailField(_('email address'),
                              unique=True)

    custom_id = models.CharField(max_length=14,
                                 primary_key=True,
                                 unique=True)

    USERNAME_FIELD = 'email'  # уникальный идентификатор пользователя
    REQUIRED_FIELDS = ['username']

    def save(self, *args, **kwargs):
        if not self.custom_id:
            self.custom_id = _generate_uniq_custom_id()
        super().save(*args, **kwargs)
