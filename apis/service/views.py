from rest_framework.response import Response

from .serializers import ServiceSerializer, ServiceUpdateSerializer
from service.models import Service
from service.selectors import get_service_by_pk
from service.services import service_update_from_api
from rest_framework import viewsets


class ServiceViewSet(viewsets.ModelViewSet):
    queryset = Service.objects.none()
    serializer_class = ServiceSerializer

    def retrieve(self, request, *args, **kwargs):
        try:
            service = get_service_by_pk(service_id=kwargs['pk'])
        except Service.DoesNotExist:
            return Response({"detail": "Not Found"}, status=404)

        return Response(ServiceSerializer(service, context={'request': request}).data)

    def update(self, request, *args, **kwargs):
        try:
            service = get_service_by_pk(service_id=kwargs['pk'])
        except Service.DoesNotExist:
            return Response({"detail": "Not Found"}, status=404)

        serializer = ServiceUpdateSerializer(service, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(ServiceSerializer(service, context={'request': request}).data)

    def partial_update(self, request, *args, **kwargs):
        try:
            service = get_service_by_pk(service_id=kwargs['pk'])
        except Service.DoesNotExist:
            return Response({"detail": "Not Found"}, status=404)

        data = request.data.copy()
        summary = data.pop('summary', None)
        serializer = ServiceUpdateSerializer(service, data=data, partial=True)
        serializer.is_valid(raise_exception=True)
        service = service_update_from_api(
            service=service,
            status=serializer.validated_data.get('status'),
            end_date=serializer.validated_data.get('end_date'),
            summary=summary,
        )

        return Response(ServiceSerializer(service, context={'request': request}).data)
