import logging

from django.contrib.auth.models import Group
from django.core.management.base import BaseCommand

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Creating roles for users in a project'

    ROLES = (
        'Administrator',
        'Customer',
        'Anonymous User'
    )

    def handle(self, *args, **options):
        logger.info('Creating roles...')
        group_objects = (Group(name=role) for role in self.ROLES)
        Group.objects.bulk_create(group_objects)
        logger.info('Roles created.')
