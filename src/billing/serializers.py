from rest_framework import serializers
from billing.models import Billing


class BillingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Billing
        fields = "__all__"
        read_only_fields = ["id", "created_at", "updated_at"]