from django.contrib import admin

from .models import Ticket


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ["id", "subject", "email", "status", "external_id", "created_at"]
    list_filter = ["status", "created_at"]
    search_fields = ["id", "subject", "email", "external_id"]
    ordering = ["-created_at"]
    date_hierarchy = "created_at"
    # Backend-managed fields: only the send flow may change status/external_id,
    # so staff cannot create inconsistent states such as "sent" without an external_id.
    readonly_fields = ["id", "status", "external_id", "created_at"]
    fields = ["id", "subject", "description", "email", "status", "external_id", "created_at"]
