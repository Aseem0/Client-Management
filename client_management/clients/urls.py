from django.urls import path
from .views import EmployeeListView,EmployeeDetailView

urlpatterns = [
    path('list_clients/', EmployeeListView.as_view(), name='employee-list'),
    path('client/<int:pk>/', EmployeeDetailView.as_view(), name='employee-detail')
]
