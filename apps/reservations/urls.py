from django.urls import path
from .views import ReservationCreateView, UserReservationsView

urlpatterns = [
    path('', ReservationCreateView.as_view(), name='reservation-create'),
    path('user/', UserReservationsView.as_view(), name='user-reservations'),
]