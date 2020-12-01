from enum import Enum

from django.db import models


class VariableTypeEnum(Enum):
    BOOLEAN = 'boolean'
    STRING = 'string'
    BYTES = 'bytes'
    SHORT = 'short'
    INTEGER = 'integer'
    LONG = 'long'
    DOUBLE = 'double'
    DATE = 'date'
    NULL = 'null'


class Variable(models.Model):
    """Camunda Variable Model"""
    process_definition = models.ForeignKey('camunda.ProcessDefinition', on_delete=models.PROTECT, related_name='variables')
    required_variable = models.ForeignKey('self', on_delete=models.SET_NULL, related_name='+', blank=True, null=True)  # When there are many gateways after complete a task
    value_to_be_required = models.CharField(max_length=50, blank=True, null=True)  # For required_variable
    name = models.CharField(max_length=50)
    type = models.CharField(max_length=10, choices=[(x.value, str(x.name).title()) for x in VariableTypeEnum], default=VariableTypeEnum.BOOLEAN.value)
    options = models.CharField(max_length=255, default='true,false')

    def __str__(self):
        return self.name


class VariableDetail(models.Model):
    """Camunda Variable Instance Model"""
    process_instance = models.ForeignKey('camunda.ProcessInstance', on_delete=models.CASCADE, related_name='variables')
    variable = models.ForeignKey(Variable, related_name='+', on_delete=models.PROTECT)
    value = models.CharField(max_length=50)

    def __str__(self):
        return self.value
