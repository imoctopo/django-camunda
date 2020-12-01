from typing import Union

from django.db import models
from .process import ProcessDefinition, ProcessInstance
from .variable import Variable


class CamundaModelBase(models.Model):
    """All models that uses Camunda should inherit of this model"""
    current_activity = models.OneToOneField('camunda.ActivityInstance', on_delete=models.PROTECT, blank=True, null=True, related_name='+')
    completed_activities = models.ManyToManyField('camunda.ActivityInstance', blank=True)
    completed_processes = models.ManyToManyField('camunda.ProcessInstance', blank=True)

    class Meta:
        abstract = True

    @property
    def current_process_definition(self) -> Union[ProcessDefinition, None]:
        if self.current_activity:
            return self.current_activity.process_instance.process_definition
        return None

    @property
    def current_process_instance(self) -> Union[ProcessInstance, None]:
        if self.current_activity:
            return self.current_activity.process_instance
        return None

    def variables_for_next_activity(self, variables: dict):
        # If there is not current activity, then the process is finished
        if not self.current_activity:
            return False
        required_variables = set()
        variables_for_next_activity = self.current_activity.activity.variables_for_next_activity.all()
        for var in variables_for_next_activity:
            required_variables.add(var.name)
            recursive_variables = self._get_required_variable(var, variables)
            required_variables = required_variables | recursive_variables

        # Check if all the variables's name are valid and the value is in the options
        variables_list = list(required_variables)
        variables_list = Variable.objects.filter(name__in=variables_list, process_definition_id=self.current_activity.process_instance.process_definition.id)
        variables_options = {var.name: str(var.options).split(',') for var in variables_list}
        not_valid_variables = []
        not_valid_values = []
        for key, value in variables.items():
            if key in variables_options:
                if type(value) is bool:
                    value = str(value).lower()
                if value not in variables_options[key]:
                    not_valid_values.append({key: value, 'expected_Values': variables_options[key]})
            else:
                not_valid_variables.append(key)

        if not_valid_variables or not_valid_values:
            return {
                'not_valid_variables': not_valid_variables,
                'expected_variables': list(required_variables),
                'not_valid_values': not_valid_values
            }
        return required_variables

    def _get_required_variable(self, var: Variable, variables: dict):
        """
        If the value of the current variable is equal to the value_to_be_required value,
        then add current variable's required_variable to required_variables set.
        This functions calls itself recursively if var has required_variable and value_to_be_required is equals to required value.
        """
        required_variables = set()
        if var.required_variable:  # If variable of variables_for_next_activity has required_variable
            current_variable_value = variables[var.name] if var.name in variables else None
            # If is boolean, cast to string and convert to lowercase
            if type(current_variable_value) is bool:
                current_variable_value = str(current_variable_value).lower()
            if current_variable_value == var.value_to_be_required:
                required_variables.add(var.required_variable.name)
                # If variable has required_variable, call this function recursively
                if var.required_variable.required_variable:
                    child = self._get_required_variable(var.required_variable, variables)
                    required_variables = required_variables | child
        return required_variables
