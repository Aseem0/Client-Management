from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework import viewsets, status
from .models import Task, TaskGroup
from .serializers import TaskSerializer, TaskGroupSerializer
from users.permissions import IsAdminOrManager 
from django.shortcuts import get_object_or_404

class TaskGroupViewSet(viewsets.ModelViewSet):
    queryset = TaskGroup.objects.all()
    serializer_class = TaskGroupSerializer
    permission_classes = [IsAuthenticated, IsAdminOrManager]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

class TaskCreateView(APIView):
    permission_classes = [IsAuthenticated, IsAdminOrManager]

    def post(self, request):
        serializer = TaskSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            task = serializer.save()
            return Response({"message": "Task created and assigned successfully!", "task": TaskSerializer(task).data}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class TaskDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        task = get_object_or_404(Task, pk=pk)

        if getattr(request.user, 'role', None) == 'employee' and request.user not in task.assigned_to.all():
            return Response({"error": "Task not assigned to you"}, status=status.HTTP_403_FORBIDDEN)

        serializer = TaskSerializer(task)
        return Response(serializer.data, status=status.HTTP_200_OK)

class TaskListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        if getattr(user, 'role', None) in ['admin', 'manager']:
            tasks = Task.objects.all()
        else:
            tasks = Task.objects.filter(assigned_to=user)
        serializer = TaskSerializer(tasks, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class TaskUpdateDeleteView(APIView):
    permission_classes = [IsAuthenticated]

    def get_task(self, pk):
        return get_object_or_404(Task, pk=pk)

    def put(self, request, pk):
        task = self.get_task(pk)
        serializer = TaskSerializer(task, data=request.data, context={'request': request})
        if serializer.is_valid():
            task = serializer.save()
            return Response({"message": "Task updated successfully", "task": TaskSerializer(task).data})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk):
        task = self.get_task(pk)
        serializer = TaskSerializer(task, data=request.data, partial=True, context={'request': request})
        if serializer.is_valid():
            task = serializer.save()
            return Response({"message": "Task updated successfully", "task": TaskSerializer(task).data})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        task = self.get_task(pk)
        user = request.user
        if getattr(user, 'role', None) == 'employee':
            return Response({"error": "You cannot delete tasks"}, status=status.HTTP_403_FORBIDDEN)
        task.delete()
        return Response({"message": "Task deleted successfully"}, status=status.HTTP_200_OK)