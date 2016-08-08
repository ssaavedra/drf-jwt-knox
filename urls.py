"""jwt_knox urls.py

"""

from django.conf.urls import url, include
from django.contrib import admin

from .views import DebugVerifyTokenView, LoginView, LogoutView, LogoutOtherView, LogoutAllView, VerifyView

urlpatterns = [
    url(r'^get_token$', LoginView.as_view()),
    url(r'^verify$', VerifyView.as_view()),
    url(r'^debug$', DebugVerifyTokenView.as_view()),
    url(r'^logout_other$', LogoutOtherView.as_view()),
    url(r'^logout_all$', LogoutAllView.as_view()),
    url(r'^logout$', LogoutView.as_view()),
]
