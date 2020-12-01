from django.db import models
from django.utils import timezone


class ProcessDefinition(models.Model):
    """Process Definition model"""
    definition_id = models.CharField(max_length=100)
    key = models.CharField(max_length=100)
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class ProcessInstance(models.Model):
    """Process Instance model"""
    instance_id = models.CharField(max_length=100)
    process_definition = models.ForeignKey(ProcessDefinition, on_delete=models.PROTECT)
    business_key = models.CharField(max_length=100, null=True)
    case_instance_id = models.CharField(max_length=100, null=True)
    ended = models.BooleanField(default=False)
    suspended = models.BooleanField(default=False)
    tenant_id = models.CharField(max_length=100, null=True)

    created = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated = models.DateTimeField(auto_now=True, null=True, blank=True)
    completed = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return self.instance_id

    def finish(self):
        self.ended = True
        self.completed = timezone.now()
        self.save()
