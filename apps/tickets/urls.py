from django.urls import path
from .views import PurchaseView

urlpatterns = [
    path('purchase/', PurchaseView.as_view(), name='purchase'),
]