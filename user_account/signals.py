from django.dispatch import receiver
from allauth.account.signals import user_signed_up, user_logged_in

@receiver(user_signed_up)
def activate_user_on_signup(request, user, **kwargs):
    user.is_active = True
    user.save()

@receiver(user_logged_in)
def activate_user_on_login(request, user, **kwargs):
    user.is_active = True
    user.save()
