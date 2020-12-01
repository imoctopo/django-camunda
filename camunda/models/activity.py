from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone


class Activity(models.Model):
    """Camunda Activity model"""
    process_definition = models.ForeignKey('camunda.ProcessDefinition', on_delete=models.CASCADE, related_name='tasks')
    name = models.CharField(max_length=100)
    key = models.CharField(max_length=100)
    variables_for_next_activity = models.ManyToManyField('camunda.Variable', blank=True)
    system = models.BooleanField(default=False)  # A system activity
    first_activity_next_process = models.ForeignKey('self', on_delete=models.PROTECT, blank=True, null=True)  # First activity for the next process
    first_activity_next_process_required_value = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
        return self.name


class ActivityInstance(models.Model):
    """Camunda Activity Instance model"""
    instance_id = models.CharField(max_length=100)  # id in json response
    activity = models.ForeignKey(Activity, on_delete=models.PROTECT, related_name='instances')
    process_instance = models.ForeignKey('camunda.ProcessInstance', on_delete=models.CASCADE, related_name='activities')
    finished = models.BooleanField(default=False)
    # For system activities with timer. This flag means that the activity instance has a reply.
    has_reply = models.BooleanField(default=False)

    created = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    completed = models.DateTimeField(blank=True, null=True)
    completed_by = models.ForeignKey('auth.User', on_delete=models.PROTECT, blank=True, null=True)
    due = models.DateTimeField(null=True)

    def __str__(self):
        return self.activity.name

    def finish(self, user: AbstractUser = None):
        """User can't be an AbstractUser's instance, pass a instance of model that inherits from AbstractUser instead."""
        self.finished = True
        self.completed = timezone.now()
        self.completed_by = user
        self.save()
