from django.shortcuts import get_object_or_404, render, redirect
from django.utils import timezone
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    UpdateView
)
from django.urls import reverse, reverse_lazy
from django.contrib.auth.decorators import login_required
from django.db.models import Q

from .mixins import PostMixin
from .models import Category, Post, User, Comment
from .forms import PostForm, CommentForm
from .common import (
    add_annotations_comments,
    filter_objects_published,
    get_objects_related
)
from .constants import POSTS_PAGE_LIMIT


class IndexView(ListView):
    """класс главной страницы."""

    model = Post
    template_name = 'blog/index.html'
    paginate_by = POSTS_PAGE_LIMIT
    queryset = add_annotations_comments(
        filter_objects_published(
            get_objects_related(
                Post.objects
            )
        ).order_by(
            '-pub_date'
        )
    )


class CreatePostView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('blog:profile',
                            kwargs={'username': self.request.user.username})


class PostDetailView(DetailView):
    """Класс для представления отдельной записи поста."""

    model = Post
    template_name = 'blog/detail.html'
    pk_url_kwarg = 'post_id'

    def get_object(self):
        filters = (
            Q(pub_date__date__lte=timezone.now())
            & Q(is_published=True)
            & Q(category__is_published=True)
        )
        if not self.request.user.is_anonymous:
            filters |= Q(author=self.request.user)
        qs = get_objects_related(
            Post.objects.filter(filters)
        )
        self.post = get_object_or_404(
            qs,
            pk=self.kwargs[self.pk_url_kwarg]
        )
        return self.post

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = CommentForm()
        context['comments'] = self.object.comments.select_related('author')
        return context


class CategoryPostsView(ListView):
    """Класс вызова шаблона (категории)."""

    model = Post
    template_name = 'blog/category.html'
    paginate_by = POSTS_PAGE_LIMIT

    def get_queryset(self):
        self.category = get_object_or_404(
            Category,
            is_published=True,
            slug=self.kwargs['category_slug']
        )
        return add_annotations_comments(
            filter_objects_published(
                get_objects_related(
                    self.category.posts
                )
            )
        ).order_by('-pub_date')


def get_context_data(self, **kwargs):
    context = super().get_context_data(**kwargs)
    context['category'] = self.category
    return context


class UserPostsListView(ListView):
    """Представление пользователя."""

    model = Post
    template_name = 'blog/profile.html'
    paginate_by = POSTS_PAGE_LIMIT

    def get_queryset(self):
        self.user = get_object_or_404(
            User,
            username=self.kwargs['username']
        )
        qs = add_annotations_comments(
            get_objects_related(
                self.user.posts
            )
        ).order_by('-pub_date')
        if self.user != self.request.user:
            return filter_objects_published(qs)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['profile'] = self.user
        return context


class UserUpdateView(LoginRequiredMixin, UpdateView):
    model = User
    template_name = 'blog/user.html'
    fields = ('username', 'last_name', 'email')

    def get_object(self):
        return self.request.user

    def get_success_url(self):
        return reverse(
            'blog:profile',
            kwargs={
                'username': self.request.user
            },
        )


class AddCommentCreateView(
    LoginRequiredMixin,
    CreateView
):
    """Класс представление Создание комментария."""

    model = Comment
    form_class = CommentForm

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.post = get_object_or_404(
            Post,
            pk=self.kwargs['post_id']
        )
        return super().form_valid(form)

    def get_success_url(self):
        return reverse(
            'blog:post_detail',
            kwargs={'post_id': self.kwargs['post_id']})


class PostUpdateView(PostMixin, UpdateView):
    """Класс редактирования поста."""

    model = Post
    template_name = 'blog/create.html'
    form_class = PostForm
    pk_url_kwarg = 'post_id'

    def dispatch(self, request, *args, **kwargs):
        instance = get_object_or_404(Post, id=kwargs['post_id'])
        if instance.author != request.user:
            return redirect('blog:post_detail', post_id=kwargs['post_id'])
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse_lazy('blog:post_detail',
                            kwargs={'post_id': self.object.id})


class PostDeleteView(PostMixin, DeleteView):
    """Представление Удаление поста."""

    def get_success_url(self):
        return reverse_lazy('blog:index')


@login_required
def delete_comment(request, id, comment_id):
    """Представление для удаления комментария пользователя."""
    comment = get_object_or_404(Comment,
                                id=comment_id,
                                author=request.user)
    if comment.author != request.user:
        return redirect('blog:post_detail', request.kwargs['post_id'])
    if request.method == 'POST':
        comment.delete()
        return redirect('blog:post_detail', post_id=id)
    return render(request, 'blog/comment.html', {'comment': comment})


@login_required
def edit_comment(request, id, comment_id):
    """Представление для редактирования комментария пользователя."""
    comment = get_object_or_404(Comment,
                                id=comment_id,
                                author=request.user)
    form = CommentForm(request.POST or None, instance=comment)
    if comment.author != request.user:
        return redirect('blog:post_detail', request.kwargs['post_id'])
    if form.is_valid():
        form.save()
        return redirect('blog:post_detail', post_id=id)
    return render(
        request,
        'blog/comment.html',
        {'form': form, 'comment': comment})
