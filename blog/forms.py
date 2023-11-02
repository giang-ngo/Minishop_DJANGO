from django import forms
from .models import Post, Comment, PostingCategory


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['title', 'content', 'image', 'category', 'tags']

    def __init__(self, *args, **kwargs):
        category = kwargs.pop('category', '')
        super(PostForm, self).__init__(*args, **kwargs)

        self.fields['posting_category'] = forms.ModelChoiceField(
            queryset=PostingCategory.objects.filter(category_name=category))
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['body']
