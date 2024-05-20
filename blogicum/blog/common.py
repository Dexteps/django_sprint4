from django.utils.timezone import now


def filter_objects_published(objs):
    """Общая функция выборки по публикации."""
    return objs.select_related(
        'author',
        'category',
        'location'
    ).filter(
        is_published=True,
        category__is_published=True,
        pub_date__date__lte=now(),
    )
