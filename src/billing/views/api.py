from rest_framework import generics, permissions, filters, status
from rest_framework.response import Response
from billing.models import Billing, Invoice
from billing.serializers import BillingSerializer, InvoiceSerializer

# billing/views/api.py (or extend your existing views file)
from django.shortcuts import get_object_or_404

class InvoiceByReservationView(generics.RetrieveAPIView):
    """
    Return the invoice created for a reservation id.
    GET /api/billing/invoices/by-reservation/<reservation_id>/
    """
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = InvoiceSerializer
    lookup_field = "reservation_id"

    def get(self, request, reservation_id, *args, **kwargs):
        invoice = get_object_or_404(Invoice, reservation__id=reservation_id)
        serializer = self.get_serializer(invoice)
        return Response(serializer.data, status=status.HTTP_200_OK)


class BillingListCreateView(generics.ListCreateAPIView):
    queryset = Billing.objects.all()
    serializer_class = BillingSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["user__username", "transaction_id"]
    ordering_fields = ["created_at", "total_amount", "payment_status"]
    ordering = ["-created_at"]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class BillingDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Billing.objects.all()
    serializer_class = BillingSerializer
    permission_classes = [permissions.IsAuthenticated]


class InvoiceListCreateView(generics.ListCreateAPIView):
    queryset = Invoice.objects.all().order_by("-created_at")
    serializer_class = InvoiceSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["invoice_number", "bill_to_name", "bill_to_phone", "transaction_id"]
    ordering_fields = ["created_at", "grand_total", "payment_status", "due_date"]
    ordering = ["-created_at"]

    def perform_create(self, serializer):
        serializer.save()


class InvoiceDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Invoice.objects.all()
    serializer_class = InvoiceSerializer
    permission_classes = [permissions.IsAuthenticated]


class MarkInvoicePaidView(generics.UpdateAPIView):
    queryset = Invoice.objects.all()
    serializer_class = InvoiceSerializer
    permission_classes = [permissions.IsAuthenticated]

    def update(self, request, *args, **kwargs):
        invoice = self.get_object()
        invoice.payment_status = Invoice.PaymentStatus.PAID
        invoice.save()
        return Response(self.get_serializer(invoice).data, status=status.HTTP_200_OK)


class SendPaymentLinkView(generics.RetrieveAPIView):
    queryset = Invoice.objects.all()
    serializer_class = InvoiceSerializer
    permission_classes = [permissions.IsAuthenticated]

    def retrieve(self, request, *args, **kwargs):
        # Stub: In a real system, you'd generate and send a payment link here
        invoice = self.get_object()
        return Response(
            {
                "message": "Payment link sent",
                "invoice_id": invoice.id,
                "invoice_number": invoice.invoice_number,
            },
            status=status.HTTP_200_OK,
        )
