from django.shortcuts import render, redirect
from django.contrib import auth
from myhpom import models
from myhpom.forms.signup_form import SignupForm
from myhpom.models import User, UserDetails, State


def signup(request):
    """
    TODO:
    * check to make sure the email isn't already taken
    * send an email to the user after signup
    * redirect to 'select_network' if the state is one that is supported
    """
    if request.method == "POST":
        form = SignupForm(request.POST)
        if form.is_valid():
            user_keys = ['first_name', 'last_name', 'email']
            user = User(**{k: v for k, v in form.fields.items() if k in user_keys})
            user.set_password(form.fields['password'])
            user.save()
            user_details = UserDetails.create(
                user=user, state=State.objects.get(name=form.fields['state'])
            )
            auth.login(request, user)
            redirect('next_steps')
        # else it falls through to re-display the page with errors
    else:
        form = SignupForm()

    # fall through to re-rendering the form
    return render(request, 'myhpom/accounts/signup.html', context={'form': form})
