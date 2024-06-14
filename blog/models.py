from django.db import models
from user_account.models import Account
from django.urls import reverse
from taggit.managers import TaggableManager
from ckeditor.fields import RichTextField
from django.utils.text import slugify
from django.db.models import Count


class PostingCategory(models.Model):
    category_name = models.CharField(max_length=200, unique=True)
    slug = models.SlugField(max_length=200, unique=True)

    class Meta:
        verbose_name = 'posting category'
        verbose_name_plural = 'posting categories'

    def get_url(self):
        return reverse('posts_by_category', args=[self.slug])

    def __str__(self) -> str:
        return self.category_name


STATUS = (
    (0, "Draft"),
    (1, "Publish")
)


class Post(models.Model):
    title = models.CharField(max_length=200, unique=True)
    # content = models.TextField()
    content = RichTextField()
    image = models.ImageField(upload_to='photos/blog')
    slug = models.SlugField(max_length=200, unique=True)
    author = models.ForeignKey(
        Account, on_delete=models.CASCADE, related_name='blog_posts')
    updated_on = models.DateTimeField(auto_now=True)
    created_on = models.DateTimeField(auto_now_add=True)
    status = models.IntegerField(choices=STATUS, default=0)
    category = models.ForeignKey(
        PostingCategory, on_delete=models.CASCADE, related_name='categories')
    tags = TaggableManager(blank=True)

    class Meta:
        ordering = ['-created_on']

    # Tự động tạo slug - title theo model
    def save(self, *args, **kwargs):
        self.slug = slugify(self.title)
        super(Post, self).save(*args, **kwargs)

    def count_comment(self):
        comments = Comment.objects.filter(
            post=self).aggregate(count=Count('body'))
        count = 0
        if comments['count'] is not None:
            count = int(comments['count'])
        return count

    def get_url(self):
        return reverse('post_detail', args=[self.category.slug, self.slug])

    def __str__(self):
        return self.title


class Comment(models.Model):
    post = models.ForeignKey(
        Post, on_delete=models.CASCADE, null=True)
    parent = models.ForeignKey(
        'self', related_name='parent_comment', on_delete=models.CASCADE,
        null=True)
    user = models.ForeignKey(Account, on_delete=models.CASCADE)
    body = models.TextField()
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created']

    def __str__(self) -> str:
        return self.body
