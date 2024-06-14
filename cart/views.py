from django.shortcuts import render, redirect
from store.models import Product, Variation
from cart.models import Cart, CartItem
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required
from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver


def _cart_id(request):
    cart = request.session.session_key
    if not cart:
        cart = request.session.create()
    return cart


def add_cart(request, product_id):
    product = Product.objects.get(id=product_id)
    product_variation = []

    if request.method == 'POST':
        for item in request.POST:
            key = item
            value = request.POST.get(item)
            try:
                variation = Variation.objects.get(
                    product=product, variation_value__iexact=value, variation_category__iexact=key)
                product_variation.append(variation)
            except:
                pass

    if request.user.is_authenticated:
        user = request.user
        cart_item_qs = CartItem.objects.filter(product=product, user=user)
        if cart_item_qs.exists():
            for cart_item in cart_item_qs:
                ex_var_list = list(cart_item.variations.all())
                if product_variation == ex_var_list:
                    cart_item.quantity += 1
                    cart_item.save()
                    break
            else:
                cart_item = CartItem.objects.create(
                    product=product, quantity=1, user=user)
                if product_variation:
                    cart_item.variations.add(*product_variation)
                cart_item.save()
        else:
            cart_item = CartItem.objects.create(
                product=product, quantity=1, user=user)
            if product_variation:
                cart_item.variations.add(*product_variation)
            cart_item.save()
    else:
        cart, created = Cart.objects.get_or_create(cart_id=_cart_id(request))
        cart.save()
        cart_item_qs = CartItem.objects.filter(product=product, cart=cart)
        if cart_item_qs.exists():
            for cart_item in cart_item_qs:
                ex_var_list = list(cart_item.variations.all())
                if product_variation == ex_var_list:
                    cart_item.quantity += 1
                    cart_item.save()
                    break
            else:
                cart_item = CartItem.objects.create(
                    product=product, quantity=1, cart=cart)
                if product_variation:
                    cart_item.variations.add(*product_variation)
                cart_item.save()
        else:
            cart_item = CartItem.objects.create(
                product=product, quantity=1, cart=cart)
            if product_variation:
                cart_item.variations.add(*product_variation)
            cart_item.save()

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


def merge_cart_items(request, user):
    try:
        session_cart = Cart.objects.get(cart_id=_cart_id(request))
        session_cart_items = CartItem.objects.filter(
            cart=session_cart, is_active=True)
        user_cart_items = CartItem.objects.filter(user=user, is_active=True)

        for session_item in session_cart_items:
            product = session_item.product
            product_variations = list(session_item.variations.all())
            existing_items = user_cart_items.filter(product=product)

            found = False
            for existing_item in existing_items:
                if list(existing_item.variations.all()) == product_variations:
                    existing_item.quantity += session_item.quantity
                    existing_item.save()
                    session_item.delete()
                    found = True
                    break

            if not found:
                session_item.user = user
                session_item.cart = None
                session_item.save()

        session_cart.delete()
    except Cart.DoesNotExist:
        pass


@receiver(user_logged_in)
def handle_user_logged_in(sender, request, user, **kwargs):
    merge_cart_items(request, user)


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
            total += cart_item.quantity * cart_item.product.price
            quantity += cart_item.quantity

        tax = (2 * total) / 100
        grand_total = tax + total
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
        cart_items = CartItem.objects.filter(user=request.user, is_active=True)
        for cart_item in cart_items:
            total += cart_item.product.price * cart_item.quantity
            quantity += cart_item.quantity
        tax = (2 * total) / 100
        grand_total = total + tax
    except ObjectDoesNotExist:
        pass

    context = {
        'total': total,
        'quantity': quantity,
        'cart_items': cart_items,
        'tax': tax,
        'grand_total': grand_total,
    }
    return render(request, 'store/checkout.html', context)
