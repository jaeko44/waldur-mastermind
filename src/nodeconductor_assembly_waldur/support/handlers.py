from django.db import transaction

from nodeconductor.core import utils as core_utils

from .log import event_logger
from . import tasks, models


def log_issue_save(sender, instance, created=False, **kwargs):
    if created:
        return

    event_logger.waldur_issue.info(
        'Issue {issue_key} has been updated.',
        event_type='issue_update_succeeded',
        event_context={
            'issue': instance,
        })


def log_issue_delete(sender, instance, **kwargs):
    event_logger.waldur_issue.info(
        'Issue {issue_key} has been deleted.',
        event_type='issue_deletion_succeeded',
        event_context={
            'issue': instance,
        })


def log_offering_created(sender, instance, created=False, **kwargs):
    if created:
        event_logger.waldur_offering.info(
            'Offering {offering_name} has been created.',
            event_type='offering_created',
            event_context={
                'offering': instance,
            })


def log_offering_deleted(sender, instance, **kwargs):
    event_logger.waldur_offering.info(
        'Offering {offering_name} has been deleted.',
        event_type='offering_deleted',
        event_context={
            'offering': instance,
        })


def log_offering_state_changed(sender, instance, **kwargs):
    state = instance.state
    if state != instance.tracker.previous('state'):
        event_logger.waldur_offering.info(
            'Offering state has changed to {offering_state}',
            event_type='offering_state_changed',
            event_context={
                'offering': instance,
            }
        )


def send_comment_added_notification(sender, instance, created=False, **kwargs):
    comment = instance

    if not created or not comment.is_public:
        return

    serialized_comment = core_utils.serialize_instance(comment)
    transaction.on_commit(lambda:
                          tasks.send_comment_added_notification.delay(serialized_comment))


def send_issue_updated_notification(sender, instance, created=False, **kwargs):
    if created or set(instance.tracker.changed()) == {models.Issue.assignee.field.attname, 'modified'}:
        return

    serialized_issue = core_utils.serialize_instance(instance)
    transaction.on_commit(lambda:
                          tasks.send_issue_updated_notification.delay(serialized_issue))
