from django.db.models import Sum
from django.utils.translation import ugettext_lazy as _

from rest_framework import serializers

from nodeconductor.core import serializers as core_serializers
from nodeconductor.core import signals as core_signals
from nodeconductor.structure import models as structure_models
from nodeconductor.structure import serializers as structure_serializers

from . import models


class PriceEstimateSerializer(serializers.HyperlinkedModelSerializer):
    scope = core_serializers.GenericRelatedField(
        related_models=models.PriceEstimate.get_estimated_models(),
        required=False
    )
    scope_name = serializers.ReadOnlyField(source='scope.name')
    scope_uuid = serializers.ReadOnlyField(source='scope.uuid')

    class Meta(object):
        model = models.PriceEstimate
        fields = ('url', 'uuid', 'scope', 'scope_name', 'scope_uuid',
                  'limit', 'total', 'threshold')
        read_only_fields = ('total', 'scope')
        extra_kwargs = {
            'url': {'lookup_field': 'uuid'},
        }

    def validate(self, attrs):
        if 'limit' in attrs:
            if isinstance(self.instance.scope, structure_models.Project):
                self._validate_project_limit(self.instance.scope, attrs['limit'])

            if isinstance(self.instance.scope, structure_models.Customer):
                self._validate_customer_limit(self.instance.scope, attrs['limit'])

        return attrs

    def _validate_project_limit(self, project, limit):
        customer = project.customer

        customer_limit = self._get_customer_limit(customer)
        if customer_limit == -1:
            return

        total_limit = self._get_total_limit(customer.projects.exclude(uuid=project.uuid)) + limit

        if total_limit > customer_limit:
            message = _('Total price limits of projects exceeds organization price limit. '
                        'Total limit: %(total_limit)s, organization limit: %(customer_limit)s')
            context = dict(total_limit=total_limit, customer_limit=customer_limit)
            raise serializers.ValidationError({'limit': message % context})

    def _validate_customer_limit(self, customer, limit):
        if limit == -1:
            return

        total_limit = self._get_total_limit(customer.projects.all())

        if limit < total_limit:
            message = _('Organization limit cannot be less than a sum of its projects limits: %d')
            raise serializers.ValidationError({'limit': message % total_limit})

    def _get_customer_limit(self, customer):
        try:
            estimate = models.PriceEstimate.objects.get(scope=customer)
            return estimate.limit
        except models.PriceEstimate.DoesNotExist:
            return -1

    def _get_total_limit(self, projects):
        if not projects.exists():
            return 0
        estimates = models.PriceEstimate.objects.filter(scope__in=projects).exclude(limit=-1)
        return estimates.aggregate(Sum('limit'))['limit__sum'] or 0


class NestedPriceEstimateSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.PriceEstimate
        fields = ('url', 'threshold', 'total', 'limit')
        extra_kwargs = {
            'url': {'lookup_field': 'uuid', 'view_name': 'billing-price-estimate-detail'},
        }


def get_price_estimate(serializer, scope):
    try:
        estimate = models.PriceEstimate.objects.get(scope=scope)
    except models.PriceEstimate.DoesNotExist:
        return {
            'threshold': 0.0,
            'total': 0.0,
            'limit': -1.0
        }
    else:
        serializer = NestedPriceEstimateSerializer(instance=estimate, context=serializer.context)
        return serializer.data


def add_price_estimate(sender, fields, **kwargs):
    fields['billing_price_estimate'] = serializers.SerializerMethodField()
    setattr(sender, 'get_billing_price_estimate', get_price_estimate)


core_signals.pre_serializer_fields.connect(
    sender=structure_serializers.ProjectSerializer,
    receiver=add_price_estimate,
)
core_signals.pre_serializer_fields.connect(
    sender=structure_serializers.CustomerSerializer,
    receiver=add_price_estimate,
)
