"""jwt_knox urls.py

"""

from rest_framework import routers
from rest_framework.urlpatterns import include, url

from .viewsets import JWTKnoxAPIViewSet

app_name = 'jwt_knox'

router = routers.SimpleRouter(trailing_slash=False)
router.register(r'', JWTKnoxAPIViewSet, base_name='jwt_knox')

urlpatterns = [url('^', include(router.urls)), ]
