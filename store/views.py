from django.shortcuts import render
from store.models import Product
from django.db.models import Q
from django.core.paginator import Paginator



def store(request):
    products = Product.objects.all().filter(is_available=True)
    page = Paginator(products, 1)
    page_list = request.GET.get('page')
    page = page.get_page(page_list)
    context = {'products': products, 'page': page}
    return render(request, 'store/store.html', context)

def search(request):
    if 'keyword' in request.GET:
        keyword = request.GET.get('keyword')
        if keyword:
            products = Product.objects.order_by('-created_date').filter(
                Q(description__icontains=keyword) | Q(product_name__icontains=keyword))
            product_count = products.count()
    context = {'products': products, 'product_count': product_count}
    return render(request, 'store/store.html', context)