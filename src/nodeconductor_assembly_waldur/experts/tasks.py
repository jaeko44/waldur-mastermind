from __future__ import unicode_literals

import logging

from celery import shared_task
from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string

from nodeconductor.structure import models as structure_models
from . import models

logger = logging.getLogger(__name__)


def get_request_customer_link(request, customer):
    return settings.WALDUR_EXPERTS['REQUEST_CUSTOMER_LINK_TEMPLATE'].format(
        request_uuid=request.uuid.hex,
        customer_uuid=customer.uuid.hex
    )


def get_request_project_link(request):
    return settings.WALDUR_EXPERTS['REQUEST_PROJECT_LINK_TEMPLATE'].format(
        request_uuid=request.uuid.hex,
        project_uuid=request.project.uuid.hex
    )


@shared_task(name='nodeconductor_assembly_waldur.experts.send_new_request')
def send_new_request(request_uuid):
    """
    Send email notification about new expert request.
    """

    request = models.ExpertRequest.objects.get(uuid=request_uuid)

    enabled_providers = models.ExpertProvider.objects.filter(enable_notifications=True)
    customers = list(enabled_providers.values_list('customer', flat=True))
    customers = structure_models.Customer.objects.filter(pk__in=customers)
    for customer in customers:
        users = customer.get_owners()
        extra_context = {
            'request_link': get_request_customer_link(request, customer)
        }
        send_request_mail('new_request', request, users, extra_context)


@shared_task(name='nodeconductor_assembly_waldur.experts.send_new_bid')
def send_new_bid(bid_uuid):
    """
    Send email notification about new bid.
    """

    bid = models.ExpertBid.objects.get(uuid=bid_uuid)
    users = bid.request.customer.get_owners()
    extra_context = {
        'bid': bid,
        'request_link': get_request_project_link(bid.request)
    }
    send_request_mail('new_bid', bid.request, users, extra_context)


@shared_task(name='nodeconductor_assembly_waldur.experts.send_new_contract')
def send_new_contract(request_uuid):
    """
    Send email notification about accepted expert request.
    """

    request = models.ExpertRequest.objects.get(uuid=request_uuid)
    users = request.customer.get_owners()
    extra_context = {
        'request_link': get_request_project_link(request)
    }
    send_request_mail('contract', request, users, extra_context)


def send_request_mail(event_type, request, users, extra_context=None):
    """
    Shorthand to send email notification about expert request event.
    """

    recipient_list = list(users.exclude(email='').values_list('email', flat=True))

    context = dict(
        request=request,
        customer_name=request.project.customer.name,
        project_name=request.project.name,
        currency_name=settings.WALDUR_EXPERTS['CURRENCY_NAME'],
        site_name=settings.WALDUR_EXPERTS['SITE_NAME'],
    )
    if extra_context:
        context.update(extra_context)

    logger.debug('About to send expert request {request_name} to {recipient_list}.'.format(
        request_name=request.name,
        recipient_list=', '.join(recipient_list)
    ))

    broadcast_mail('experts', event_type, context, recipient_list)


# TODO: Move to waldur-core
def broadcast_mail(app, event_type, context, recipient_list):
    """
    Shorthand to format email message from template file and sent it to all recipients.

    It is assumed that there are there are 3 templates available for event type in application.
    For example, if app is 'experts' and event_type is 'new_request', then there should be 3 files:

    1) experts/new_request_subject.txt is template for email subject
    2) experts/new_request_message.txt is template for email body as text
    3) experts/new_request_message.html is template for email body as HTML

    By default, built-in Django send_mail is used, all members
    of the recipient list will see the other recipients in the 'To' field.
    Contrary to this, we're using explicit loop in order to ensure that
    recipients would NOT see the other recipients.

    :param app: prefix for template filename.
    :param event_type: postfix for template filename.
    :param context: dictionary passed to the template for rendering.
    :param recipient_list: list of strings, each an email address.
    """

    subject_template = '%s/%s_subject.txt' % (app, event_type)
    text_template = '%s/%s_message.txt' % (app, event_type)
    html_template = '%s/%s_message.html' % (app, event_type)

    subject = render_to_string(subject_template, context).strip()
    text_message = render_to_string(text_template, context)
    html_message = render_to_string(html_template, context)

    for recipient in recipient_list:
        send_mail(subject, text_message, settings.DEFAULT_FROM_EMAIL, [recipient], html_message=html_message)
