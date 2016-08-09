"""jwt_knox urls.py

"""

from django.conf.urls import url, include
from django.contrib import admin

from .views import DebugVerifyTokenView, LoginView, LogoutView, LogoutOtherView, LogoutAllView, VerifyView


app_name = 'jwt_knox'

urlpatterns = [
    url(r'^get_token$', LoginView.as_view(), name='get_new_token'),
    url(r'^verify$', VerifyView.as_view(), name='verify_token'),
    url(r'^debug$', DebugVerifyTokenView.as_view(), name='debug_token_auth_info'),
    url(r'^logout_other$', LogoutOtherView.as_view(), name='logout_other_tokens'),
    url(r'^logout_all$', LogoutAllView.as_view(), name='logout_all_user_tokens'),
    url(r'^logout$', LogoutView.as_view(), name='logout_current_token'),
]
