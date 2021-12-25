"""jwt_knox urls.py

"""

from rest_framework import routers

from .viewsets import JWTKnoxAPIViewSet

router = routers.SimpleRouter(trailing_slash=False)
router.register(r'', JWTKnoxAPIViewSet, basename='jwt_knox')

urlpatterns = router.urls
