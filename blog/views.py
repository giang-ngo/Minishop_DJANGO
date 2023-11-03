from django.shortcuts import render, get_object_or_404, redirect
from .models import Post, PostingCategory, Comment
from django.core.paginator import Paginator
from taggit.models import Tag
from .forms import PostForm, CommentForm
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from account.models import UserProfile

# Create your views here.


def posts_list(request, category_slug=None):
    
    categories = None
    posts = None
    
    # Lọc bài đăng đã xuất bản
    published_posts = Post.objects.filter(status=1)
    # Lọc các tag với bải đăng đã xuất bản
    tags = Tag.objects.filter(post__in=published_posts)

    if category_slug != None:
        categories = get_object_or_404(PostingCategory, slug=category_slug)
        recent_posts = Post.objects.filter(
            category=categories, status=1)[:3]

        page = Paginator(Post.objects.filter(
            category=categories, status=1), 5)
        page_list = request.GET.get('page')
        page = page.get_page(page_list)
        # post_count = posts.count()
    else:
        recent_posts = Post.objects.all().filter(
            status=1)[:3]
        page = Paginator(Post.objects.all().filter(
            status=1), 5)
        page_list = request.GET.get('page')
        page = page.get_page(page_list)
        # post_count = posts.count()
    context = {'recent_posts': recent_posts, 'page': page,
               'tags': tags}
    return render(request, 'blog/posts_list.html', context)


def post_detail(request, category_slug, post_slug):
    userprofile = get_object_or_404(UserProfile, user=request.user)

    posts = Post.objects.all().filter(
        status=1)[:3]

    post_single = Post.objects.get(
        category__slug=category_slug, slug=post_slug)

    comments = Comment.objects.filter(
        post_id=post_single.id)

    context = {'post_single': post_single,
               'posts': posts,
               'userprofile': userprofile,
               'comments': comments,
               }
    return render(request, 'blog/post_single.html', context)


@login_required(login_url='login')
def post_create(request):
    categories = PostingCategory.objects.all()
    form = PostForm()
    if request.method == 'POST':
        category_name = request.POST.get('category')
        category = PostingCategory.objects.get(category_name=category_name)
        # tags = request.POST.getlist('tags')
        tags = request.POST.get('tags').split(',')
        post = Post.objects.create(
            author=request.user,
            title=request.POST.get('title'),
            content=request.POST.get('content'),
            image=request.FILES.get('image'),
            category=category,
        )
        for tag_name in tags:
            tag, _ = Tag.objects.get_or_create(name=tag_name.title())
            post.tags.add(tag)
        post.save()

        return redirect('posts_list')
    context = {'form': form, 'categories': categories}
    return render(request, 'blog/post_form.html', context)


def tagged(request, tag_slug):
    
    posts = Post.objects.all().filter(
        status=1)
    recent_posts = Post.objects.all().filter(
            status=1)[:3]
    tags = Tag.objects.all()
    tag = get_object_or_404(Tag, slug=tag_slug)
    page = Paginator(Post.objects.all().filter(
        tags=tag,status=1), 5)
    page_list = request.GET.get('page')
    page = page.get_page(page_list)
    context = {
        'tags': tags,
        'page': page,
        'posts': posts,
        'recent_posts':recent_posts,
    }
    return render(request, 'blog/posts_list.html', context)


def search(request):
    if 'keyword' in request.GET:
        keyword = request.GET.get('keyword')
        if keyword:
            posts = Post.objects.order_by('-created_on').filter(
                Q(content__icontains=keyword) | Q(title__icontains=keyword))
            recent_posts = Post.objects.all().filter(
                status=1)[:3]
            page = Paginator(posts, 5)
            page_list = request.GET.get('page')
            page = page.get_page(page_list)
            post_count = posts.count()
    context = {'posts': posts,
               'post_count': post_count, 'page': page, 'recent_posts': recent_posts}
    return render(request, 'blog/posts_list.html', context)


@login_required(login_url='login')
def comment(request, post_id):
    url = request.META.get('HTTP_REFERER')
    form = CommentForm()

    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            data = Comment()
            data.body = form.cleaned_data['body']
            data.user = request.user
            data.post_id = post_id
            data.save()
            return redirect(url)
