from django import forms
from .models import Post, Comment


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ('title', 'text', 'group', 'image')
        labels = {
            'text': 'Текст поста',
            'group': 'Группа',
            'image': 'Изображение',
        }
        help_texts = {
            'text': 'Введите текст поста',
            'group': 'Выберите группу',
            'image': 'Выберите изображение',
        }

    def clean_text(self):
        data = self.cleaned_data['text']
        if not data:
            raise forms.ValidationError('Текст поста должен быть заполнен')
        return data


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('text',)
        labels = {
            'text': 'Текст комментария',
        }
        help_texts = {
            'text': 'Введите текст комментария',
        }

    def clean_text(self):
        data = self.cleaned_data['text']
        if not data:
            raise forms.ValidationError(
                'Текст комментария должен быть заполнен'
            )
        return data
