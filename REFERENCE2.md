# CloudScanner - Comprehensive Reference Sheet

**Purpose:** Detailed line-by-line explanation of every file in the project with plain English context.

---

## **TABLE OF CONTENTS**

1. [Dependencies (requirements.txt)](#1-dependencies-requirementstxt)
2. [Entry Point (main.py)](#2-entry-point-mainpy)
3. [Orchestration (scan.py)](#3-orchestration-scanpy)
4. [Security Checks](#4-security-checks)
   - NSG Check
   - Storage Check
   - Key Vault Check
5. [Core Utilities](#5-core-utilities)
   - Model
   - Clients
   - CVSS
   - MITRE
   - Reporter
6. [Test Suite](#6-test-suite)
7. [Configuration Files](#7-configuration-files)
8. [CI/CD Workflows](#8-cicd-workflows)

---

# 1. DEPENDENCIES (requirements.txt)

## What This File Does
Lists every Python library the scanner needs. When you run `pip install -r requirements.txt`, it downloads and installs all these libraries.

## Line-by-Line Breakdown

### **Line 1: `azure-identity==1.17.1`**

**What:** Azure authentication library  
**Version:** 1.17.1 (pinned for consistency)  
**Purpose:** Proves to Azure that you are who you say you are

**Plain English:**
Imagine you're trying to access your bank account online. Before the bank shows you your money, you need to log in with your username and password. Azure works the same way. `azure-identity` handles that login process.

**In Code:**
```python
from azure.identity import ClientSecretCredential
credential = ClientSecretCredential(
    tenant_id="your-tenant-id",
    client_id="your-client-id", 
    client_secret="your-secret"
)
```

**What Happens:**
1. You provide three pieces of info: tenant ID, client ID, and secret
2. `azure-identity` sends them to Azure's login servers
3. If valid, Azure issues a temporary access token
4. That token lets you query Azure resources

---

### **Line 2: `azure-mgmt-resource==23.1.0`**

**What:** Azure Resource Management library  
**Purpose:** Interact with general Azure resources

**Plain English:**
This is like a toolkit for working with ANY Azure resource (not specific to one service). We have it installed but don't use it much yet. It's there if we need to list resource groups or other general operations.

**Status:** Installed but not heavily used currently

---

### **Line 3: `azure-mgmt-network==25.3.0`**

**What:** Azure Network Management library  
**Purpose:** Work with networking resources (NSGs, virtual networks, etc.)

**Plain English:**
This is the tool we use to talk to Azure about network security groups. When we ask "show me all the NSGs in my subscription," this library handles that conversation.

**In Code:**
```python
from azure.mgmt.network import NetworkManagementClient
client = NetworkManagementClient(credential, subscription_id)
for nsg in client.network_security_groups.list_all():
    # We have access to each NSG here
```

**What It Does:**
- Lists all NSGs
- Gets details about each NSG
- Reads security rules from each NSG

---

### **Line 4: `azure-mgmt-storage==21.2.1`**

**What:** Azure Storage Management library  
**Purpose:** Work with storage accounts (blobs, files, tables, queues)

**Plain English:**
This is the tool we use to ask Azure about storage accounts. When we ask "which storage accounts have public blob access enabled," this library makes that request.

**In Code:**
```python
from azure.mgmt.storage import StorageManagementClient
client = StorageManagementClient(credential, subscription_id)
for acct in client.storage_accounts.list():
    # We have access to each storage account here
```

**What It Does:**
- Lists all storage accounts
- Gets properties of each account
- Checks blob access settings

---

### **Line 5: `azure-mgmt-keyvault==10.3.0`**

**What:** Azure Key Vault Management library  
**Purpose:** Work with key vaults (where secrets, keys, certificates are stored)

**Plain English:**
Key vaults are like safes where you store passwords, API keys, and certificates. This library lets us ask Azure "which key vaults don't have purge protection enabled?"

**In Code:**
```python
from azure.mgmt.keyvault import KeyVaultManagementClient
client = KeyVaultManagementClient(credential, subscription_id)
for vault in client.vaults.list_by_subscription():
    # We have access to each key vault here
```

**What It Does:**
- Lists all key vaults
- Reads vault properties
- Checks if purge protection is enabled

---

### **Line 6: `jinja2==3.1.4`**

**What:** HTML template rendering engine  
**Purpose:** Take a template and fill in data to create HTML files

**Plain English:**
Imagine you have a letter template that says "Dear [NAME], you have [COUNT] findings." Jinja2 fills in [NAME] and [COUNT] with real data.

**Example:**
```python
template = "Report: {{findings_count}} issues found"
html = jinja2.Template(template).render(findings_count=42)
# Result: "Report: 42 issues found"
```

**In Code:**
```python
from jinja2 import Template
html = Template(HTML_TEMPLATE).render(findings=findings)
```

**What It Does:**
- Takes an HTML template with placeholders
- Fills in finding data
- Creates the final HTML report

---

### **Line 7: `cvss==3.1`**

**What:** CVSS (Common Vulnerability Scoring System) library  
**Purpose:** Calculate and score vulnerability severity

**Plain English:**
CVSS is an industry standard for rating how bad a vulnerability is (on a scale). For example, "world-accessible SSH" is worse than "optional security feature disabled."

**In Our Project:**
We're not using the full CVSS scoring yet. Instead, we have simple hardcoded mappings:
```python
RULE_SEVERITY = {
    "NSG_WORLD_SSH": "High",
    "NSG_WORLD_RDP": "High",
    "NSG_WORLD_HTTP": "Medium",
}
```

**Status:** Installed for future use, currently replaced by simple mappings

---

### **Line 8: `requests==2.32.3`**

**What:** HTTP library for making web requests  
**Purpose:** Send HTTP GET/POST/etc. requests to web services

**Plain English:**
When you type a URL in your browser, your browser makes an HTTP request to a server. `requests` is a Python library that does the same thing. The Azure libraries use it internally to talk to Azure's servers.

**Status:** Installed indirectly (Azure libraries depend on it)

---

## **DEPENDENCIES SUMMARY TABLE**

| Library | Purpose | Used Directly? | How |
|---------|---------|---|---|
| `azure-identity` | Authentication | ✅ YES | Creates credentials for Azure |
| `azure-mgmt-resource` | General resources | ❌ Not yet | Future use |
| `azure-mgmt-network` | NSG management | ✅ YES | Lists & reads NSGs |
| `azure-mgmt-storage` | Storage management | ✅ YES | Lists & reads storage accounts |
| `azure-mgmt-keyvault` | Key Vault management | ✅ YES | Lists & reads key vaults |
| `jinja2` | HTML templates | ✅ YES | Renders HTML reports |
| `cvss` | Severity scoring | ❌ Partially | Unused, replaced by mappings |
| `requests` | HTTP requests | ⚠️ Indirect | Used by Azure libraries |

---

# 2. ENTRY POINT (main.py)

## What This File Does
This is where everything starts. When you run `python scanner/src/main.py`, this file executes first.

## Line-by-Line Breakdown

```python
import argparse
```
**What:** Import the argument parsing library  
**Plain English:** This library lets us accept command-line arguments like `python main.py --out results.html`

---

```python
from .core import reporter
```
**What:** Import the reporter module  
**Plain English:** Load the code that generates HTML and JSON reports

---

```python
from .scan import run_azure
```
**What:** Import the run_azure function  
**Plain English:** Load the function that orchestrates all the security checks

---

```python
def main():
```
**What:** Define the main function  
**Plain English:** This is the main entry point—the first code that runs

---

```python
    ap=argparse.ArgumentParser()
```
**What:** Create an argument parser object  
**Plain English:** Set up a tool to parse command-line arguments

---

```python
    ap.add_argument("--out",default="reports/run.html")
```
**What:** Add an optional argument for output HTML file path  
**Plain English:** User can specify where to save the HTML report. If they don't specify, use `reports/run.html` as default

**Example Usage:**
```bash
python main.py --out my_report.html
# or just
python main.py
# (uses default)
```

---

```python
    ap.add_argument("--json",default="reports/run.json")
```
**What:** Add an optional argument for output JSON file path  
**Plain English:** User can specify where to save the JSON report. If they don't specify, use `reports/run.json` as default

---

```python
    a=ap.parse_args()
```
**What:** Parse the command-line arguments  
**Plain English:** Read what the user typed on the command line and store it in variable `a`

**Example:**
```bash
python main.py --out custom.html --json custom.json
# a.out = "custom.html"
# a.json = "custom.json"
```

---

```python
    f=run_azure()
```
**What:** Call the run_azure function  
**Plain English:** Execute all the security checks (NSG, Storage, KeyVault) and get back a list of findings

**What Happens:**
1. Load Azure credentials from environment variables
2. Connect to Azure
3. Run all three checks
4. Return list of Finding objects

**Result:** `f` contains all the vulnerabilities found

---

```python
    reporter.write_json(f,a.json)
```
**What:** Write findings to JSON file  
**Plain English:** Take the findings and save them as JSON to the path the user specified (or default)

**File Example:**
```json
[
  {
    "id": "AZ-NSG-WORLD-SSH",
    "service": "NSG",
    "resource": "my-nsg",
    "rule": "NSG_WORLD_SSH",
    "description": "World access to 22",
    "severity": "High",
    "mitre": "T1046"
  }
]
```

---

```python
    reporter.write_html("azure",f,a.out)
```
**What:** Write findings to HTML file  
**Plain English:** Take the findings and save them as a pretty HTML report to the path the user specified (or default)

**Parameters:**
- `"azure"` - Cloud provider name (future: could be "gcp", "aws")
- `f` - List of findings
- `a.out` - Output file path

---

```python
    print("Done, findings:",len(f))
```
**What:** Print summary to console  
**Plain English:** Tell the user how many vulnerabilities were found

**Output Example:**
```
Done, findings: 5
```

---

```python
if __name__=="__main__": main()
```
**What:** Run main() only if this file is executed directly  
**Plain English:** This code only runs if someone types `python main.py`. It doesn't run if someone imports this file in another script.

---

## **main.py FLOW DIAGRAM**

```
User runs: python main.py --out results.html
    ↓
main() function starts
    ↓
Parse command-line arguments
    ↓
Call run_azure() to get findings
    ↓
Write JSON report
    ↓
Write HTML report
    ↓
Print "Done, findings: X"
    ↓
End
```

---

# 3. ORCHESTRATION (scan.py)

## What This File Does
Coordinates all the security checks. It's the "conductor" that tells each check to run.

## Line-by-Line Breakdown

```python
import os
```
**What:** Import the os module  
**Plain English:** This lets us read environment variables (like your Azure credentials)

---

```python
from .core.clients import AzureClients
```
**What:** Import the Azure clients class  
**Plain English:** Load the tool that connects to Azure

---

```python
from .checks.nsg import check_nsg_world_open
from .checks.storage import check_storage_public
from .checks.keyvault import check_keyvault_purge_protection
```
**What:** Import all three security check functions  
**Plain English:** Load the three different security checks

---

```python
def run_azure():
```
**What:** Define the main orchestration function  
**Plain English:** This function runs all the checks and returns all findings

---

```python
    sub=os.getenv("AZURE_SUBSCRIPTION_ID")
    ten=os.getenv("AZURE_TENANT_ID")
    cid=os.getenv("AZURE_CLIENT_ID")
    sec=os.getenv("AZURE_CLIENT_SECRET")
```
**What:** Read environment variables  
**Plain English:** Load your Azure credentials from the system environment

**Where They Come From:**
- `.env` file (for local development)
- GitHub Secrets (for CI/CD)
- Environment variables (for Docker containers)

**Example:**
```
AZURE_SUBSCRIPTION_ID=abc123
AZURE_TENANT_ID=def456
AZURE_CLIENT_ID=ghi789
AZURE_CLIENT_SECRET=jkl012
```

---

```python
    c=AzureClients(sub,ten,cid,sec)
```
**What:** Create Azure clients object  
**Plain English:** Use the credentials to connect to Azure. `c` is now your connection to Azure.

**What `c` Contains:**
- `c.network` - Connection to network service
- `c.storage` - Connection to storage service
- `c.keyvault` - Connection to key vault service

---

```python
    f=[]
```
**What:** Initialize empty findings list  
**Plain English:** Create an empty list where we'll store all the vulnerabilities we find

---

```python
    f+=check_nsg_world_open(c.network)
```
**What:** Run NSG check and add findings to list  
**Plain English:** Ask the NSG check function to look for world-accessible ports. Whatever it finds, add to our list.

**What Happens:**
1. `check_nsg_world_open()` connects to Azure via `c.network`
2. It lists all NSGs
3. It looks for world-accessible ports
4. It returns a list of Finding objects
5. `f+=` adds those findings to our main list

---

```python
    f+=check_storage_public(c.storage)
```
**What:** Run storage check and add findings to list  
**Plain English:** Ask the storage check function to look for public blobs. Whatever it finds, add to our list.

---

```python
    f+=check_keyvault_purge_protection(c.keyvault)
```
**What:** Run key vault check and add findings to list  
**Plain English:** Ask the key vault check function to look for disabled purge protection. Whatever it finds, add to our list.

---

```python
    return f
```
**What:** Return all findings  
**Plain English:** Send back the complete list of all vulnerabilities found to whoever called this function (main.py)

---

## **scan.py FLOW DIAGRAM**

```
run_azure() is called
    ↓
Load Azure credentials from environment
    ↓
Create AzureClients connection
    ↓
Initialize empty findings list
    ↓
Run check_nsg_world_open() → add findings
    ↓
Run check_storage_public() → add findings
    ↓
Run check_keyvault_purge_protection() → add findings
    ↓
Return all findings
```

---

# 4. SECURITY CHECKS

## What These Files Do
Each file contains a function that checks for a specific security vulnerability in Azure.

---

## 4.1 NSG CHECK (nsg.py)

### What It Does
Finds Network Security Groups with world-accessible ports (SSH, RDP, HTTP).

### Line-by-Line Breakdown

```python
from ..core.model import Finding
from ..core.cvss import severity_for
from ..core.mitre import mitre_for
```
**What:** Import supporting modules  
**Plain English:** Load:
- Finding class (data structure for vulnerabilities)
- severity_for function (maps rule to severity level)
- mitre_for function (maps rule to MITRE technique)

---

```python
def check_nsg_world_open(net):
```
**What:** Define the NSG check function  
**Parameters:**
- `net` - Azure Network Management Client

**Plain English:** This function takes an Azure network client and finds world-accessible NSG rules.

---

```python
    findings=[]
```
**What:** Initialize empty findings list  
**Plain English:** Create a list to store all vulnerabilities we find

---

```python
    for nsg in net.network_security_groups.list_all():
```
**What:** Loop through every NSG in the subscription  
**Plain English:** Get a list of all NSGs from Azure, then process each one

---

```python
        rg = nsg.id.split("/resourceGroups/")[1].split("/")[0]
```
**What:** Extract resource group name from NSG ID  
**Plain English:** Azure IDs are long paths like `/subscriptions/xxx/resourceGroups/my-rg/providers/...`. We extract `my-rg` to know which resource group owns this NSG.

**Example:**
```
Input:  /subscriptions/sub1/resourceGroups/my-rg/providers/.../test-nsg
Output: my-rg
```

---

```python
        rules = (nsg.security_rules or []) + (nsg.default_security_rules or [])
```
**What:** Get all security rules (custom + default)  
**Plain English:** NSGs have two types of rules:
- Custom rules (you added)
- Default rules (built into Azure)

We check both.

---

```python
        for r in rules:
```
**What:** Loop through each rule  
**Plain English:** Process each security rule one by one

---

```python
            if getattr(r,"access","")!="Allow": continue
```
**What:** Skip if rule doesn't allow access  
**Plain English:** We only care about rules that allow traffic. If it denies, skip it.

**Logic:**
- `getattr(r, "access", "")` - Get the "access" property. If it doesn't exist, use empty string
- `!="Allow"` - If it's not "Allow", skip this rule

---

```python
            if getattr(r,"direction","")!="Inbound": continue
```
**What:** Skip if rule is for outbound traffic  
**Plain English:** We only care about inbound rules (traffic coming in from outside). Outbound rules (traffic going out) don't expose your resources.

---

```python
            src=getattr(r,"source_address_prefix","")
            if src=="0.0.0.0/0":
```
**What:** Check if source is the entire world  
**Plain English:** 
- `0.0.0.0/0` means "any IP address in the world"
- If a rule allows inbound access from `0.0.0.0/0`, anyone on the internet can reach it
- That's bad for sensitive ports like SSH and RDP

---

```python
                port=str(getattr(r,"destination_port_range",""))
                if port=="22":
                    code="NSG_WORLD_SSH"
                elif port=="3389":
                    code="NSG_WORLD_RDP"
                else:
                    code="NSG_WORLD_HTTP"
```
**What:** Determine which port is exposed  
**Plain English:** 
- Port 22 = SSH (remote command execution)
- Port 3389 = RDP (remote desktop)
- Other ports = HTTP/web service
- Each gets its own rule code

---

```python
                findings.append(Finding(
                    id=f"AZ-NSG-{code}",
                    service="NSG",
                    resource=f"{rg}/{nsg.name}/{r.name}",
                    rule=code,
                    description=f"World access to {port}",
                    severity=severity_for(code),
                    mitre=mitre_for(code)
                ))
```
**What:** Create a Finding object and add to list  
**Plain English:** Record the vulnerability with all details:
- `id` - Unique identifier
- `service` - Which Azure service (NSG, Storage, etc.)
- `resource` - Which specific resource (nsg-name/rule-name)
- `rule` - Rule code (NSG_WORLD_SSH, etc.)
- `description` - Human-readable description
- `severity` - How bad is it (High, Medium, Low)
- `mitre` - MITRE ATT&CK technique

---

```python
    return findings
```
**What:** Return all findings  
**Plain English:** Send back the list of world-accessible NSG rules found

---

### **NSG Check Flow**

```
For each NSG in subscription:
    ├─ Get all security rules
    ├─ For each rule:
    │  ├─ Skip if doesn't allow traffic
    │  ├─ Skip if not inbound
    │  ├─ Check if source is world-open (0.0.0.0/0)
    │  └─ If world-open:
    │     ├─ Determine port (SSH, RDP, etc.)
    │     └─ Create Finding object
    └─ Return all findings
```

---

## 4.2 STORAGE CHECK (storage.py)

### What It Does
Finds Storage Accounts with public blob container access enabled.

### Line-by-Line Breakdown

```python
from ..core.model import Finding
from ..core.cvss import severity_for
from ..core.mitre import mitre_for
```
**What:** Import supporting modules (same as NSG check)

---

```python
def check_storage_public(stg):
```
**What:** Define the storage check function  
**Parameters:**
- `stg` - Azure Storage Management Client

---

```python
    findings=[]
```
**What:** Initialize empty findings list

---

```python
    for acct in stg.storage_accounts.list():
```
**What:** Loop through every storage account in subscription  
**Plain English:** Get a list of all storage accounts from Azure, then process each one

---

```python
        rg = acct.id.split("/resourceGroups/")[1].split("/")[0]
```
**What:** Extract resource group name (same as NSG check)

---

```python
        props=stg.storage_accounts.get_properties(rg,acct.name)
```
**What:** Get detailed properties of the storage account  
**Plain English:** Fetch the account's full configuration from Azure

---

```python
        if getattr(props,"allow_blob_public_access",None):
```
**What:** Check if public blob access is allowed  
**Plain English:** 
- `allow_blob_public_access` is a property that says "is public blob access enabled?"
- `if getattr(..., None)` - Get this property. If it doesn't exist, use None
- If True, public access is enabled (bad)
- If False or None, public access is disabled (good)

---

```python
            findings.append(Finding(
                id="AZ-STG-PUBLIC-BLOB",
                service="Storage",
                resource=acct.name,
                rule="STG_PUBLIC_BLOB",
                description="Public blob access enabled",
                severity=severity_for("STG_PUBLIC_BLOB"),
                mitre=mitre_for("STG_PUBLIC_BLOB")
            ))
```
**What:** Create a Finding object  
**Plain English:** Record that this storage account has public blob access enabled

---

```python
    return findings
```
**What:** Return all findings

---

### **Storage Check Flow**

```
For each Storage Account in subscription:
    ├─ Get account properties
    ├─ Check if allow_blob_public_access is enabled
    └─ If enabled:
       └─ Create Finding object
Return all findings
```

---

## 4.3 KEY VAULT CHECK (keyvault.py)

### What It Does
Finds Key Vaults without purge protection enabled.

### Line-by-Line Breakdown

```python
from ..core.model import Finding
from ..core.cvss import severity_for
from ..core.mitre import mitre_for
```
**What:** Import supporting modules

---

```python
def check_keyvault_purge_protection(kv):
```
**What:** Define the key vault check function  
**Parameters:**
- `kv` - Azure Key Vault Management Client

---

```python
    findings=[]
```
**What:** Initialize empty findings list

---

```python
    for v in kv.vaults.list_by_subscription():
```
**What:** Loop through every key vault in subscription

---

```python
        enabled=getattr(getattr(v,"properties",None),"enable_purge_protection",None)
```
**What:** Get the purge protection setting  
**Plain English:**
- `getattr(v, "properties", None)` - Get vault properties
- `getattr(..., "enable_purge_protection", None)` - Get purge protection setting

**Why Nested?** Some vaults might not have a properties object, so we check for None first.

---

```python
        if not enabled:
```
**What:** Check if purge protection is NOT enabled  
**Plain English:** If purge protection is disabled, that's a vulnerability

---

```python
            findings.append(Finding(
                id="AZ-KV-PURGE-PROTECTION-DISABLED",
                service="KeyVault",
                resource=v.name,
                rule="KV_NO_PURGE_PROTECTION",
                description="Purge protection disabled",
                severity=severity_for("KV_NO_PURGE_PROTECTION"),
                mitre=mitre_for("KV_NO_PURGE_PROTECTION")
            ))
```
**What:** Create a Finding object  
**Plain English:** Record that this key vault doesn't have purge protection

---

```python
    return findings
```
**What:** Return all findings

---

### **Key Vault Check Flow**

```
For each Key Vault in subscription:
    ├─ Get purge protection setting
    └─ If NOT enabled:
       └─ Create Finding object
Return all findings
```

---

# 5. CORE UTILITIES

## What These Files Do
Supporting functions and classes used by the checks and main code.

---

## 5.1 MODEL (model.py)

### What It Does
Defines the `Finding` data structure (class).

### Code Breakdown

```python
from dataclasses import dataclass, field
from typing import Dict, List
```
**What:** Import tools for creating a data class  
**Plain English:**
- `dataclass` - A decorator that automatically creates a class with fields
- `field` - For setting default values
- `Dict`, `List` - Type hints

---

```python
@dataclass
class Finding:
```
**What:** Define a data class called Finding  
**Plain English:** This is a template for storing information about a vulnerability

---

```python
    id: str
```
**What:** Unique identifier field  
**Example:** `"AZ-NSG-WORLD-SSH"`

---

```python
    service: str
```
**What:** Which Azure service  
**Example:** `"NSG"`, `"Storage"`, `"KeyVault"`

---

```python
    resource: str
```
**What:** Which specific resource  
**Example:** `"my-rg/my-nsg/allow-ssh"`

---

```python
    rule: str
```
**What:** Rule code  
**Example:** `"NSG_WORLD_SSH"`

---

```python
    description: str
```
**What:** Human-readable description  
**Example:** `"World access to 22"`

---

```python
    severity: str
```
**What:** How bad is this vulnerability  
**Example:** `"High"`, `"Medium"`, `"Low"`

---

```python
    mitre: str
```
**What:** MITRE ATT&CK technique  
**Example:** `"T1046"` (Network Service Scanning)

---

```python
    references: List[str] = field(default_factory=list)
```
**What:** Optional list of documentation links  
**Default:** Empty list if not provided

---

```python
    metadata: Dict = field(default_factory=dict)
```
**What:** Optional additional data  
**Default:** Empty dict if not provided

---

### **Finding Class Example**

```python
finding = Finding(
    id="AZ-NSG-WORLD-SSH",
    service="NSG",
    resource="my-rg/my-nsg/allow-ssh",
    rule="NSG_WORLD_SSH",
    description="World access to port 22",
    severity="High",
    mitre="T1046",
    references=["https://docs.azure.com/..."],
    metadata={"port": 22}
)
```

---

## 5.2 CLIENTS (clients.py)

### What It Does
Wraps Azure SDK clients with lazy loading and credential handling.

### Code Breakdown

```python
from azure.identity import ClientSecretCredential
from azure.mgmt.network import NetworkManagementClient
from azure.mgmt.storage import StorageManagementClient
from azure.mgmt.keyvault import KeyVaultManagementClient
```
**What:** Import Azure client libraries  
**Plain English:** Load the tools for connecting to each Azure service

---

```python
class AzureClients:
```
**What:** Define a class that holds all Azure clients  
**Plain English:** A container for all our Azure connections

---

```python
    def __init__(self, subscription_id, tenant_id, client_id, client_secret):
```
**What:** Constructor (initialization method)  
**Parameters:**
- `subscription_id` - Your Azure subscription
- `tenant_id` - Your Azure tenant
- `client_id` - Service principal client ID
- `client_secret` - Service principal secret

---

```python
        self.subscription_id = subscription_id
```
**What:** Store subscription ID  
**Plain English:** Save it for later use

---

```python
        self.credential = ClientSecretCredential(
            tenant_id=tenant_id, 
            client_id=client_id, 
            client_secret=client_secret
        )
```
**What:** Create authentication credential object  
**Plain English:** Use the provided credentials to create an Azure credential object. This proves to Azure that we're authorized.

---

```python
        self._net=None; self._stg=None; self._kv=None
```
**What:** Initialize client placeholders  
**Plain English:** Set up three variables (one for each service) and set them to None initially. We'll create the actual clients when needed.

---

```python
    @property
    def network(self):
        if not self._net:
            self._net = NetworkManagementClient(self.credential, self.subscription_id)
        return self._net
```
**What:** Lazy-load network client  
**Plain English:**
- When someone accesses `.network`, this runs
- If we haven't created the network client yet (`if not self._net`), create it now
- Return the network client

**Why Lazy?** We only connect to a service when it's actually needed, saving time and resources.

---

```python
    @property
    def storage(self):
        if not self._stg:
            self._stg = StorageManagementClient(self.credential, self.subscription_id)
        return self._stg
```
**What:** Lazy-load storage client (same pattern as network)

---

```python
    @property
    def keyvault(self):
        if not self._kv:
            self._kv = KeyVaultManagementClient(self.credential, self.subscription_id)
        return self._kv
```
**What:** Lazy-load key vault client (same pattern as network)

---

### **How It's Used**

```python
# Create clients
clients = AzureClients(sub_id, tenant_id, client_id, secret)

# Use network client (this is when it's actually created)
nsgs = clients.network.network_security_groups.list_all()

# Use storage client
accounts = clients.storage.storage_accounts.list()

# Use key vault client
vaults = clients.keyvault.vaults.list_by_subscription()
```

---

## 5.3 CVSS (cvss.py)

### What It Does
Maps rule codes to severity levels.

### Code Breakdown

```python
RULE_SEVERITY = {
    "NSG_WORLD_SSH": "High",
    "NSG_WORLD_RDP": "High",
    "NSG_WORLD_HTTP": "Medium",
    "STG_PUBLIC_BLOB": "High",
    "KV_NO_PURGE_PROTECTION": "Medium",
}
```
**What:** Dictionary mapping rule codes to severity  
**Plain English:** A simple lookup table that says "NSG_WORLD_SSH is High severity, STG_PUBLIC_BLOB is High severity," etc.

---

```python
def severity_for(rule: str) -> str:
    return RULE_SEVERITY.get(rule, "Low")
```
**What:** Function to look up severity for a rule  
**Plain English:**
- Takes a rule code (e.g., "NSG_WORLD_SSH")
- Looks it up in the dictionary
- Returns the severity (e.g., "High")
- If rule doesn't exist, returns "Low" as default

**Example:**
```python
severity_for("NSG_WORLD_SSH")  # Returns "High"
severity_for("UNKNOWN_RULE")    # Returns "Low"
```

---

## 5.4 MITRE (mitre.py)

### What It Does
Maps rule codes to MITRE ATT&CK techniques.

### Code Breakdown

```python
RULE_MITRE = {
    "NSG_WORLD_SSH": "T1046",
    "NSG_WORLD_RDP": "T1046",
    "NSG_WORLD_HTTP": "T1190",
    "STG_PUBLIC_BLOB": "T1530",
    "KV_NO_PURGE_PROTECTION": "T1211",
}
```
**What:** Dictionary mapping rule codes to MITRE techniques  
**Plain English:** MITRE ATT&CK is an industry framework for categorizing attack techniques. This maps our rules to them.

**Examples:**
- T1046 = Network Service Scanning (NSG world-open)
- T1190 = Exploit Public-Facing Application (HTTP exposed)
- T1530 = Data from Cloud Storage (public blobs)

---

```python
def mitre_for(rule: str) -> str:
    return RULE_MITRE.get(rule, "-")
```
**What:** Function to look up MITRE technique for a rule  
**Plain English:**
- Takes a rule code
- Looks it up in the dictionary
- Returns the MITRE technique
- If rule doesn't exist, returns "-" (unknown)

---

## 5.5 REPORTER (reporter.py)

### What It Does
Generates HTML and JSON reports from findings.

### Code Breakdown

```python
import os, json
from jinja2 import Template
from datetime import datetime
```
**What:** Import required libraries

---

```python
HTML_TEMPLATE = "<html><body><h1>Cloud Report</h1>{% for f in findings %}<p>{{f.id}} - {{f.description}} ({{f.severity}})</p>{% endfor %}</body></html>"
```
**What:** HTML template with placeholders  
**Plain English:**
- `{% for f in findings %}` - Loop through findings
- `{{f.id}}` - Insert finding ID
- `{{f.description}}` - Insert description
- `{{f.severity}}` - Insert severity

**Example Output:**
```html
<html>
<body>
<h1>Cloud Report</h1>
<p>AZ-NSG-WORLD-SSH - World access to 22 (High)</p>
<p>AZ-STG-PUBLIC-BLOB - Public blob access enabled (High)</p>
</body>
</html>
```

---

```python
def write_html(provider, findings, out_path):
```
**What:** Function to write HTML report  
**Parameters:**
- `provider` - Cloud provider ("azure", "gcp", "aws")
- `findings` - List of Finding objects
- `out_path` - Where to save the file

---

```python
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
```
**What:** Create directory if it doesn't exist  
**Plain English:** If the directory `reports/` doesn't exist, create it

---

```python
    from jinja2 import Template
```
**What:** Import Jinja2 Template (redundant, already imported at top)

---

```python
    html = Template(HTML_TEMPLATE).render(findings=findings)
```
**What:** Render template with findings data  
**Plain English:**
- Take the HTML template
- Replace `{% for f in findings %}` with actual findings
- Replace `{{f.id}}` with actual finding IDs, etc.
- Return final HTML string

---

```python
    with open(out_path, "w") as f:
        f.write(html)
```
**What:** Write HTML to file  
**Plain English:** Save the rendered HTML to the specified file path

---

```python
def write_json(findings, out_path):
```
**What:** Function to write JSON report

---

```python
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
```
**What:** Create directory if it doesn't exist

---

```python
    with open(out_path, "w") as f:
        json.dump([f.__dict__ for f in findings], f, indent=2)
```
**What:** Write findings as JSON  
**Plain English:**
- `[f.__dict__ for f in findings]` - Convert each Finding object to a dictionary
- `json.dump(..., f, indent=2)` - Write to file with nice formatting (indent=2)

**Output Example:**
```json
[
  {
    "id": "AZ-NSG-WORLD-SSH",
    "service": "NSG",
    "resource": "my-rg/my-nsg/allow-ssh",
    "rule": "NSG_WORLD_SSH",
    "description": "World access to 22",
    "severity": "High",
    "mitre": "T1046",
    "references": [],
    "metadata": {}
  }
]
```

---

# 6. TEST SUITE

## What These Files Do
Automated tests that verify the security checks work correctly.

---

## 6.1 CONFTEST (conftest.py)

### What It Does
Provides shared test fixtures (mock objects) for all tests.

### Code Breakdown

```python
"""Pytest configuration and shared fixtures"""
import pytest
```
**What:** Import pytest

---

```python
@pytest.fixture
def mock_nsg():
    """Mock NSG resource"""
    return {
        'name': 'test-nsg',
        'id': '/subscriptions/sub1/resourceGroups/rg1/providers/Microsoft.Network/networkSecurityGroups/test-nsg',
        'security_rules': []
    }
```
**What:** Create a reusable mock NSG  
**Plain English:**
- `@pytest.fixture` - This is a fixture (reusable test object)
- Returns a mock NSG dictionary
- Any test can request this fixture by adding `mock_nsg` parameter

**Usage:**
```python
def test_example(self, mock_nsg):
    # mock_nsg is available here
```

---

```python
@pytest.fixture
def mock_storage():
    """Mock Storage Account resource"""
    return {
        'name': 'teststorage',
        'id': '/subscriptions/sub1/resourceGroups/rg1/providers/Microsoft.Storage/storageAccounts/teststorage',
        'containers': []
    }
```
**What:** Create a reusable mock Storage Account

---

```python
@pytest.fixture
def mock_keyvault():
    """Mock Key Vault resource"""
    return {
        'name': 'test-kv',
        'id': '/subscriptions/sub1/resourceGroups/rg1/providers/Microsoft.KeyVault/vaults/test-kv',
        'enable_purge_protection': True
    }
```
**What:** Create a reusable mock Key Vault

---

## 6.2 NSG TESTS (test_nsg.py)

### What It Does
Test the NSG security check function.

### Code Breakdown

```python
"""Tests for NSG security checks"""
import unittest
from unittest.mock import MagicMock
from scanner.src.checks.nsg import check_nsg_world_open
```
**What:** Import test framework and the function we're testing

---

```python
class TestNSGChecks(unittest.TestCase):
    """Test cases for Network Security Group checks"""
```
**What:** Define a test class  
**Plain English:** A container for related tests

---

### **Test 1: `test_nsg_world_accessible_ssh`**

```python
    def test_nsg_world_accessible_ssh(self):
        """Test detection of world-accessible SSH (port 22)"""
```
**What:** Define a test  
**Plain English:** This test checks if we correctly detect world-accessible SSH

---

```python
        # Arrange - Create rule with proper attributes
        mock_rule = MagicMock()
        mock_rule.access = "Allow"
        mock_rule.direction = "Inbound"
        mock_rule.source_address_prefix = "0.0.0.0/0"
        mock_rule.destination_port_range = "22"
        mock_rule.name = "AllowSSH"
```
**What:** Set up the test data  
**Plain English:** Create a fake security rule that allows world-accessible SSH

**This Mimics:** A vulnerable NSG rule

---

```python
        mock_nsg = MagicMock()
        mock_nsg.id = "/subscriptions/sub1/resourceGroups/test-rg/providers/Microsoft.Network/networkSecurityGroups/test-nsg"
        mock_nsg.name = "test-nsg"
        mock_nsg.security_rules = [mock_rule]
        mock_nsg.default_security_rules = []
```
**What:** Create a fake NSG containing our fake rule  
**Plain English:** Create a mock NSG that has the vulnerable rule we created above

---

```python
        mock_net = MagicMock()
        mock_net.network_security_groups.list_all.return_value = [mock_nsg]
```
**What:** Create a fake network client  
**Plain English:**
- `mock_net` is a fake Azure network client
- When someone calls `mock_net.network_security_groups.list_all()`, return our fake NSG

---

```python
        # Act
        findings = check_nsg_world_open(mock_net)
```
**What:** Run the check function  
**Plain English:** Call the function we're testing, passing our fake network client

---

```python
        # Assert
        self.assertGreater(len(findings), 0)
        self.assertEqual(findings[0].rule, "NSG_WORLD_SSH")
```
**What:** Verify the results  
**Plain English:**
- `assertGreater(len(findings), 0)` - We should find at least one vulnerability
- `assertEqual(findings[0].rule, "NSG_WORLD_SSH")` - The finding should be NSG_WORLD_SSH

**If This Passes:** The check correctly identified world-accessible SSH

---

### **Test 2: `test_nsg_no_vulnerabilities`**

```python
    def test_nsg_no_vulnerabilities(self):
        """Test NSG with no security issues"""
```
**What:** Test that we don't report false positives

---

```python
        mock_nsg = MagicMock()
        mock_nsg.id = "..."
        mock_nsg.name = "secure-nsg"
        mock_nsg.security_rules = []
        mock_nsg.default_security_rules = []
```
**What:** Create a secure NSG (no rules)  
**Plain English:** Create a fake NSG with no security rules (nothing vulnerable)

---

```python
        mock_net = MagicMock()
        mock_net.network_security_groups.list_all.return_value = [mock_nsg]

        findings = check_nsg_world_open(mock_net)

        self.assertEqual(len(findings), 0)
```
**What:** Verify no findings are reported  
**Plain English:**
- Run the check
- Assert that we find zero vulnerabilities

**If This Passes:** The check correctly identifies that a secure NSG has no issues

---

## 6.3 STORAGE TESTS (test_storage.py)

### Similar to NSG tests but for storage accounts

```python
def test_storage_public_blob_access(self):
```
**What:** Test detection of public blob access

---

```python
        mock_props = MagicMock()
        mock_props.allow_blob_public_access = True
```
**What:** Create mock properties with public access enabled

---

```python
        mock_stg = MagicMock()
        mock_stg.storage_accounts.list.return_value = [mock_acct]
        mock_stg.storage_accounts.get_properties.return_value = mock_props
```
**What:** Create mock storage client  
**Plain English:** Fake the storage client to return our vulnerable account

---

```python
def test_storage_private_containers(self):
```
**What:** Test that we don't flag private storage accounts

---

## 6.4 KEY VAULT TESTS (test_keyvault.py)

### Similar pattern to the others

```python
def test_keyvault_purge_protection_disabled(self):
```
**What:** Test detection of disabled purge protection

---

```python
def test_keyvault_purge_protection_enabled(self):
```
**What:** Test that we don't flag protected key vaults

---

# 7. CONFIGURATION FILES

## What These Files Do
Configure the project behavior and build process.

---

## 7.1 pyproject.toml

### Sections

**[build-system]**
```toml
requires = ["setuptools>=65.0"]
build-backend = "setuptools.build_meta"
```
**What:** How to build the project  
**Plain English:** Use setuptools to build and install the package

---

**[project]**
```toml
name = "azure-security-scanner"
version = "1.0.0"
description = "Azure cloud security scanner for vulnerability detection"
requires-python = ">=3.9"
```
**What:** Project metadata  
**Plain English:** Name, version, description, minimum Python version

---

**[tool.pytest.ini_options]**
```toml
testpaths = ["scanner/tests"]
addopts = "--cov=scanner/src --cov-report=html --cov-report=term-missing"
python_files = "test_*.py"
```
**What:** Pytest configuration  
**Plain English:**
- Look for tests in `scanner/tests/`
- Generate HTML coverage report
- Print missing coverage in terminal
- Only run files starting with `test_`

---

**[tool.coverage.run]**
```toml
source = ["scanner/src"]
```
**What:** Which code to measure coverage for

---

**[tool.mypy]**
```toml
python_version = "3.9"
ignore_missing_imports = true
```
**What:** Type checking configuration  
**Plain English:** Use Python 3.9 for type checking. Ignore missing type hints in third-party libraries

---

## 7.2 .gitignore

```
.venv/
venv/
```
**What:** Ignore virtual environment  
**Plain English:** Don't commit the venv folder (it's large and regenerable)

---

```
.env
.env.local
```
**What:** Ignore environment files  
**Plain English:** Don't commit `.env` (contains secrets)

---

```
.pytest_cache/
.coverage
htmlcov/
```
**What:** Ignore test artifacts  
**Plain English:** Don't commit test cache and coverage reports (regenerable)

---

```
reports/
```
**What:** Ignore scan reports  
**Plain English:** Don't commit generated reports

---

## 7.3 .flake8

```ini
[flake8]
max-line-length = 100
```
**What:** Maximum line length for code  
**Plain English:** Lines shouldn't be longer than 100 characters

---

```ini
ignore = E203,W503
```
**What:** Ignore specific style warnings  
**Plain English:** E203 and W503 are false positives, so we ignore them

---

```ini
per-file-ignores =
    __init__.py:F401
```
**What:** File-specific ignores  
**Plain English:** In `__init__.py` files, ignore F401 (unused imports), since they're often re-exported

---

## 7.4 .pylintrc

```ini
[MASTER]
disable=
    missing-module-docstring,
    missing-class-docstring,
    too-few-public-methods,
```
**What:** Disable noisy warnings  
**Plain English:** Don't warn about missing docstrings (too verbose)

---

```ini
[FORMAT]
max-line-length=100
```
**What:** Same as flake8 - max line length

---

```ini
[DESIGN]
max-attributes=7
```
**What:** Maximum attributes in a class  
**Plain English:** Classes shouldn't have more than 7 attributes (suggests poor design)

---

# 8. CI/CD WORKFLOWS

## What These Files Do
Automate testing and scanning on GitHub.

---

## 8.1 tests.yml

```yaml
name: Tests & Quality Checks

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main, develop ]
```
**What:** When to run  
**Plain English:** Run tests whenever someone pushes to main/develop or creates a pull request

---

```yaml
strategy:
  matrix:
    python-version: ['3.9', '3.10', '3.11']
```
**What:** Test on multiple Python versions  
**Plain English:** Run tests on Python 3.9, 3.10, and 3.11 to ensure compatibility

---

```yaml
- name: Install dependencies
  run: |
    python -m pip install --upgrade pip
    pip install -r requirements.txt
```
**What:** Install all dependencies

---

```yaml
- name: Run unit tests with coverage
  run: |
    pytest scanner/tests/ --cov=scanner/src --cov-report=xml
```
**What:** Run tests and measure coverage

---

```yaml
- name: Upload coverage to Codecov
  uses: codecov/codecov-action@v3
```
**What:** Send coverage report to Codecov  
**Plain English:** Upload coverage data to codecov.io so you can see coverage trends

---

## 8.2 scan.yml

```yaml
on:
  schedule:
    - cron: '0 2 * * *'
  workflow_dispatch:
```
**What:** When to run  
**Plain English:**
- `schedule` - Run daily at 2 AM UTC
- `workflow_dispatch` - Allow manual triggering

---

```yaml
- name: Configure Azure credentials
  env:
    AZURE_SUBSCRIPTION_ID: ${{ secrets.AZURE_SUBSCRIPTION_ID }}
    AZURE_CLIENT_ID: ${{ secrets.AZURE_CLIENT_ID }}
    AZURE_CLIENT_SECRET: ${{ secrets.AZURE_CLIENT_SECRET }}
    AZURE_TENANT_ID: ${{ secrets.AZURE_TENANT_ID }}
```
**What:** Load Azure credentials from GitHub Secrets  
**Plain English:** Use stored secrets (not visible in logs) to authenticate

---

```yaml
- name: Run security scan
  run: |
    python scanner/src/main.py
```
**What:** Run the scanner  
**Plain English:** Execute the main scanner to find vulnerabilities

---

```yaml
- name: Commit scan results
  run: |
    git config user.name "Security Scanner Bot"
    git config user.email "scanner@example.com"
    git add reports/
    git commit -m "chore: automated security scan results" || echo "No changes to commit"
    git push
```
**What:** Save results back to repo  
**Plain English:**
- Set up bot identity
- Add reports to git
- Commit with a message
- Push back to main branch
- If no changes, just echo "No changes"

---

# 9. TEST REPORTS SCRIPT (test_reports.py)

## What This File Does
Generates sample security findings and creates HTML/JSON reports without needing real Azure credentials. Useful for testing, documentation, and demonstrations.

### Why It Exists
When developing or demonstrating the scanner, you often can't use real Azure credentials. This script lets you generate realistic-looking findings to test the report generation system.

### Code Breakdown

```python
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
```

**What:** Docstring with detailed usage instructions  
**Plain English:** This tells anyone reading the file exactly how to use it, what it outputs, and why it's useful

---

```python
import sys
import os
```

**What:** Import system and OS modules  
**Plain English:** We need `sys` for path manipulation and `os` for cross-platform path handling

---

```python
# Add scanner/src to path for relative imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'scanner', 'src'))
```

**What:** Modify Python's import search path  
**Plain English:**
- `os.path.dirname(__file__)` - Get the directory where this script is located
- `os.path.join(..., 'scanner', 'src')` - Build the path to scanner/src folder
- `sys.path.insert(0, ...)` - Add this path to the FRONT of Python's search list

**Why?** When you run `python test_reports.py` from the repo root, Python needs to know where to find `scanner.src.core.model` and `scanner.src.core.reporter`. We're explicitly telling it.

**Example:**
```
If script is at: C:\Users\ljohn\...\Latest_Repo\test_reports.py
Then __file__ = C:\Users\ljohn\...\Latest_Repo\test_reports.py
Then dirname = C:\Users\ljohn\...\Latest_Repo
Then path = C:\Users\ljohn\...\Latest_Repo\scanner\src
```

---

```python
from scanner.src.core.model import Finding
from scanner.src.core.reporter import write_html, write_json
```

**What:** Import the classes/functions we need  
**Plain English:**
- Import `Finding` class (data structure for vulnerabilities)
- Import `write_html` function (creates HTML reports)
- Import `write_json` function (creates JSON reports)

These are the same imports used in the actual scanner checks.

---

```python
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
        references=["https://docs.microsoft.com/azure/virtual-network/network-security-groups-overview"],
        metadata={"port": 80, "source": "0.0.0.0/0"}
    ),
]
```

**What:** Create a list of sample Finding objects  
**Plain English:** 
- We create 5 different vulnerability findings
- Each represents a real security issue (NSG world-open, public storage, disabled purge protection)
- Mix of High and Medium severity
- Each has complete information (id, description, MITRE mapping, references, metadata)

**Why Multiple Examples?** 
- Tests different service types (NSG, Storage, KeyVault)
- Tests different severity levels
- Shows variety in real-world reports

**Each Finding Contains:**
- `id` - Unique identifier
- `service` - Which Azure service
- `resource` - Specific resource name/path
- `rule` - Rule code
- `description` - What the vulnerability is
- `severity` - How bad (High/Medium/Low)
- `mitre` - MITRE ATT&CK technique
- `references` - Links to documentation
- `metadata` - Extra details (port, location, etc.)

---

```python
if __name__ == "__main__":
```

**What:** Entry point check  
**Plain English:** This code only runs if someone executes this file directly (not if it's imported)

---

```python
    print(f"Generating test reports with {len(sample_findings)} sample findings...\n")
```

**What:** Print starting message  
**Plain English:** Tell the user how many findings we're about to generate (5 in this case)

**Output:**
```
Generating test reports with 5 sample findings...
```

---

```python
    # Write JSON report
    json_path = "reports/test_run.json"
    write_json(sample_findings, json_path)
    print(f"✅ JSON report: {json_path}")
```

**What:** Generate JSON report  
**Plain English:**
- Define the output path as `reports/test_run.json`
- Call `write_json()` (imported from reporter.py) with:
  - `sample_findings` - The list of findings
  - `json_path` - Where to save it
- Print confirmation message

**What write_json Does:**
- Takes each Finding object
- Converts it to a dictionary
- Writes all findings to a JSON file
- Includes nice formatting (indentation)

**Output File Example:**
```json
[
  {
    "id": "AZ-NSG-WORLD-SSH",
    "service": "NSG",
    "resource": "prod-rg/prod-nsg/allow-ssh",
    "rule": "NSG_WORLD_SSH",
    "description": "Network Security Group allows world-accessible SSH (port 22)",
    "severity": "High",
    "mitre": "T1046",
    "references": [...],
    "metadata": {...}
  }
]
```

---

```python
    # Write HTML report
    html_path = "reports/test_run.html"
    write_html("azure", sample_findings, html_path)
    print(f"✅ HTML report: {html_path}")
```

**What:** Generate HTML report  
**Plain English:**
- Define the output path as `reports/test_run.html`
- Call `write_html()` (imported from reporter.py) with:
  - `"azure"` - Cloud provider name
  - `sample_findings` - The list of findings
  - `html_path` - Where to save it
- Print confirmation message

**What write_html Does:**
- Takes the HTML template from reporter.py
- Fills in the findings data using Jinja2
- Writes formatted HTML to file

**Output File:** A nice HTML report you can open in any browser

---

```python
    print(f"\nReports generated with {len(sample_findings)} findings:")
    for finding in sample_findings:
        print(f"  - {finding.id}: {finding.description} ({finding.severity})")
```

**What:** Print summary of findings  
**Plain English:**
- Print a blank line
- Loop through each finding
- Print its ID, description, and severity

**Output Example:**
```
Reports generated with 5 findings:
  - AZ-NSG-WORLD-SSH: Network Security Group allows world-accessible SSH (port 22) (High)
  - AZ-NSG-WORLD-RDP: Network Security Group allows world-accessible RDP (port 3389) (High)
  - AZ-STG-PUBLIC-BLOB: Storage Account has public blob access enabled (High)
  - AZ-KV-PURGE-PROTECTION-DISABLED: Key Vault does not have purge protection enabled (Medium)
  - AZ-NSG-WORLD-HTTP: Network Security Group allows world-accessible HTTP (port 80) (Medium)
```

---

```python
    print("\n📖 View reports:")
    print(f"  JSON: Open {json_path} in VS Code or text editor")
    print(f"  HTML: Run 'start {html_path}' to open in browser")
```

**What:** Instructions on viewing reports  
**Plain English:** Tell the user how to open and view the generated reports

**Output:**
```
📖 View reports:
  JSON: Open reports/test_run.json in VS Code or text editor
  HTML: Run 'start reports/test_run.html' to open in browser
```

---

## test_reports.py Usage

### Running It

```bash
python test_reports.py
```

### What Happens

1. ✅ Creates `reports/test_run.json` with sample findings
2. ✅ Creates `reports/test_run.html` with formatted report
3. ✅ Prints summary to console
4. ✅ Shows you how to view the reports

### View Results

**JSON (machine-readable):**
```bash
cat reports/test_run.json
# or open in VS Code
```

**HTML (human-readable):**
```bash
# Windows
start reports/test_run.html

# macOS/Linux
open reports/test_run.html
```

---

## Why This Script Is Important

**For Development:**
- Test report generation without Azure credentials
- Verify HTML/JSON output format
- Catch formatting bugs before live runs

**For Documentation:**
- Show what findings look like
- Demonstrate scanner output format
- Create examples for capstone report

**For Demos:**
- Show stakeholders what reports look like
- No need to expose real Azure resources
- Quick, reproducible output

---

# 10. DOCKERFILE

## What This File Does
Defines how to build a Docker container for the scanner.

### Code Breakdown

```dockerfile
FROM python:3.12-slim
```
**What:** Base image  
**Plain English:** Start with Python 3.12 in a slim container (smaller than full image)

---

```dockerfile
WORKDIR /app
```
**What:** Set working directory  
**Plain English:** All commands run in `/app` directory inside the container

---

```dockerfile
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
```
**What:** Install dependencies  
**Plain English:**
- Copy requirements.txt from host to container
- Run pip install
- `--no-cache-dir` saves space by not caching packages

---

```dockerfile
COPY scanner/ ./scanner/
```
**What:** Copy code to container  
**Plain English:** Copy the entire scanner folder from host to container

---

```dockerfile
RUN mkdir -p reports
```
**What:** Create reports directory  
**Plain English:** Create the directory where reports will be saved

---

```dockerfile
ENV PYTHONUNBUFFERED=1
```
**What:** Disable Python buffering  
**Plain English:** Print output immediately (important for container logs)

---

```dockerfile
ENTRYPOINT ["python", "-m", "scanner.src.main"]
```
**What:** What to run when container starts  
**Plain English:** Run `python -m scanner.src.main` (the main scanner)

**Usage:**
```bash
docker run -e AZURE_SUBSCRIPTION_ID=xxx ... cloudscanner:latest
# Runs: python -m scanner.src.main
```

---

# END OF REFERENCE SHEET

---

This reference sheet covers every file in detail with plain English explanations. Feel free to refer back to it as you work on the project!
