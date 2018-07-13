# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import sys
from django.db import models
from django.core.exceptions import ValidationError
from .state import State
from myhpom.validators import validate_not_blank


class StateRequirement(models.Model):
    """an advance directive requirement for a given state.
    * state => State: the state in which this requirement applies. If null, global to all states.
    * position: the ordered position of the requirement in the list for this state (REQUIRED)
    * text: a textual description of the requirement (REQUIRED)
    * UNIQUE(state, order) -- protect against multiple items in the same position
    * UNIQUE(state, text) -- protect against multiple items with the same text
    """

    state = models.ForeignKey(State, on_delete=models.CASCADE, null=True, blank=True)
    position = models.PositiveSmallIntegerField()
    text = models.CharField(max_length=1024)

    class Meta:
        unique_together = (('state', 'position'), ('state', 'text'))
        ordering = ['-state', 'position']  # state=None (global requirements) first

    @classmethod
    def for_state(Class, state):
        """
        return the ordered list of requirements for this state, includes global then specific:
        """
        return Class.objects.filter(models.Q(state=None) | models.Q(state=state))


def state_requirement_pre_save_receiver(sender, instance, **kwargs):
    """
    * Ensure that the StateRequirement fields are valid before saving:
        * position: not blank
        * text: not blank
    """
    errors = []
    for key in ['position', 'text']:
        try:
            validate_not_blank(instance.__dict__.get(key))
        except ValidationError:
            errors.append(key + ': ' + ' '.join(sys.exc_info()[1]))

    if len(errors) > 0:
        raise ValidationError(errors)


models.signals.pre_save.connect(state_requirement_pre_save_receiver, sender=StateRequirement)
