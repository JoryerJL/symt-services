from employee.models import Employee
from rest_framework import serializers


class EmployeeSerializer(serializers.ModelSerializer):
    organization_id = serializers.IntegerField(source='organization.id', read_only=True)
    organization_slug = serializers.CharField(source='organization.slug', read_only=True)

    class Meta:
        model = Employee
        fields = [
            'id',
            'first_name',
            'last_name',
            'phone_number',
            'chat_id',
            'organization_id',
            'organization_slug',
        ]
        read_only_fields = ['organization_id', 'organization_slug']
