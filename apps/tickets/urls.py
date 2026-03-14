from django.urls import path
from .views import PurchaseView

# Resumen:
# Ruta de compra de tickets.
urlpatterns = [
    # POST /api/v1/tickets/purchase/
    path('purchase/', PurchaseView.as_view(), name='purchase'),
]