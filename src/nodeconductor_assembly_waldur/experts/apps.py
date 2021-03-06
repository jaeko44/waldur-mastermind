from __future__ import unicode_literals

from django.apps import AppConfig
from django.db.models import signals


class ExpertsConfig(AppConfig):
    name = 'nodeconductor_assembly_waldur.experts'
    verbose_name = 'Experts'

    def ready(self):
        from nodeconductor.structure import models as structure_models
        from nodeconductor_assembly_waldur.invoices import registrators as invoices_registrators
        from . import handlers, registrators

        ExpertRequest = self.get_model('ExpertRequest')
        ExpertBid = self.get_model('ExpertBid')
        ExpertContract = self.get_model('ExpertContract')

        invoices_registrators.RegistrationManager.add_registrator(
            ExpertRequest,
            registrators.ExpertRequestRegistrator
        )

        signals.post_save.connect(
            handlers.add_completed_expert_request_to_invoice,
            sender=ExpertRequest,
            dispatch_uid='nodeconductor_assembly_waldur.experts.handlers.'
                         'add_completed_expert_request_to_invoice',
        )

        signals.pre_delete.connect(
            handlers.terminate_invoice_when_expert_request_deleted,
            sender=ExpertRequest,
            dispatch_uid='nodeconductor_assembly_waldur.experts.handlers.'
                         'terminate_invoice_when_expert_request_deleted',
        )

        signals.post_save.connect(
            handlers.log_expert_request_creation,
            sender=ExpertRequest,
            dispatch_uid='nodeconductor_assembly_waldur.experts.handlers.'
                         'log_expert_request_creation',
        )

        signals.post_save.connect(
            handlers.log_expert_request_state_changed,
            sender=ExpertRequest,
            dispatch_uid='nodeconductor_assembly_waldur.experts.handlers.'
                         'log_expert_request_state_changed',
        )

        signals.post_save.connect(
            handlers.log_expert_bid_creation,
            sender=ExpertBid,
            dispatch_uid='nodeconductor_assembly_waldur.experts.handlers.'
                         'log_expert_bid_creation',
        )

        signals.post_save.connect(
            handlers.notify_expert_providers_about_new_request,
            sender=ExpertRequest,
            dispatch_uid='nodeconductor_assembly_waldur.experts.handlers.'
                         'notify_expert_providers_about_new_request',
        )

        signals.post_save.connect(
            handlers.notify_customer_owners_about_new_bid,
            sender=ExpertBid,
            dispatch_uid='nodeconductor_assembly_waldur.experts.handlers.'
                         'notify_customer_owners_about_new_bid',
        )

        signals.post_save.connect(
            handlers.notify_customer_owners_about_new_contract,
            sender=ExpertContract,
            dispatch_uid='nodeconductor_assembly_waldur.experts.handlers.'
                         'notify_customer_owners_about_new_contract',
        )

        signals.post_save.connect(
            handlers.set_project_name_on_expert_request_creation,
            sender=ExpertRequest,
            dispatch_uid='nodeconductor_assembly_waldur.experts.handlers.'
                         'set_project_name_on_expert_request_creation',
        )

        signals.post_save.connect(
            handlers.update_expert_request_on_project_name_update,
            sender=structure_models.Project,
            dispatch_uid='nodeconductor_assembly_waldur.experts.handlers.'
                         'update_expert_request_on_project_name_update',
        )

        signals.post_save.connect(
            handlers.set_team_name_on_expert_contract_creation,
            sender=ExpertContract,
            dispatch_uid='nodeconductor_assembly_waldur.experts.handlers.'
                         'set_team_name_on_expert_contract_creation',
        )

        signals.post_save.connect(
            handlers.update_expert_contract_on_project_name_update,
            sender=structure_models.Project,
            dispatch_uid='nodeconductor_assembly_waldur.experts.handlers.'
                         'update_expert_contract_on_project_name_update',
        )
