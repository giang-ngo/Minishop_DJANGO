from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import auth, messages
from .models import Account, UserProfile
from .forms import RegisterForm, UserProfileForm, UserForm, UpdateRecoveryPhoneNumberForm, VerifyRecoveryPhoneForm, RequestPasswordResetForm, VerifyOTPForPasswordResetForm
from cart.views import _cart_id
from cart.models import Cart, CartItem
import requests
from order.models import Order, OrderProduct
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage
from django.contrib.auth.decorators import login_required
from twilio.rest import Client
import random
import os
from django.conf import settings


def loginPage(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        try:
            user = Account.objects.get(email=email)
        except Account.DoesNotExist:
            messages.error(request, 'User does not exist.')
            return redirect('login')

        user = auth.authenticate(email=email, password=password)

        if user is not None:
            try:
                cart = Cart.objects.get(cart_id=_cart_id(request))
                cart_items = CartItem.objects.filter(cart=cart)

                if cart_items:
                    product_variation = [list(item.variations.all())
                                         for item in cart_items]

                    cart_items = CartItem.objects.filter(user=user)
                    ex_var_list = []
                    id_list = []
                    for item in cart_items:
                        existing_variation = item.variations.all()
                        ex_var_list.append(list(existing_variation))
                        id_list.append(item.id)

                    for pr in product_variation:
                        if pr in ex_var_list:
                            index = ex_var_list.index(pr)
                            item_id = id_list[index]
                            item = CartItem.objects.get(id=item_id)
                            item.quantity += 1
                            item.user = user
                            item.save()
                        else:
                            for item in cart_items:
                                item.user = user
                                item.save()
            except Cart.DoesNotExist:
                pass

            auth.login(request, user)
            url = request.META.get('HTTP_REFERER')
            try:
                query = requests.utils.urlparse(url).query
                params = dict(x.split('=') for x in query.split('&'))
                if 'next' in params:
                    return redirect(params['next'])
            except:
                return redirect('home')
        else:
            messages.error(request, 'Invalid login credentials.')
    return render(request, 'user_account/login.html')


def logoutUser(request):
    auth.logout(request)
    return redirect('home')


def registerPage(request):
    if request.user.is_authenticated:
        return redirect('home')

    form = RegisterForm()
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            email = form.cleaned_data['email']
            phone_number = form.cleaned_data['phone_number']
            password = form.cleaned_data['password']
            username = email.split('@')[0]
            user = Account.objects.create_user(
                first_name=first_name, last_name=last_name, email=email, password=password, username=username)
            user.phone_number = phone_number
            user.save()

            current_site = get_current_site(request)
            mail_subject = 'Please activate your account.'
            message = render_to_string('user_account/user_account_verification_email.txt', {
                'user': user,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': default_token_generator.make_token(user),
            })
            to_email = email
            send_email = EmailMessage(mail_subject, message, to=[to_email])
            send_email.send()

            messages.success(
                request, 'Thank you for registering with us. We have sent you a verification email.')
            return redirect('login')
    context = {'form': form}
    return render(request, 'user_account/register.html', context)


def activate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account._default_manager.get(pk=uid)
    except (TypeError, Account.DoesNotExist, OverflowError, ValueError):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(
            request, 'Congratulations! Your account is activated.')
        return redirect('login')
    else:
        messages.error(request, 'Invalid activation link.')
        return redirect('register')


def forgot_password(request):
    if request.method == 'POST':
        email = request.POST['email']
        if Account.objects.filter(email=email).exists():
            user = Account.objects.get(email__exact=email)

            current_site = get_current_site(request)
            mail_subject = 'Reset Your Password.'
            message = render_to_string('user_account/reset_password_email.txt', {
                'user': user,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': default_token_generator.make_token(user),
            })
            to_email = email
            send_email = EmailMessage(mail_subject, message, to=[to_email])
            send_email.send()

            messages.success(request, 'Password reset email has been sent.')
            return redirect('login')
        else:
            messages.error(request, 'Account does not exist.')
    return render(request, 'user_account/forgot_password.html')


def reset_password_validate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account._default_manager.get(pk=uid)
    except (TypeError, Account.DoesNotExist, OverflowError, ValueError):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        request.session['uid'] = uid
        messages.success(request, 'Please reset your password.')
        return redirect('reset_password')
    else:
        return redirect('login')


def reset_password(request):
    if request.method == 'POST':
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        if password == confirm_password:
            uid = request.session.get("uid")
            user = Account.objects.get(pk=uid)
            user.set_password(password)
            user.save()
            messages.success(request, 'Password reset successful.')
            return redirect('login')
        else:
            messages.error(request, 'Passwords do not match!')

    return render(request, 'user_account/reset_password.html')


@login_required(login_url='login')
def dashboard(request):
    userprofile = get_object_or_404(UserProfile, user=request.user)
    orders = Order.objects.order_by(
        '-created_at').filter(user_id=request.user.id, is_ordered=True)
    orders_count = orders.count()
    context = {'orders_count': orders_count, 'userprofile': userprofile}
    return render(request, 'user_account/dashboard.html', context)


@login_required(login_url='login')
def my_orders(request):
    userprofile = get_object_or_404(UserProfile, user=request.user)
    orders = Order.objects.filter(
        user=request.user, is_ordered=True).order_by('-created_at')
    context = {'orders': orders, 'userprofile': userprofile}
    return render(request, 'user_account/my_orders.html', context)


@login_required(login_url='login')
def edit_profile(request):
    userprofile = get_object_or_404(UserProfile, user=request.user)
    user_form = UserForm(instance=request.user)
    profile_form = UserProfileForm(instance=userprofile)
    if request.method == 'POST':
        user_form = UserForm(request.POST, instance=request.user)
        profile_form = UserProfileForm(
            request.POST, request.FILES, instance=userprofile)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(
                request, 'Your profile has been updated successfully.')
            return redirect('dashboard')
    context = {
        'user_form': user_form,
        'profile_form': profile_form,
        'userprofile': userprofile,
    }
    return render(request, 'user_account/edit_profile.html', context)


@login_required(login_url='login')
def change_password(request):
    userprofile = get_object_or_404(UserProfile, user=request.user)
    if request.method == 'POST':
        current_password = request.POST.get('current_password')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')

        user = Account.objects.get(username__exact=request.user.username)

        if new_password == confirm_password:
            if user.check_password(current_password):
                user.set_password(new_password)
                user.save()
                messages.success(
                    request, 'Your password has been changed successfully.')
                return redirect('dashboard')
            else:
                messages.error(request, 'Current password is incorrect.')
        else:
            messages.error(request, 'Passwords do not match!')
    context = {'userprofile': userprofile}
    return render(request, 'user_account/change_password.html', context)


@login_required(login_url='login')
def order_detail(request, order_id):
    order_detail = OrderProduct.objects.filter(order__order_number=order_id)
    order = Order.objects.get(order_number=order_id)
    subtotal = sum(item.product.price * item.quantity for item in order_detail)

    context = {'order_detail': order_detail,
               'order': order, 'subtotal': subtotal}
    return render(request, 'user_account/order_detail.html', context)


@login_required(login_url='login')
def update_recovery_phone_number(request):
    user = request.user
    if request.method == 'POST':
        form = UpdateRecoveryPhoneNumberForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            otp = send_otp(user.recovery_phone_number)
            request.session['otp'] = otp
            request.session['user_id'] = user.id
            messages.success(
                request, 'OTP has been sent to your recovery phone number.')
            return redirect('verify_recovery_phone')
    else:
        form = UpdateRecoveryPhoneNumberForm(instance=user)
    return render(request, 'user_account/update_recovery_phone.html', {'form': form})


@login_required(login_url='login')
def verify_recovery_phone(request):
    if request.method == 'POST':
        form = VerifyRecoveryPhoneForm(request.POST)
        if form.is_valid():
            otp = form.cleaned_data['otp']
            if otp == str(request.session.get('otp')):
                user_id = request.session.get('user_id')
                user = Account.objects.get(id=user_id)
                user.recovery_phone_verified = True
                user.save()
                del request.session['otp']
                del request.session['user_id']
                messages.success(
                    request, 'Recovery phone number verified successfully.')
                return redirect('dashboard')
            else:
                form.add_error('otp', 'Invalid OTP')
    else:
        form = VerifyRecoveryPhoneForm()
    return render(request, 'user_account/verify_recovery_phone.html', {'form': form})


def send_otp(phone_number, sender_name="Minishop"):
    otp = random.randint(100000, 999999)
    account_sid = settings.TWILIO_ACCOUNT_SID
    auth_token = settings.TWILIO_AUTH_TOKEN
    client = Client(account_sid, auth_token)

    # Customize the message body
    message_body = (
        f"Hello from {sender_name},\n\n"
        f"Your OTP for verifying your recovery phone number is: {otp}. "
        f"Please do not share this code with anyone.\n\n"
        f"Thank you,\n"
        f"{sender_name} Team"
    )

    message = client.messages.create(
        body=message_body,
        from_=settings.TWILIO_PHONE_NUMBER,
        to=phone_number
    )
    return otp


def request_password_reset(request):
    if request.method == 'POST':
        form = RequestPasswordResetForm(request.POST)
        if form.is_valid():
            recovery_phone_number = form.cleaned_data['recovery_phone_number']
            user = Account.objects.get(
                recovery_phone_number=recovery_phone_number)
            otp = send_otp(recovery_phone_number)
            request.session['otp'] = otp
            request.session['user_id'] = user.id
            messages.success(
                request, 'OTP has been sent to your recovery phone number.')
            return redirect('verify_otp_for_password_reset')
    else:
        form = RequestPasswordResetForm()
    return render(request, 'user_account/request_password_reset.html', {'form': form})


def verify_otp_for_password_reset(request):
    if request.method == 'POST':
        form = VerifyOTPForPasswordResetForm(request.POST)
        if form.is_valid():
            otp = form.cleaned_data['otp']
            if otp == str(request.session.get('otp')):
                user_id = request.session.get('user_id')
                user = Account.objects.get(id=user_id)
                new_password = form.cleaned_data['new_password']
                user.set_password(new_password)
                user.save()
                del request.session['otp']
                del request.session['user_id']
                messages.success(request, 'Password reset successful.')
                return redirect('login')
            else:
                form.add_error('otp', 'Invalid OTP')
    else:
        form = VerifyOTPForPasswordResetForm()
    return render(request, 'user_account/verify_otp_for_password_reset.html', {'form': form})
