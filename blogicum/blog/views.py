from django.shortcuts import get_object_or_404, render, redirect
from django.http import Http404
from django.db.models.functions import Now
from django.utils import timezone
from django.core.paginator import Paginator
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import DetailView, ListView, UpdateView, CreateView

from django.urls import reverse, reverse_lazy
from django.contrib.auth.decorators import login_required
from django.db.models import Count

from .models import Category, Post, User, Comment
from .forms import PostForm, CommentForm
from .common import filter_objects_published


class IndexView(ListView):
    """класс главной страницы."""

    model = Post
    template_name = 'blog/index.html'
    paginate_by = 10

    def get_queryset(self):
        return Post.objects.select_related(
            'author', 'category', 'location'
        ).filter(
            is_published=True,
            pub_date__lte=Now(),
            category__is_published=True,
        ).order_by('-pub_date').annotate(
            comment_count=Count('comments'))


class CreatePostView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        username = self.request.user.username
        return reverse_lazy('blog:profile', kwargs={'username': username})


class PostDetailView(DetailView):
    """Класс для представления отдельной записи поста."""

    model = Post
    template_name = 'blog/detail.html'
    pk_url_kwarg = 'post_id'

    def get_object(self):
        post_id = self.kwargs.get(self.pk_url_kwarg)
        post = get_object_or_404(Post, pk=post_id)
        if post.author != self.request.user and any([
            post.pub_date > timezone.now(),
            not post.is_published,
            not post.category.is_published,
        ]):
            raise Http404
        return post

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = CommentForm()
        context['comments'] = self.object.comments.select_related('author')
        return context


class CategoryPostsView(ListView):
    """Класс вызова шаблона (категории)."""

    category = None
    model = Post
    template_name = 'blog/category.html'
    paginate_by = 10

    def get_queryset(self):
        self.category = get_object_or_404(
            Category,
            is_published=True,
            slug=self.kwargs['category_slug']
        )
        return filter_objects_published(self.category.posts)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = self.category
        return context


def profile(request, username):
    """функция отображения профиля."""
    template = 'blog/profile.html'
    user = get_object_or_404(User, username=username)
    posts = Post.objects.filter(
        author=user).annotate(
            comment_count=Count('comments')).order_by('-pub_date')
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'profile': user,
        'page_obj': page_obj,
    }
    return render(request, template, context)


class UserUpdateView(LoginRequiredMixin, UpdateView):
    model = User
    template_name = 'blog/user.html'
    fields = ['username', 'last_name', 'email']

    def get_object(self):
        return self.request.user

    def get_success_url(self):
        return reverse(
            'blog:profile',
            kwargs={
                'username': self.request.user
            },
        )


@login_required
def add_comment(request, post_id):
    """Класс для добавления комментария."""
    post = get_object_or_404(Post, pk=post_id)
    form = CommentForm(request.POST)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    comment = post.comments.order_by('created_at')
    return redirect('blog:post_detail', post_id=post_id)


class PostUpdateView(LoginRequiredMixin, UpdateView):
    """Класс редактирования поста."""

    model = Post
    template_name = 'blog/create.html'
    form_class = PostForm
    pk_url_kwarg = 'post_id'

    def dispatch(self, request, *args, **kwargs):
        instance = get_object_or_404(Post, pk=kwargs['post_id'])
        if instance.author != request.user:
            return redirect('blog:post_detail', post_id=kwargs['post_id'])
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse_lazy('blog:post_detail',
                            kwargs={'post_id': self.object.pk})


@login_required
def delete_post(request, post_id):
    """Представление для удаления поста пользователя."""
    instance = get_object_or_404(Post, pk=post_id, author=request.user)
    form = PostForm(instance=instance)
    if request.method == 'POST':
        instance.delete()
        return redirect('blog:profile', username=request.user)
    return render(request, 'blog/create.html', {'form': form})


@login_required
def delete_comment(request, pk, comment_pk):
    """Представление для удаления комментария пользователя."""
    comment = get_object_or_404(Comment,
                                pk=comment_pk,
                                author=request.user)
    context = {'comment': comment}
    if request.method == 'POST':
        comment.delete()
        return redirect('blog:post_detail', post_id=pk)
    return render(request, 'blog/comment.html', context)


@login_required
def edit_comment(request, pk, comment_pk):
    """Представление для редактирования комментария пользователя."""
    comment = get_object_or_404(Comment,
                                pk=comment_pk,
                                author=request.user)
    form = CommentForm(request.POST or None, instance=comment)
    context = {'form': form, 'comment': comment}
    if form.is_valid():
        form.save()
        return redirect('blog:post_detail', post_id=pk)
    return render(request, 'blog/comment.html', context)
