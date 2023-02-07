import datetime as dt

from django.core.validators import MaxValueValidator
from django.db import models
from users.models import User


class Category(models.Model):
    """Модель категории произведения."""

    name = models.CharField(max_length=50)
    slug = models.SlugField(unique=True)


class Genre(models.Model):
    """Модель жанра произведения."""

    name = models.CharField(max_length=50)
    slug = models.SlugField(unique=True)


class Title(models.Model):
    """Модель произведения."""

    name = models.CharField(
        max_length=100,
        help_text='Название произведения'
    )
    year = models.IntegerField(
        validators=[
            MaxValueValidator(dt.datetime.now().year)
        ],
        help_text='Дата'
    )
    description = models.TextField(
        null=True,
        blank=True,
        help_text='Описание'
    )
    genre = models.ManyToManyField(
        Genre,
        verbose_name='Произведение',
        related_name='genre',
        blank=True
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        verbose_name='Категория',
        related_name='category',
    )

    def __str__(self):

        return self.name


class Review(models.Model):
    """Модель отзыва на произведение."""

    RATE_CHOICES = zip(range(1, 11), range(1, 11))
    title = models.ForeignKey(
        Title,
        on_delete=models.CASCADE,
        verbose_name='Произведение',
        related_name='review'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор',
        related_name='review'
    )
    text = models.TextField(
        verbose_name='Отзыв'
    )
    pub_date = models.DateField(
        auto_now_add=True,
        verbose_name='Дата публикации'
    )
    score = models.IntegerField(choices=RATE_CHOICES, default=1)

    class Meta:
        ordering = ['-pub_date']
        constraints = [
            models.UniqueConstraint(
                fields=['author', 'title'],
                name='unique_author_title_review'
            )
        ]

    def __str__(self):
        return self.text


class Comment(models.Model):
    """Модель комментария к отзыву."""

    review = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
        verbose_name='Отзыв',
        related_name='comments',
        blank=True,
        null=True
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор',
        related_name='comments',
        blank=True,
        null=True
    )
    pub_date = models.DateField(
        auto_now_add=True,
        verbose_name='Дата публикации'
    )
    text = models.TextField(
        verbose_name='Текст комментария'
    )

    class Meta:
        ordering = ['-pub_date']
