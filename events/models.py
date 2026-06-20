from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()


class Event(models.Model):
    name = models.CharField(max_length=100)
    date = models.DateField()
    location = models.CharField(max_length=200)
    description = models.TextField()
    created_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='created_events',
        null=True,
        blank=True
    )
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.name


class EventRegistration(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    )

    volunteer = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='event_registrations'
    )
    # MongoDB ObjectId as string
    event_id = models.CharField(max_length=24, null=True, blank=True)
    # Store event name for display
    event_name = models.CharField(max_length=100, null=True, blank=True)
    registered_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='pending'
    )

    class Meta:
        unique_together = ('volunteer', 'event_id')

    def __str__(self):
        event_name = self.event_name or 'Unknown Event'
        return f"{self.volunteer.username} - {event_name}"

    @property
    def event(self):
        """Return event details from MongoDB or fallback to stored name."""
        from volunteerhub.mongo import events_collection
        from bson import ObjectId

        if self.event_id:
            try:
                event = events_collection.find_one(
                    {'_id': ObjectId(self.event_id)}
                )
                if event:
                    return event
            except Exception:
                pass

        return {
            'name': self.event_name or 'Unknown Event',
            'date': None,
            'location': 'Unknown location',
        }


class Task(models.Model):
    STATUS_CHOICES = (
        ('assigned', 'Assigned'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('on_hold', 'On Hold'),
    )

    registration = models.ForeignKey(
        EventRegistration,
        on_delete=models.CASCADE,
        related_name='tasks'
    )
    title = models.CharField(max_length=150)
    description = models.TextField()
    status = models.CharField(
        max_length=15,
        choices=STATUS_CHOICES,
        default='assigned'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title} - {self.registration.volunteer.username}"
