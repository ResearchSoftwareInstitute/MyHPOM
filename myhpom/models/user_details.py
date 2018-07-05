from django.db import models
from .user import User
from .state import State


class UserDetails(models.Model):
    """Added user details to that are included when the user signs up.
    * user = the User object that these details are associated with
    * state = the State that this user belongs to.
    * middle_name = because it's not in the User model
    * accept_tos = the user has checked/affirmed the "Terms and Conditions".
    """

    user = models.OneToOneField(User)
    state = models.ForeignKey(State, on_delete=models.SET_NULL, null=True, blank=True)
    middle_name = models.CharField(max_length=30, null=True, blank=True)
    accept_tos = models.NullBooleanField()
