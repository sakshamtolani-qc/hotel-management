from rest_framework import generics, permissions, filters
from billing.models import Billing
from billing.serializers import BillingSerializer


class BillingListCreateView(generics.ListCreateAPIView):
    queryset = Billing.objects.all()
    serializer_class = BillingSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["reservation__id", "user__username", "transaction_id"]
    ordering_fields = ["created_at", "total_amount", "payment_status"]
    ordering = ["-created_at"]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class BillingDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Billing.objects.all()
    serializer_class = BillingSerializer
    permission_classes = [permissions.IsAuthenticated]