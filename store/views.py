from django.shortcuts import render, get_object_or_404
from store.models import Product
from django.db.models import Q
from django.core.paginator import Paginator
from category.models import Category


def store(request, category_slug=None):
    categories = None
    products = None
    if category_slug != None:
        categories = get_object_or_404(Category, slug=category_slug)
        products = Product.objects.filter(
            category=categories, is_available=True)
        page = Paginator(products, 6)
        page_list = request.GET.get('page')
        page = page.get_page(page_list)
        product_count = products.count()

    else:
        products = Product.objects.all().filter(is_available=True)
        page = Paginator(products, 6)
        page_list = request.GET.get('page')
        page = page.get_page(page_list)
        product_count = products.count()
    context = {'products': products, 'page': page,
               'product_count': product_count}
    return render(request, 'store/store.html', context)


def product_detail(request, category_slug, product_slug):
    single_product = Product.objects.get(
        slug=product_slug, category__slug=category_slug)

    context = {'single_product': single_product}
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
