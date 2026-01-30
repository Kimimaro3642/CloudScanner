"""Pytest configuration and shared fixtures"""
import sys
import os
import pytest

# Add project root to Python path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))


@pytest.fixture
def mock_nsg():
    """Mock NSG resource"""
    return {
        'name': 'test-nsg',
        'id': '/subscriptions/sub1/resourceGroups/rg1/providers/Microsoft.Network/networkSecurityGroups/test-nsg',
        'security_rules': []
    }


@pytest.fixture
def mock_storage():
    """Mock Storage Account resource"""
    return {
        'name': 'teststorage',
        'id': '/subscriptions/sub1/resourceGroups/rg1/providers/Microsoft.Storage/storageAccounts/teststorage',
        'containers': []
    }


@pytest.fixture
def mock_keyvault():
    """Mock Key Vault resource"""
    return {
        'name': 'test-kv',
        'id': '/subscriptions/sub1/resourceGroups/rg1/providers/Microsoft.KeyVault/vaults/test-kv',
        'enable_purge_protection': True
    }