from .views import ServiceViewSet
from rest_framework import routers

routers = routers.DefaultRouter()
routers.register(r'service', ServiceViewSet)

urlpatterns = routers.urls