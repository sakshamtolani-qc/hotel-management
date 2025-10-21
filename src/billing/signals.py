from django.db.models.signals import post_save
from django.dispatch import receiver
from decimal import Decimal
from django.utils import timezone
from datetime import timedelta
from reservations.models import Reservation
from billing.models import Invoice, InvoiceItem
from django.conf import settings
from django.contrib.auth import get_user_model
import logging

User = get_user_model()
logger = logging.getLogger(__name__)

@receiver(post_save, sender=Reservation)
def create_invoice_for_reservation(sender, instance: Reservation, created, **kwargs):
    """
    Auto-generate an invoice when a Reservation is created.
    - subtotal = room.price_per_night * total_days
    - tax = 10% of subtotal
    - grand_total = subtotal + tax
    - due_date = invoice.date + 1 day (D3)
    """
    if not created:
        return

    try:
        # Use correct date fields
        check_in = instance.check_in_date
        check_out = instance.check_out_date
        total_days = (check_out - check_in).days or 1

        # Resolve room price
        room = getattr(instance, "room", None)
        if room:
            price_per_day = Decimal(str(getattr(room, "price_per_night", getattr(room, "price", 0))))
        else:
            price_per_day = Decimal(str(getattr(instance, "price", 0)))

        subtotal = (price_per_day * Decimal(total_days)).quantize(Decimal("0.01"))
        tax = (subtotal * Decimal("0.10")).quantize(Decimal("0.01"))
        grand_total = (subtotal + tax).quantize(Decimal("0.01"))

        # Use reservation_id or pk instead of id
        invoice_number = f"INV-{getattr(instance, 'reservation_id', instance.pk)}-{timezone.now().strftime('%Y%m%d%H%M%S')}"

        invoice_date = timezone.now().date()
        due_date = invoice_date + timedelta(days=1)

        user = getattr(instance, "user", None) or getattr(instance, "guest", None)

        # Create invoice
        invoice = Invoice.objects.create(
            reservation=instance,
            user=user if user else User.objects.first(),
            invoice_number=invoice_number,
            date=invoice_date,
            due_date=due_date,
            payment_status=Invoice.PaymentStatus.PENDING,
            bill_to_name=getattr(instance, "guest_name", getattr(user, "get_full_name", "") if user else ""),
            bill_to_phone=getattr(instance, "guest_phone", getattr(user, "phone", "")),
            bill_to_address=getattr(instance, "guest_address", "") or getattr(user, "email", ""),
            subtotal=subtotal,
            tax=tax,
            grand_total=grand_total,
        )

        # Create invoice item for room
        item_no = f"ROOM-{getattr(room, 'number', getattr(instance, 'reservation_id', instance.pk))}" if room else f"ROOM-{getattr(instance, 'reservation_id', instance.pk)}"
        description = getattr(room, "title", "Room Charges") if room else "Room Charges"
        InvoiceItem.objects.create(
            invoice=invoice,
            item_no=item_no,
            description=description,
            quantity=total_days,
            price=price_per_day,
            total=subtotal,
        )

    except Exception as e:
        # Safe logging using reservation_id or pk
        logger.exception(f"Error auto-creating invoice for reservation {getattr(instance, 'reservation_id', instance.pk)}: {e}")
