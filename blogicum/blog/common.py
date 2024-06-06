from django.db.models import Count
from django.utils.timezone import now


def get_objects_related(objs):
    """Общая функция выборки по публикации."""
    return (
        objs.select_related(
            'author',
            'category',
            'location'
        )
    )


def filter_objects_published(objs):
    return objs.filter(
        is_published=True,
        category__is_published=True,
        pub_date__date__lte=now()
    )


def add_annotations_comments(objs):
    return objs.annotate(
        comment_count=Count('comments')
    )
