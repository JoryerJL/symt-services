from .views import ClientViewSet
from rest_framework import routers

router = routers.DefaultRouter()
router.register(r'client', ClientViewSet)

urlpatterns = router.urls