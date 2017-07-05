from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers

from nodeconductor.core import serializers as core_serializers
from nodeconductor.structure import permissions as structure_permissions

from . import models


class ExpertProviderSerializer(core_serializers.AugmentedSerializerMixin,
                               serializers.HyperlinkedModelSerializer):
    agree_with_policy = serializers.BooleanField(write_only=True, required=False)

    class Meta(object):
        model = models.ExpertProvider
        fields = ('url', 'uuid', 'created', 'customer', 'customer_name', 'agree_with_policy')
        read_only_fields = ('url', 'uuid', 'created')
        related_paths = {
            'customer': ('uuid', 'name', 'native_name', 'abbreviation')
        }
        protected_fields = ('customer',)
        extra_kwargs = {
            'url': {'lookup_field': 'uuid', 'view_name': 'expert-provider-detail'},
            'customer': {'lookup_field': 'uuid'},
        }

    def validate(self, attrs):
        agree_with_policy = attrs.pop('agree_with_policy', False)
        if not agree_with_policy:
            raise serializers.ValidationError(
                {'agree_with_policy': _('User must agree with policies to register organization.')})

        structure_permissions.is_owner(self.context['request'], None, attrs['customer'])
        return attrs


class ExpertRequestSerializer(serializers.HyperlinkedModelSerializer):
    class Meta(object):
        model = models.ExpertRequest
        fields = ('url', 'uuid', 'created', 'project')
        extra_kwargs = {
            'url': {'lookup_field': 'uuid', 'view_name': 'expert-request-detail'},
            'project': {'lookup_field': 'uuid'},
        }

    def validate_project(self, project):
        request = self.context['request']
        structure_permissions.is_owner(request, None, project.customer)
        if models.ExpertRequest.objects.filter(
            state=models.ExpertRequest.States.ACTIVE,
            project=project
        ).exists():
            raise serializers.ValidationError(_('Active expert request for current project already exists.'))
        return project
