from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth import get_user_model

User = get_user_model()


class CustomUserAdmin(UserAdmin):
    list_display = (
        "username",
        "email",
        "first_name",
        "last_name",
        "user_type",
        "phone_number",
        "is_staff",
    )
    list_filter = ("user_type", "is_staff", "is_superuser", "is_active")
    fieldsets = UserAdmin.fieldsets + (
        (
            "Additional Info",
            {
                "fields": (
                    "phone_number",
                    "address",
                    "city",
                    "state",
                    "zip_code",
                    "country",
                    "id_document_number",
                    "date_of_birth",
                    "user_type",
                )
            },
        ),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        (
            "Additional Info",
            {
                "classes": ("wide",),
                "fields": (
                    "email",
                    "phone_number",
                    "address",
                    "city",
                    "state",
                    "zip_code",
                    "country",
                    "id_document_number",
                    "date_of_birth",
                    "user_type",
                ),
            },
        ),
    )


admin.site.register(User, CustomUserAdmin)
