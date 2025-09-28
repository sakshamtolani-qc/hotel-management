from django.urls import path
from billing.views import api as views

app_name = "billing"

urlpatterns = [
    # Invoices
    path("invoices/", views.InvoiceListCreateView.as_view(), name="invoice-list-create"),
    path("invoices/<int:pk>/", views.InvoiceDetailView.as_view(), name="invoice-detail"),
    path("invoices/<int:pk>/mark-paid/", views.MarkInvoicePaidView.as_view(), name="invoice-mark-paid"),
    path(
        "invoices/<int:pk>/send-payment-link/",
        views.SendPaymentLinkView.as_view(),
        name="invoice-send-payment-link",
    ),

    # Legacy/simple billing endpoints (optional)
    path("records/", views.BillingListCreateView.as_view(), name="billing-list-create"),
    path("records/<int:pk>/", views.BillingDetailView.as_view(), name="billing-detail"),
]
