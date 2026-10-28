import uuid

from django.db import models


class Ticket(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        SENT = "sent", "Sent"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    subject = models.CharField(max_length=120)
    description = models.CharField(max_length=2000)
    email = models.EmailField()
    status = models.CharField(
        max_length=16, choices=Status.choices, default=Status.PENDING
    )
    # Django stores aware datetimes in UTC because settings.USE_TZ=True and TIME_ZONE="UTC".
    created_at = models.DateTimeField(auto_now_add=True)
    external_id = models.CharField(max_length=128, null=True, blank=True)

    class Meta:
        ordering = ["created_at"]

    def __str__(self) -> str:
        return f"Ticket {self.id} ({self.status})"
