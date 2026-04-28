from employee.models import Employee
from .serializers import EmployeeSerializer
from rest_framework.response import Response
from rest_framework import viewsets, status


class EmployeeViewSet(viewsets.ModelViewSet):
    queryset = Employee.objects.all()
    serializer_class = EmployeeSerializer

    def list(self, request, *args, **kwargs):
        phone_number = request.query_params.get('phone_number', None)
        chat_id = request.query_params.get('chat_id', None)
        if phone_number:
            queryset = self.get_queryset().filter(phone_number=phone_number)
        elif chat_id:
            queryset = self.get_queryset().filter(chat_id=chat_id)
        else:
            queryset = self.get_queryset()

        if not queryset.exists():
            return Response({"detail": "Not Found"}, status=status.HTTP_404_NOT_FOUND)

        if phone_number or chat_id:
            serializer = self.get_serializer(queryset.first())
            return Response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)

        return Response(serializer.data)

