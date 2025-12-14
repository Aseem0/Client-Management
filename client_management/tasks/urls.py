from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TaskCreateView, TaskUpdateDeleteView, TaskListView, TaskDetailView, TaskGroupViewSet

router = DefaultRouter()
router.register(r'groups', TaskGroupViewSet, basename='taskgroup')

urlpatterns = [
    path('create/', TaskCreateView.as_view(), name='task-create'),
    path('my-tasks/', TaskListView.as_view(), name='task-list'),
    path('update/<int:pk>/', TaskUpdateDeleteView.as_view(), name='task-update'),
    path('detail/<int:pk>/', TaskDetailView.as_view(), name='task-detail'),
    path('', include(router.urls)),
]
