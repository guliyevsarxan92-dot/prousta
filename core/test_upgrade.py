from django.db import connection
from django.db.migrations.executor import MigrationExecutor
from django.test import TransactionTestCase


class LegacyNumberUpgradeTests(TransactionTestCase):
    """Exercise the real historical schema, not a copy of migration logic."""
    def test_populated_legacy_schema_upgrades_without_duplicate_numbers(self):
        executor = MigrationExecutor(connection)
        leaves = executor.loader.graph.leaf_nodes()
        target = [('core', '0005_elan_bitis_tarixi_elan_nomre_alter_elan_status')]
        try:
            executor.migrate(target)
            state = executor.loader.project_state(target).apps
            user = state.get_model('auth', 'User').objects.create(username='legacy-upgrade')
            Ad = state.get_model('core', 'Elan')
            for _ in range(2):
                Ad.objects.create(istifadeci_id=user.pk, bashliq='Legacy', acaqlama='Legacy', nomre='')
            executor = MigrationExecutor(connection)
            executor.migrate(leaves)
            current = executor.loader.project_state(leaves).apps.get_model('core', 'Elan')
            numbers = list(current.objects.filter(istifadeci_id=user.pk).values_list('nomre', flat=True))
            self.assertEqual(len(numbers), 2)
            self.assertTrue(all(numbers))
            self.assertEqual(len(set(numbers)), 2)
        finally:
            MigrationExecutor(connection).migrate(leaves)
