# myapp/adapters.py
from allauth.account.adapter import DefaultAccountAdapter
from django.conf import settings

class MyAccountAdapter(DefaultAccountAdapter):
    def get_login_redirect_url(self, request):
        path = super().get_login_redirect_url(request)
        if 'next' in request.GET:
            return request.GET['next']
        return path or settings.LOGIN_REDIRECT_URL

