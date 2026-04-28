from django.urls import path, include

urlpatterns = [
    path('api/', include('apis.employee.router'), name='employee'),
    path('api/', include('apis.client.router'), name='client'),
    path('api/', include('apis.service.router'), name='service'),
]
