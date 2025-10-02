from django.urls import path
from . import views

urlpatterns = [
    path('', views.BookingListView.as_view(), name='booking_list'),
    path('create/', views.BookingCreateView.as_view(), name='booking_create'),
    path('<int:pk>/', views.BookingDetailView.as_view(), name='booking_detail'),
    path('<int:pk>/edit/', views.BookingUpdateView.as_view(), name='booking_edit'),
    path('<int:pk>/delete/', views.BookingDeleteView.as_view(), name='booking_delete'),
    path('success/', views.booking_success, name='booking_success'),
    path('ajax/get_time_slots/', views.get_time_slots, name='get_time_slots'),
    path('ajax/get_price/', views.get_price, name='get_price'),
    path('ajax/get_commission_rate/', views.get_commission_rate, name='get_commission_rate'),
    path('ajax/get_available_discounts/', views.get_available_discounts, name='get_available_discounts'),
]
