from rest_framework import viewsets, permissions
from rest_framework.response import Response
from rest_framework.decorators import action

# Example ViewSet:
# class InvoiceViewSet(viewsets.ModelViewSet):
#     permission_classes = [permissions.IsAuthenticated]
#     serializer_class = InvoiceSerializer
#     queryset = Invoice.objects.all()
