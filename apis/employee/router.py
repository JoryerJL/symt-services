from .views import EmployeeViewSet
from rest_framework import routers

router = routers.DefaultRouter()
router.register(r'employee', EmployeeViewSet)
urlpatterns = router.urls