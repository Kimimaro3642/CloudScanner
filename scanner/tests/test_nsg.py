"""Tests for NSG security checks"""
import unittest
from unittest.mock import MagicMock
from scanner.src.checks.nsg import check_nsg_world_open


class TestNSGChecks(unittest.TestCase):
    """Test cases for Network Security Group checks"""

    def test_nsg_world_accessible_ssh(self):
        """Test detection of world-accessible SSH (port 22)"""
        # Arrange - Create rule with proper attributes
        mock_rule = MagicMock()
        mock_rule.access = "Allow"
        mock_rule.direction = "Inbound"
        mock_rule.source_address_prefix = "0.0.0.0/0"
        mock_rule.destination_port_range = "22"
        mock_rule.name = "AllowSSH"

        mock_nsg = MagicMock()
        mock_nsg.id = "/subscriptions/sub1/resourceGroups/test-rg/providers/Microsoft.Network/networkSecurityGroups/test-nsg"
        mock_nsg.name = "test-nsg"
        mock_nsg.security_rules = [mock_rule]
        mock_nsg.default_security_rules = []

        mock_net = MagicMock()
        mock_net.network_security_groups.list_all.return_value = [mock_nsg]

        # Act
        findings = check_nsg_world_open(mock_net)

        # Assert
        self.assertGreater(len(findings), 0)
        self.assertEqual(findings[0].rule, "NSG_WORLD_SSH")

    def test_nsg_no_vulnerabilities(self):
        """Test NSG with no security issues"""
        mock_nsg = MagicMock()
        mock_nsg.id = "/subscriptions/sub1/resourceGroups/test-rg/providers/Microsoft.Network/networkSecurityGroups/secure-nsg"
        mock_nsg.name = "secure-nsg"
        mock_nsg.security_rules = []
        mock_nsg.default_security_rules = []

        mock_net = MagicMock()
        mock_net.network_security_groups.list_all.return_value = [mock_nsg]

        findings = check_nsg_world_open(mock_net)

        self.assertEqual(len(findings), 0)


if __name__ == '__main__':
    unittest.main()