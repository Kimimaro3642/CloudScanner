"""Tests for Key Vault security checks"""
import unittest
from unittest.mock import MagicMock
from scanner.src.checks.keyvault import check_keyvault_purge_protection


class TestKeyVaultChecks(unittest.TestCase):
    """Test cases for Key Vault checks"""

    def test_keyvault_purge_protection_disabled(self):
        """Test detection of disabled purge protection"""
        # Arrange
        mock_props = MagicMock()
        mock_props.enable_purge_protection = False

        mock_vault = MagicMock()
        mock_vault.name = "test-kv"
        mock_vault.properties = mock_props

        mock_kv = MagicMock()
        mock_kv.vaults.list_by_subscription.return_value = [mock_vault]

        # Act
        findings = check_keyvault_purge_protection(mock_kv)

        # Assert
        self.assertGreater(len(findings), 0)
        self.assertEqual(findings[0].rule, "KV_NO_PURGE_PROTECTION")

    def test_keyvault_purge_protection_enabled(self):
        """Test Key Vault with purge protection enabled"""
        mock_props = MagicMock()
        mock_props.enable_purge_protection = True

        mock_vault = MagicMock()
        mock_vault.name = "secure-kv"
        mock_vault.properties = mock_props

        mock_kv = MagicMock()
        mock_kv.vaults.list_by_subscription.return_value = [mock_vault]

        findings = check_keyvault_purge_protection(mock_kv)

        self.assertEqual(len(findings), 0)


if __name__ == '__main__':
    unittest.main()