from rest_framework import serializers
from billing.models import Billing, Invoice, InvoiceItem
from decimal import Decimal


class BillingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Billing
        fields = "__all__"
        read_only_fields = ["id", "created_at", "updated_at"]


class InvoiceItemSerializer(serializers.ModelSerializer):
    itemNo = serializers.CharField(source="item_no")
    description = serializers.CharField(required=False, allow_blank=True)
    quantity = serializers.IntegerField()
    price = serializers.DecimalField(max_digits=10, decimal_places=2)
    total = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)

    class Meta:
        model = InvoiceItem
        fields = [
            "id",
            "itemNo",
            "description",
            "quantity",
            "price",
            "total",
        ]
        read_only_fields = ["id"]


class BillToSerializer(serializers.Serializer):
    name = serializers.CharField()
    phone = serializers.CharField()
    address = serializers.CharField()


class InvoiceSerializer(serializers.ModelSerializer):
    invoiceNumber = serializers.CharField(source="invoice_number")
    dueDate = serializers.DateField(source="due_date")
    paymentStatus = serializers.ChoiceField(source="payment_status", choices=Invoice.PaymentStatus.choices)
    billTo = BillToSerializer(write_only=True)
    subtotal = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    tax = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    grandTotal = serializers.DecimalField(source="grand_total", max_digits=10, decimal_places=2, read_only=True)
    paymentMethod = serializers.CharField(source="payment_method", required=False, allow_blank=True, allow_null=True)
    transactionId = serializers.CharField(source="transaction_id", required=False, allow_blank=True, allow_null=True)
    items = InvoiceItemSerializer(many=True)

    class Meta:
        model = Invoice
        fields = [
            "id",
            "invoiceNumber",
            "date",
            "dueDate",
            "paymentStatus",
            "billTo",
            "subtotal",
            "tax",
            "grandTotal",
            "paymentMethod",
            "transactionId",
            "notes",
            "items",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at", "subtotal", "tax", "grandTotal"]

    def to_representation(self, instance):
        data = super().to_representation(instance)
        # Inject billTo from model fields
        data["billTo"] = {
            "name": instance.bill_to_name,
            "phone": instance.bill_to_phone,
            "address": instance.bill_to_address,
        }
        return data

    def _recalculate_totals(self, items_data):
        subtotal = sum(
            Decimal(str(item.get("quantity", 0))) * Decimal(str(item.get("price", 0)))
            for item in items_data
        )
        tax = (subtotal * Decimal("0.10")).quantize(Decimal("0.01"))  # 10% tax
        grand_total = (subtotal + tax).quantize(Decimal("0.01"))
        return subtotal, tax, grand_total

    def create(self, validated_data):
        items_data = validated_data.pop("items", [])
        bill_to = validated_data.pop("billTo", {})
        request = self.context.get("request")
        user = request.user if request else None

        # Compute totals based on items
        subtotal, tax, grand_total = self._recalculate_totals(items_data)
        invoice = Invoice.objects.create(
            user=user,
            bill_to_name=bill_to.get("name", ""),
            bill_to_phone=bill_to.get("phone", ""),
            bill_to_address=bill_to.get("address", ""),
            subtotal=subtotal,
            tax=tax,
            grand_total=grand_total,
            **validated_data,
        )

        for item in items_data:
            quantity = Decimal(str(item.get("quantity", 0)))
            price = Decimal(str(item.get("price", 0)))
            total = (quantity * price).quantize(Decimal("0.01"))
            # itemNo is mapped by source to item_no
            InvoiceItem.objects.create(invoice=invoice, total=total, **item)

        return invoice

    def update(self, instance, validated_data):
        items_data = validated_data.pop("items", None)
        bill_to = validated_data.pop("billTo", None)

        # Update simple fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        if bill_to is not None:
            instance.bill_to_name = bill_to.get("name", instance.bill_to_name)
            instance.bill_to_phone = bill_to.get("phone", instance.bill_to_phone)
            instance.bill_to_address = bill_to.get("address", instance.bill_to_address)

        # Replace items if provided
        if items_data is not None:
            instance.items.all().delete()
            for item in items_data:
                quantity = Decimal(str(item.get("quantity", 0)))
                price = Decimal(str(item.get("price", 0)))
                total = (quantity * price).quantize(Decimal("0.01"))
                InvoiceItem.objects.create(invoice=instance, total=total, **item)

            # Recompute totals
            subtotal, tax, grand_total = self._recalculate_totals(items_data)
            instance.subtotal = subtotal
            instance.tax = tax
            instance.grand_total = grand_total

        instance.save()
        return instance
