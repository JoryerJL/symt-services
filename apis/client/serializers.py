from client.models import Client, Address
from rest_framework import serializers

class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = '__all__'

class ClientSerializer(serializers.ModelSerializer):
    address = AddressSerializer()
    class Meta:
        model = Client
        fields = '__all__'
        read_only_fields = ['address',]