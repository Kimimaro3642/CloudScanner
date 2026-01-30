#!/usr/bin/env python3
"""
Test script to generate sample findings and create reports.
This demonstrates what the HTML and JSON reports look like.

USAGE:
    python test_reports.py

OUTPUT:
    - reports/test_run.html (formatted HTML report for browser viewing)
    - reports/test_run.json (structured JSON findings)

VIEW RESULTS:
    Windows: start reports/test_run.html
    macOS/Linux: open reports/test_run.html

DESCRIPTION:
This script is useful for:
- Testing the report generation without Azure credentials
- Seeing how findings are formatted in HTML and JSON
- Demonstrating the scanner's output format
- Development and documentation purposes
"""

import sys
import os

# Add scanner/src to path for relative imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'scanner', 'src'))

from scanner.src.core.model import Finding
from scanner.src.core.reporter import write_html, write_json
from scanner.src.core.cvss import cvss_for

# Create sample findings to demonstrate what reports look like
sample_findings = [
    Finding(
        id="AZ-NSG-WORLD-SSH",
        service="NSG",
        resource="prod-rg/prod-nsg/allow-ssh",
        rule="NSG_WORLD_SSH",
        description="Network Security Group allows world-accessible SSH (port 22)",
        severity="High",
        mitre="T1046",
        cvss_score=9.8,
        references=["https://docs.microsoft.com/azure/virtual-network/network-security-groups-overview"],
        metadata={"port": 22, "source": "0.0.0.0/0"}
    ),
    Finding(
        id="AZ-NSG-WORLD-RDP",
        service="NSG",
        resource="prod-rg/remote-nsg/allow-rdp",
        rule="NSG_WORLD_RDP",
        description="Network Security Group allows world-accessible RDP (port 3389)",
        severity="High",
        mitre="T1046",
        cvss_score=9.8,
        references=["https://docs.microsoft.com/azure/virtual-network/network-security-groups-overview"],
        metadata={"port": 3389, "source": "0.0.0.0/0"}
    ),
    Finding(
        id="AZ-STG-PUBLIC-BLOB",
        service="Storage",
        resource="prodstorageacct",
        rule="STG_PUBLIC_BLOB",
        description="Storage Account has public blob access enabled",
        severity="High",
        mitre="T1530",
        cvss_score=9.1,
        references=["https://docs.microsoft.com/azure/storage/blobs/anonymous-read-access-configure"],
        metadata={"account_type": "StorageV2"}
    ),
    Finding(
        id="AZ-KV-PURGE-PROTECTION-DISABLED",
        service="KeyVault",
        resource="prod-keyvault-001",
        rule="KV_NO_PURGE_PROTECTION",
        description="Key Vault does not have purge protection enabled",
        severity="Medium",
        mitre="T1211",
        cvss_score=6.5,
        references=["https://docs.microsoft.com/azure/key-vault/general/soft-delete-overview"],
        metadata={"location": "eastus"}
    ),
    Finding(
        id="AZ-NSG-WORLD-HTTP",
        service="NSG",
        resource="dev-rg/web-nsg/allow-http",
        rule="NSG_WORLD_HTTP",
        description="Network Security Group allows world-accessible HTTP (port 80)",
        severity="Medium",
        mitre="T1190",
        cvss_score=7.5,
        references=["https://docs.microsoft.com/azure/virtual-network/network-security-groups-overview"],
        metadata={"port": 80, "source": "0.0.0.0/0"}
    ),
]

if __name__ == "__main__":
    print(f"Generating test reports with {len(sample_findings)} sample findings...\n")
    
    # Write JSON report
    json_path = "reports/test_run.json"
    write_json(sample_findings, json_path)
    print(f"[CREATED] JSON report: {json_path}")
    
    # Write HTML report
    html_path = "reports/test_run.html"
    write_html("azure", sample_findings, html_path)
    print(f"[CREATED] HTML report: {html_path}")
    
    print(f"\nReports generated with {len(sample_findings)} findings:")
    for finding in sample_findings:
        print(f"  - {finding.id}: {finding.description} ({finding.severity})")
    
    print("\nView reports:")
    print(f"  JSON: Open {json_path} in VS Code or text editor")
    print(f"  HTML: Run 'start {html_path}' to open in browser")
