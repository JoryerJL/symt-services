from rest_framework.response import Response

from .serializers import ServiceSerializer, ServiceUpdateSerializer
from service.models import Service
from rest_framework import viewsets

class ServiceViewSet(viewsets.ModelViewSet):
    queryset = Service.objects.all()
    serializer_class = ServiceSerializer


    def update(self, request, *args, **kwargs):
        self.serializer_class = ServiceUpdateSerializer
        return super().update(request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        self.serializer_class = ServiceUpdateSerializer
        summary = request.data.get('summary')
        service = self.get_object()
        if summary:
            if service.summary:
                service.summary += f"\n{summary}"
            else:
                service.summary = summary
            service.save(update_fields=["summary"])

        data = request.data.copy()
        if 'summary' in data:
            data.pop('summary')

        serializer = self.get_serializer(service, data=data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(ServiceSerializer(service, context={'request': request}).data)
