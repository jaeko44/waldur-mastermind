from django.apps import AppConfig
from django.db.models import signals


class BillingConfig(AppConfig):
    name = 'nodeconductor_assembly_waldur.billing'
    verbose_name = 'Billing'

    def ready(self):
        from nodeconductor_assembly_waldur.invoices import models as invoices_models

        from . import handlers, models

        for index, model in enumerate(models.PriceEstimate.get_estimated_models()):
            signals.post_save.connect(
                handlers.create_price_estimate,
                sender=model,
                dispatch_uid='nodeconductor_assembly_waldur.billing.'
                             'create_price_estimate_%s_%s' % (index, model.__class__),
            )

        for index, model in enumerate(models.PriceEstimate.get_estimated_models()):
            signals.pre_delete.connect(
                handlers.delete_stale_price_estimate,
                sender=model,
                dispatch_uid='nodeconductor_assembly_waldur.billing.'
                             'delete_stale_price_estimate_%s_%s' % (index, model.__class__),
            )

        for index, model in enumerate(invoices_models.InvoiceItem.get_all_models()):
            signals.post_save.connect(
                handlers.process_invoice_item,
                sender=model,
                dispatch_uid='nodeconductor_assembly_waldur.billing.'
                             'process_invoice_item_%s_%s' % (index, model.__class__),
            )

        signals.post_save.connect(
            handlers.log_price_estimate_limit_update,
            sender=models.PriceEstimate,
            dispatch_uid='nodeconductor_assembly_waldur.billing.log_price_estimate_limit_update',
        )
