from django.urls import path

from . import views


app_name = 'blog'

urlpatterns = [
    path(
        '',
        views.IndexView.as_view(),
        name='index'
    ),
    path(
        'posts/create/',
        views.CreatePostView.as_view(),
        name='create_post'
    ),
    path(
        'posts/<int:post_id>/', views.PostDetailView.as_view(),
        name='post_detail'
    ),
    path(
        'category/<slug:category_slug>/',
        views.CategoryPostsView.as_view(),
        name='category_posts'
    ),
    path(
        'edit/',
        views.UserUpdateView.as_view(),
        name='edit_profile'
    ),
    path(
        '<int:post_id>/comment/',
        views.add_comment,
        name='add_comment'
    ),
    path(
        'posts/<int:post_id>/edit/',
        views.PostUpdateView.as_view(),
        name='edit_post'
    ),
    path(
        'posts/<int:post_id>/delete/',
        views.delete_post,
        name='delete_post'
    ),
    path(
        'posts/<int:pk>/delete_comment/<int:comment_pk>/',
        views.delete_comment,
        name='delete_comment'
    ),
    path(
        'posts/<int:pk>/edit_comment/<int:comment_pk>/',
        views.edit_comment,
        name='edit_comment'
    ),
    path(
        'profile/<slug:username>/',
        views.profile,
        name='profile'
    )
]
