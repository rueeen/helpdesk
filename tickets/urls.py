# tickets/urls.py
from django.urls import path
from .views import TicketListView, TicketDetailView, TicketCreateView, StatusUpdateView

urlpatterns = [
    path('', TicketListView.as_view(), name='ticket_list'),
    path('detail/<int:pk>/', TicketDetailView.as_view(), name='ticket_detail'),
    path('create/', TicketCreateView.as_view(), name='ticket_create'),
    path('update/<int:pk>/', StatusUpdateView.as_view(), name='status_update'),
]

