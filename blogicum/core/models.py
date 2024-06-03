from django.db import models


class CreatedAt(models.Model):
    created_at = models.DateTimeField('Добавлено', auto_now_add=True)

    class Meta:
        abstract = True
        ordering = ('created_at',)


class IsPublishedCreatedAt(CreatedAt):
    is_published = models.BooleanField(
        'Опубликовано',
        default=True,
        help_text='Снимите галочку, чтобы скрыть публикацию.'
    )
    class Meta(CreatedAt.Meta):
        abstract = True
