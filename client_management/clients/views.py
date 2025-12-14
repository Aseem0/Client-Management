from rest_framework.views import APIView
from rest_framework.response import Response
from users.models import User
from rest_framework import status
from users.serializers import UserSerializer
from users.permissions import IsAdminOrManager
from rest_framework.permissions import IsAuthenticated

class EmployeeListView(APIView):
    permission_classes = [IsAdminOrManager] 

    def get(self, request):
        employees = User.objects.filter(role='employee')
        serializer = UserSerializer(employees, many=True)
        return Response(serializer.data)

class EmployeeDetailView(APIView):
    permission_classes = [IsAuthenticated, IsAdminOrManager]

    def get_object(self, pk):
        try:
            return User.objects.get(pk=pk, role='employee')
        except User.DoesNotExist:
            return None

    def get(self, request, pk):
        employee = self.get_object(pk)
        if not employee:
            return Response({"error": "Employee not found"}, status=404)
        serializer = UserSerializer(employee)
        return Response(serializer.data)

    def put(self, request, pk):
        employee = self.get_object(pk)
        if not employee:
            return Response({"error": "Employee not found"}, status=404)
        serializer = UserSerializer(employee, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Employee updated successfully", "employee": serializer.data})
        return Response(serializer.errors, status=400)

    def patch(self, request, pk):
        employee = self.get_object(pk)
        if not employee:
            return Response({"error": "Employee not found"}, status=404)
        serializer = UserSerializer(employee, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Employee updated successfully", "employee": serializer.data})
        return Response(serializer.errors, status=400)

    def delete(self, request, pk):
        employee = self.get_object(pk)
        if not employee:
            return Response({"error": "Employee not found"}, status=404)
        employee.delete()
        return Response({"message": "Employee deleted successfully"})