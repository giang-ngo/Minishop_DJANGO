from django.shortcuts import render, get_object_or_404
from blog.models import Post, PostingCategory
from django.core.paginator import Paginator
from taggit.models import Tag
# Create your views here.


def posts_list(request, category_slug=None):
    categories = None
    posts = None
    tags = Tag.objects.all()
    if category_slug != None:
        categories = get_object_or_404(PostingCategory, slug=category_slug)
        posts = Post.objects.filter(
            category=categories, status=1)[:3]

        page = Paginator(Post.objects.filter(
            category=categories, status=1), 5)
        page_list = request.GET.get('page')
        page = page.get_page(page_list)
        post_count = posts.count()
    else:
        posts = Post.objects.all().filter(
            status=1)[:3]
        page = Paginator(Post.objects.all().filter(
            status=1), 5)
        page_list = request.GET.get('page')
        page = page.get_page(page_list)
        post_count = posts.count()
    context = {'posts': posts, 'page': page,
               'post_count': post_count,
               'tags': tags}
    return render(request, 'blog/posts_list.html', context)


def post_detail(request, category_slug, post_slug):
    posts = Post.objects.all().filter(
        status=1)[:3]
    post_single = Post.objects.get(
        category__slug=category_slug, slug=post_slug)
    context = {'post_single': post_single,
               'posts': posts,
               }
    return render(request, 'blog/post_single.html', context)


def tagged(request, tag_slug):
    posts = Post.objects.all().filter(
        status=1)[:3]
    tags = Tag.objects.all()
    tag = get_object_or_404(Tag, slug=tag_slug)
    page = Paginator(Post.objects.all().filter(
        tags=tag), 5)
    page_list = request.GET.get('page')
    page = page.get_page(page_list)
    context = {
        'tags': tags,
        'page': page,
        'posts': posts,
    }
    return render(request, 'blog/posts_list.html', context)
