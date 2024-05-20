from django.db import models
from django.contrib.auth import get_user_model

from core.models import PublishedAndCreatedModel
from .constants import MAX_LENGTH_RENDER_TITLE, MAX_LENGTH_TITLE


User = get_user_model()


class Category(PublishedAndCreatedModel, models.Model):
    title = models.CharField('Заголовок', max_length=MAX_LENGTH_TITLE)
    description = models.TextField('Описание')
    slug = models.SlugField(
        'Идентификатор',
        unique=True,
        help_text=('Идентификатор страницы для URL; '
                   'разрешены символы латиницы, цифры, дефис и подчёркивание.')
    )

    class Meta:
        verbose_name = 'категория'
        verbose_name_plural = 'Категории'

    def __str__(self) -> str:
        return self.title[:MAX_LENGTH_RENDER_TITLE]


class Location(PublishedAndCreatedModel, models.Model):
    name = models.CharField('Название места', max_length=MAX_LENGTH_TITLE)

    class Meta:
        verbose_name = 'местоположение'
        verbose_name_plural = 'Местоположения'

    def __str__(self) -> str:
        return self.name[:MAX_LENGTH_RENDER_TITLE]


class Post(PublishedAndCreatedModel, models.Model):
    title = models.CharField('Заголовок', max_length=MAX_LENGTH_TITLE,)
    text = models.TextField('Текст')
    pub_date = models.DateTimeField(
        'Дата и время публикации',
        help_text=('Если установить дату и время в будущем — '
                   'можно делать отложенные публикации.')
    )
    image = models.ImageField('Изображение', blank=True, upload_to='posts_img')
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts',
        verbose_name='Автор публикации',
    )
    location = models.ForeignKey(
        Location,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='posts',
        verbose_name='Местоположение'
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        related_name='posts',
        verbose_name='Категория'
    )

    class Meta:
        verbose_name = 'публикация'
        verbose_name_plural = 'Публикации'
        ordering = ('-pub_date',)

    def __str__(self) -> str:
        return self.title[:MAX_LENGTH_RENDER_TITLE]


class Comment(models.Model):

    text = models.TextField('Текст')
    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name='Добавлено'
    )
    author = models.ForeignKey(
        User, on_delete=models.CASCADE,
        verbose_name='Автор публикации',
        related_name='comments'
    )
    post = models.ForeignKey(
        Post, on_delete=models.CASCADE,
        verbose_name='Публикация',
        related_name='comments'
    )

    class Meta:
        verbose_name = 'коментарий'
        verbose_name_plural = 'коментарии'
        ordering = ('created_at',)
