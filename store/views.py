from django.shortcuts import render, get_object_or_404, redirect
from store.models import Product, ProductGallery
from django.db.models import Q
from django.core.paginator import Paginator
from category.models import Category
from django.contrib.auth.decorators import login_required
from order.models import OrderProduct
from .forms import ReviewForm
from .models import ReviewRating
from account.models import UserProfile


def store(request, category_slug=None):
    categories = None
    products = None
    if category_slug != None:
        categories = get_object_or_404(Category, slug=category_slug)
        products = Product.objects.filter(
            category=categories, is_available=True).order_by('-created_date')
        page = Paginator(products, 6)
        page_list = request.GET.get('page')
        page = page.get_page(page_list)
        product_count = products.count()

    else:
        products = Product.objects.all().filter(
            is_available=True).order_by('-created_date')
        page = Paginator(products, 6)
        page_list = request.GET.get('page')
        page = page.get_page(page_list)
        product_count = products.count()
    context = {'products': products, 'page': page,
               'product_count': product_count}
    return render(request, 'store/store.html', context)


def product_detail(request, category_slug, product_slug):
    userprofile = get_object_or_404(UserProfile, user=request.user)
    try:
        single_product = Product.objects.get(
            category__slug=category_slug, slug=product_slug)
    except Exception as e:
        raise e

    if request.user.is_authenticated:
        try:
            order_product = OrderProduct.objects.filter(
                user=request.user, product__id=single_product.id)
        except OrderProduct.DoesNotExist:
            order_product = None
    else:
        order_product = None

    reviews = ReviewRating.objects.filter(
        product_id=single_product.id, status=True).order_by('-created_at')

    product_gallery = ProductGallery.objects.filter(
        product_id=single_product.id)

    context = {'single_product': single_product,
               'order_product': order_product,
               'reviews': reviews,
               'product_gallery': product_gallery,
               'userprofile': userprofile}
    return render(request, 'store/product_detail.html', context)


def search(request):
    if 'keyword' in request.GET:
        keyword = request.GET.get('keyword')
        if keyword:
            products = Product.objects.order_by('-created_date').filter(
                Q(description__icontains=keyword) | Q(product_name__icontains=keyword))
            product_count = products.count()
    context = {'products': products, 'product_count': product_count}
    return render(request, 'store/store.html', context)


@login_required(login_url='login')
def review(request, product_id):
    '''Hàm tạo được nhiều đánh giá'''
    url = request.META.get('HTTP_REFERER')
    form = ReviewForm()

    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            data = ReviewRating()
            data.product_id = product_id
            data.user = request.user
            data.subject = form.cleaned_data['subject']
            data.review = form.cleaned_data['review']
            data.rating = form.cleaned_data['rating']
            data.ip = request.META.get('REMOTE_ADDR')
            data.rating = form.cleaned_data['rating']
            data.save()
            return redirect(url)  # chuyển hướng đến trang hiện tại


# @login_required(login_url='login')
# def review(request, product_id):
#     '''Hàm tạo được 1 đánh giá, những lần sau chỉ update'''
#     url = request.META.get("HTTP_REFERER")
#     if request.method == 'POST':
#         try:
#             reviews = ReviewRating.objects.get(
#                 user__id=request.user.id, product__id=product_id)
#             form = ReviewForm(request.POST, instance=reviews)
#             form.save()
#         except ReviewRating.DoesNotExist:
#             form = ReviewForm(request.POST)
#             if form.is_valid():
#                 data = ReviewRating()
#                 data.product_id = product_id
#                 data.user = request.user
#                 data.subject = form.cleaned_data['subject']
#                 data.review = form.cleaned_data['review']
#                 data.rating = form.cleaned_data['rating']
#                 data.ip = request.META.get('REMOTE_ADDR')
#                 data.rating = form.cleaned_data['rating']
#                 data.save()
#                 return redirect(url)
