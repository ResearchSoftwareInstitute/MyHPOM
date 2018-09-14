import json
import requests
import traceback
from collections import OrderedDict
from django.core.mail import send_mail
from django.template.loader import get_template
from django.template import Context
from celery import shared_task
from myhpom.models import AdvanceDirective, DocumentUrl, CloudFactoryRun


@shared_task
def submit_advancedirective_to_cloudfactory(ad_id, line_id, document_host=None, callback_url=None):
    """ 
    * ad_id = the database id for the AdvanceDirective
    * line_id = the id of the CloudFactory production line to submit this request to.
    * document_host = the host to use for the DocumentURL
    * callback_url = the URL to use with the callback request

    - create an expiring DocumentUrl for the AdvanceDirective
    - submit the DocumentUrl to the CloudFactory (test) endpoint
    - store the status of the submitted document
    - if an error occurs in this process, send support email.
        - the AdvanceDirective might no longer exist by the time celery picks it up,
        - or the document it points to might have been removed.
    """
    # if an error occurs while building the post_data, don't send support email,
    # but do let celery catch the exception and return it with the task status.
    ad = AdvanceDirective.objects.get(id=ad_id)
    document_url = DocumentUrl.objects.create(advancedirective=ad)
    run = CloudFactoryRun(line_id=line_id, callback_url=callback_url or "")
    unit = CloudFactoryUnit(
        run=run, input=cloudfactory_advancedirective_unit_input(document_url, document_host)
    )
    post_data = run.post_data()

    # if an error occurs in posting the run to CloudFactory, send support email
    try:
        response = requests.post(settings.CLOUDFACTORY_API_URL, json=post_data)
        response_data = response.json()

        if response.status_code != 201:
            run.__dict__.update(status=str(response.status_code), message=response_data['message'])
            run.save()
            raise ValueError(response_data['message'] + '\n' + json.dumps(post_data, indent=2))

        run.__dict__.update(
            run_id=rundata['id'], status=rundata['status'], created_at=rundata['created_at']
        )
        run.save()
        return run

    except exc:
        tb = traceback.format_tb(exc_info[2])
        message = get_template('myhpom/celery_task_error_email.txt').render(
            Context({'sections': OrderedDict(traceback=tb, run=json.dumps(run.data(), indent=2))})
        )
        send_mail(
            'MMH Celery Error', message, settings.DEFAULT_FROM_EMAIL, settings.DEFAULT_SUPPORT_EMAIL
        )
        raise exc


# The following helper function doesn't really belong in any of the models
# -- neither the CloudFactoryUnit model nor the DocumentUrl model should "know" about this task --
# so, it's here with the task.


def cloudfactory_advancedirective_unit_input(document_url, document_host=None):
    """For a given DocumentUrl object, return the unit input that cloud factory expects.
    see https://docs.google.com/document/d/1VHD3iVq2Ky_SblQScv9O7tlphv9QHllMpGvn-bkWM_8/edit
    """
    ad = document_url.advancedirective
    unit_input = {
        'full_name': ' '.join(
            name
            for name in [ad.user.first_name, ad.user.userdetails.middle_name, ad.user.last_name]
            if name != ''  # in the not-uncommon case that one of the names is blank
        ),
        'state': ad.user.state.name,
        'pdf_url': "%s%s" % (document_host or '', document_url.url),
        'date_signed': str(ad.valid_date),
    }
    return unit_input
