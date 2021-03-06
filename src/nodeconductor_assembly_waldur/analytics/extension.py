from __future__ import unicode_literals

from datetime import timedelta

from nodeconductor.core import NodeConductorExtension


class AnalyticsExtension(NodeConductorExtension):
    class Settings:
        # See also: http://influxdb-python.readthedocs.io/en/latest/api-documentation.html#influxdbclient
        WALDUR_ANALYTICS = {
            'ENABLED': False,
            'INFLUXDB': {
                'host': 'localhost',
                'port': 8086,
                'username': 'USERNAME',
                'password': 'PASSWORD',
                'database': 'DATABASE',
                'ssl': False,
                'verify_ssl': False,
            }
        }

    @staticmethod
    def django_app():
        return 'nodeconductor_assembly_waldur.analytics'

    @staticmethod
    def is_assembly():
        return True

    @staticmethod
    def celery_tasks():
        return {
            'waldur-push-analytics': {
                'task': 'analytics.push_points',
                'schedule': timedelta(minutes=30),
                'args': (),
            },
        }
