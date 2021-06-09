from django.forms import ModelForm, BooleanField  # Импортируем true-false поле
from .models import *


# Создаём модельную форму
class PostForm(ModelForm):
    check_box = BooleanField(label='Алло, Галочка!!!')  # добавляем галочку, или же true-false поле

    class Meta:
        model = Post
        fields = [
            'postAuthor',
            'position',
            'postCategory',
            'preview_name',
            'text',
            'check_box',
        ]


class CommentForm(ModelForm):
    class Meta:
        model = Comment
        fields = [
            'commentText',
        ]

