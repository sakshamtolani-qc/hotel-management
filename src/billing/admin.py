# Register your models here.
<<<<<<< HEAD
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

=======
>>>>>>> 5ba5004 (Add supabase (#10))
