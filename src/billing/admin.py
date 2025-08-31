# Register your models here.
from django.contrib import admin
from billing.models import Billing


@admin.register(Billing)
class BillingAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        # "reservation",
        "user",
        "total_amount",
        "payment_status",
        "created_at",
    )
    list_filter = ("payment_status", "payment_method", "created_at")
    search_fields = ("transaction_id", "reservation__id", "user__username")
