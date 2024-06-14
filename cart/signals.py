from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver
from .views import merge_cart_items


@receiver(user_logged_in)
def handle_user_logged_in(sender, request, user, **kwargs):
    merge_cart_items(request, user)
