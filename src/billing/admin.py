from django.contrib import admin
from billing.models import Billing, Invoice, InvoiceItem


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


class InvoiceItemInline(admin.TabularInline):
    model = InvoiceItem
    extra = 0


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = (
        "invoice_number",
        "user",
        "payment_status",
        "grand_total",
        "date",
        "due_date",
        "created_at",
    )
    list_filter = ("payment_status", "date", "due_date", "created_at")
    search_fields = ("invoice_number", "bill_to_name", "bill_to_phone", "transaction_id")
    inlines = [InvoiceItemInline]
