from employee.models import Employee
from employee.selectors import (
    get_employee_by_chat_id,
    get_employee_by_phone,
    get_employee_by_pk,
)
from employee.services import employee_update_chat_id
from .serializers import EmployeeSerializer
from rest_framework.response import Response
from rest_framework import viewsets, status


class EmployeeViewSet(viewsets.ModelViewSet):
    queryset = Employee.objects.none()
    serializer_class = EmployeeSerializer

    def list(self, request, *args, **kwargs):
        phone_number = request.query_params.get('phone_number', None)
        chat_id = request.query_params.get('chat_id', None)
        try:
            if chat_id:
                employee = get_employee_by_chat_id(chat_id=chat_id)
            elif phone_number:
                employee = get_employee_by_phone(phone_number=phone_number[-10:])
            else:
                return Response(
                    {"detail": "chat_id or phone_number is required"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        except Employee.DoesNotExist:
            return Response({"detail": "Not Found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = self.get_serializer(employee)
        return Response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        try:
            employee = get_employee_by_pk(employee_id=kwargs['pk'])
        except Employee.DoesNotExist:
            return Response({"detail": "Not Found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = self.get_serializer(employee)
        return Response(serializer.data)

    def update(self, request, *args, **kwargs):
        chat_id = request.data.get('chat_id')
        if chat_id is None:
            return Response(
                {"chat_id": ["This field is required."]},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            employee = get_employee_by_pk(employee_id=kwargs['pk'])
        except Employee.DoesNotExist:
            return Response({"detail": "Not Found"}, status=status.HTTP_404_NOT_FOUND)

        employee = employee_update_chat_id(employee=employee, chat_id=str(chat_id))
        serializer = self.get_serializer(employee)
        return Response(serializer.data)
