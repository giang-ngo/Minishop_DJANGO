from django.db import models
from account.models import UserProfile
from django.urls import reverse
from taggit.managers import TaggableManager
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
    content = models.TextField()
    image = models.ImageField(upload_to='photos/blog')
    slug = models.SlugField(max_length=200, unique=True)
    author = models.ForeignKey(
        UserProfile, on_delete=models.CASCADE, related_name='blog_posts')
    updated_on = models.DateTimeField(auto_now=True)
    created_on = models.DateTimeField(auto_now_add=True)
    status = models.IntegerField(choices=STATUS, default=0)
    category = models.ForeignKey(
        PostingCategory, on_delete=models.CASCADE, related_name='categories')
    tags = TaggableManager(blank=True)

    class Meta:
        ordering = ['-created_on']

    def get_context(self):
        test = PostingCategory.objects.annotate(post_count = Count("categories")).count()
        return test

    def get_url(self):
        return reverse('post_detail', args=[self.category.slug, self.slug])

    def __str__(self):
        return self.title
