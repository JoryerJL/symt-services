from service.models import Service
from apis.client.serializers import ClientSerializer
from apis.employee.serializers import EmployeeSerializer
from rest_framework import serializers

class ServiceSerializer(serializers.ModelSerializer):
    client = ClientSerializer(read_only=True)
    employee = EmployeeSerializer(read_only=True)
    status_name = serializers.CharField(source='get_status_display', read_only=True)
    class Meta:
        model = Service
        fields = '__all__'
        read_only_fields = ['client','employee', 'status']

class ServiceUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Service
        fields = '__all__'