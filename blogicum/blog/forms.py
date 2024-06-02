from django import forms

from .models import Comment, Post


class PostForm(forms.ModelForm):
    """Форма публикации."""

    class Meta:
        model = Post
        exclude = ('author',)
        widgets = {
            'pub_date': forms.DateTimeInput(
                format='%Y-%m-%dT%H:%M',
                attrs={
                    'type': 'datetime-local',
                    'class': 'form-control'
                }
            )
        }


class CommentForm(forms.ModelForm):
    """Форма комментария."""

    class Meta:
        model = Comment
        fields = ('text',)
