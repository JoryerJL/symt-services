from .serializers import AddressSerializer, ClientSerializer
from client.models import Client, Address
from client.selectors import get_client_by_pk
from rest_framework.response import Response
from rest_framework import status
from rest_framework import viewsets


class AddressViewSet(viewsets.ModelViewSet):
    queryset = Address.objects.all()
    serializer_class = AddressSerializer


class ClientViewSet(viewsets.ModelViewSet):
    queryset = Client.objects.none()
    serializer_class = ClientSerializer

    def list(self, request, *args, **kwargs):
        return Response(
            {"detail": "client detail endpoint only"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    def retrieve(self, request, *args, **kwargs):
        try:
            client = get_client_by_pk(client_id=kwargs['pk'])
        except Client.DoesNotExist:
            return Response({"detail": "Not Found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = self.get_serializer(client)
        return Response(serializer.data)
