from .serializers import AddressSerializer, ClientSerializer
from client.models import Client, Address
from rest_framework import viewsets

class AddressViewSet(viewsets.ModelViewSet):
    queryset = Address.objects.all()
    serializer_class = AddressSerializer

class ClientViewSet(viewsets.ModelViewSet):
    queryset = Client.objects.all()
    serializer_class = ClientSerializer