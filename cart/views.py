from django.shortcuts import render, redirect
from store.models import Product, Variation
from cart.models import Cart, CartItem
from django.http import HttpResponse
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required

# Create your views here.


def _cart_id(request):
    cart = request.session.session_key
    if not cart:
        cart = request.session.create()
    return cart


def add_cart(request, product_id):
    product = Product.objects.get(id=product_id)
    if request.user.is_authenticated:
        product_variation = []
        if request.method == 'POST':
            for item in request.POST:
                key = item
                value = request.POST.get(item)

                try:
                    variation = Variation.object.get(
                        product=product, variation_value__iexact=value, variation_category__iexact=key)
                    # Thêm 1 biến thể vào list product_variation
                    product_variation.append(variation)

                except:
                    pass

        cart_item = CartItem.objects.filter(product=product, user=request.user)
        if cart_item:

            ex_var_list = []  # khởi tạo các list rỗng
            id = []
            for item in cart_item:  # cho vòng lặp for để lấy từng sản phẩm
                existing_variation = item.variations.all()  # lấy biến thể của từng sản phẩm
                # thêm danh sách các biến thể đang tồn tại trong sp vào list ex_var_list
                ex_var_list.append(list(existing_variation))
                id.append(item.id)  # thêm id của từng sp vào list id

            if product_variation in ex_var_list:  # nếu biến thể của 1 sp có trong danh sách các biến thể thì
                # index của 1 biến thể trong danh sách các biến thể
                index = ex_var_list.index(product_variation)
                item_id = id[index]  # id của sp tại vị trí index
                item = CartItem.objects.get(product=product, id=item_id)
                item.quantity += 1
                item.save()
            else:
                item = CartItem.objects.create(
                    product=product, quantity=1, user=request.user)
                if len(product_variation) > 0:
                    item.variations.clear()
                    item.variations.add(*product_variation)
                item.save()

        else:
            item = CartItem.objects.create(
                product=product, user=request.user, quantity=1)
            if len(product_variation) > 0:
                item.variations.clear()
                item.variations.add(*product_variation)
            item.save()
        return redirect('cart')
    else:
        product_variation = []
        if request.method == 'POST':
            for item in request.POST:
                key = item
                value = request.POST.get(item)

                try:
                    variation = Variation.object.get(
                        product=product, variation_value__iexact=value, variation_category__iexact=key)
                    product_variation.append(variation)
                except:
                    pass

        try:
            cart = Cart.objects.get(cart_id=_cart_id(request))
        except Cart.DoesNotExist:
            cart = Cart.objects.create(cart_id=_cart_id(request))

        cart.save()

        cart_item = CartItem.objects.filter(product=product, cart=cart)
        if cart_item:

            ex_var_list = []
            id = []
            for item in cart_item:
                existing_variation = item.variations.all()
                ex_var_list.append(list(existing_variation))
                id.append(item.id)

            if product_variation in ex_var_list:
                index = ex_var_list.index(product_variation)
                item_id = id[index]
                item = CartItem.objects.get(product=product, id=item_id)
                item.quantity += 1
                item.save()
            else:
                item = CartItem.objects.create(
                    product=product, quantity=1, cart=cart)
                if len(product_variation) > 0:
                    item.variations.clear()
                    item.variations.add(*product_variation)
                item.save()

        else:
            item = CartItem.objects.create(
                product=product, cart=cart, quantity=1)
            if len(product_variation) > 0:
                item.variations.clear()
                item.variations.add(*product_variation)
            item.save()
        return redirect('cart')


def remove_cart(request, product_id, cart_item_id):
    product = Product.objects.get(id=product_id)
    if request.user.is_authenticated:
        cart_item = CartItem.objects.get(
            product=product, user=request.user, id=cart_item_id)
    else:
        cart_item = CartItem.objects.get(
            product=product, cart__cart_id=_cart_id(request), id=cart_item_id)
    cart_item.delete()
    return redirect('cart')


def remove_cart_item(request, product_id, cart_item_id):
    product = Product.objects.get(id=product_id)
    if request.user.is_authenticated:
        cart_item = CartItem.objects.get(
        product=product, user=request.user, id=cart_item_id)
    else:
        cart_item = CartItem.objects.get(
            product=product, cart__cart_id=_cart_id(request), id=cart_item_id)
    if cart_item.quantity > 1:
        cart_item.quantity -= 1
        cart_item.save()
    else:
        cart_item.delete()
    return redirect('cart')


def cart(request, total=0, quantity=0, cart_items=None):
    try:
        tax = 0
        grand_total = 0
        if request.user.is_authenticated:
            cart_items = CartItem.objects.filter(
                user=request.user, is_active=True)
        else:
            cart = Cart.objects.get(cart_id=_cart_id(request))
            cart_items = CartItem.objects.filter(cart=cart, is_active=True)
        for cart_item in cart_items:
            total += cart_item.quantity*cart_item.product.price
            quantity += cart_item.quantity

        tax = (2*total)/100
        grand_total = tax+total
    except ObjectDoesNotExist:
        pass
    context = {'cart_items': cart_items, 'total': total,
               'quantity': quantity, 'tax': tax, 'grand_total': grand_total}
    return render(request, 'store/cart.html', context)

@login_required(login_url='login')
def checkout(request, total=0, quantity=0, cart_items=None):
    try:
        tax = 0
        grand_total = 0
        if request.user.is_authenticated:
            cart_items = CartItem.objects.filter(
                user=request.user, is_active=True)
        else:
            cart_items = CartItem.objects.filter(
                cart__cart_id=_cart_id(request), is_active=True)
        for cart_item in cart_items:
            total += (cart_item.product.price * cart_item.quantity)
            quantity += cart_item.quantity
        tax = (2 * total)/100
        grand_total = total + tax
    except:
        pass

    context = {
        'total': total,
        'quantity': quantity,
        'cart_items': cart_items,
        'tax': tax,
        'grand_total': grand_total,
    }
    return render(request, 'store/checkout.html', context)