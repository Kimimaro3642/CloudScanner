"""Tests for Storage Account security checks"""
import unittest
from unittest.mock import MagicMock
from scanner.src.checks.storage import check_storage_public


class TestStorageChecks(unittest.TestCase):
    """Test cases for Storage Account checks"""

    def test_storage_public_blob_access(self):
        """Test detection of public blob container access"""
        # Arrange
        mock_acct = MagicMock()
        mock_acct.id = "/subscriptions/sub1/resourceGroups/test-rg/providers/Microsoft.Storage/storageAccounts/teststorage"
        mock_acct.name = "teststorage"

        mock_props = MagicMock()
        mock_props.allow_blob_public_access = True

        mock_stg = MagicMock()
        mock_stg.storage_accounts.list.return_value = [mock_acct]
        mock_stg.storage_accounts.get_properties.return_value = mock_props

        # Act
        findings = check_storage_public(mock_stg)

        # Assert
        self.assertGreater(len(findings), 0)
        self.assertEqual(findings[0].rule, "STG_PUBLIC_BLOB")

    def test_storage_private_containers(self):
        """Test storage account with private containers"""
        mock_acct = MagicMock()
        mock_acct.id = "/subscriptions/sub1/resourceGroups/test-rg/providers/Microsoft.Storage/storageAccounts/securestorage"
        mock_acct.name = "securestorage"

        mock_props = MagicMock()
        mock_props.allow_blob_public_access = False

        mock_stg = MagicMock()
        mock_stg.storage_accounts.list.return_value = [mock_acct]
        mock_stg.storage_accounts.get_properties.return_value = mock_props

        findings = check_storage_public(mock_stg)

        self.assertEqual(len(findings), 0)


if __name__ == '__main__':
    unittest.main()