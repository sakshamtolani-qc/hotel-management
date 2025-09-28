# Generated manually to make timestamps non-nullable without interactive prompt
from django.db import migrations, models
import django.utils.timezone as timezone


class Migration(migrations.Migration):
    dependencies = [
        ("rooms", "0002_update_room_model_frontend_alignment.py".replace(".py", "")),
    ]

    operations = [
        migrations.AlterField(
            model_name="room",
            name="created_at",
            field=models.DateTimeField(auto_now_add=True, default=timezone.now),
        ),
        migrations.AlterField(
            model_name="room",
            name="updated_at",
            field=models.DateTimeField(auto_now=True, default=timezone.now),
        ),
    ]
