from django.db import models
from django.contrib.auth import get_user_model

from core.models import  CreatedAt, IsPublishedCreatedAt
from .constants import MAX_LENGTH_RENDER_TITLE, MAX_LENGTH_TITLE


User = get_user_model()


class Category(IsPublishedCreatedAt):
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


class Location(IsPublishedCreatedAt):
    name = models.CharField('Название места', max_length=MAX_LENGTH_TITLE)

    class Meta:
        verbose_name = 'местоположение'
        verbose_name_plural = 'Местоположения'

    def __str__(self) -> str:
        return self.name[:MAX_LENGTH_RENDER_TITLE]


class Post(IsPublishedCreatedAt):
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


class Comment(CreatedAt):

    text = models.TextField('Текст')
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

    class Meta(CreatedAt.Meta):
        verbose_name = 'коментарий'
        verbose_name_plural = 'коментарии'

    def __str__(self) -> str:
        return self.text[:MAX_LENGTH_RENDER_TITLE]
