# CloudScanner Architecture

## Overview

CloudScanner is a multi-cloud security scanning platform designed to detect misconfigurations and security vulnerabilities across cloud resources. It uses a modular, extensible architecture to support multiple cloud providers.

**Current Focus:** Azure (NSG, Storage, Key Vault)  
**Planned:** GCP, AWS

---

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     CloudScanner System                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌──────────────┐                                                │
│  │   CLI Entry  │                                                │
│  │  (main.py)   │                                                │
│  └──────┬───────┘                                                │
│         │                                                         │
│         ▼                                                         │
│  ┌──────────────────────┐                                        │
│  │  Orchestration       │                                        │
│  │  (scan.py:run_azure) │                                        │
│  └──────┬───────────────┘                                        │
│         │                                                         │
│    ┌────┴────────────────────┐                                   │
│    │                         │                                   │
│    ▼                         ▼                                   │
│  ┌──────────────┐      ┌──────────────┐                         │
│  │ Azure Clients│      │ Azure Clients│                         │
│  │ (clients.py) │      │ (clients.py) │                         │
│  └──────┬───────┘      └──────┬───────┘                         │
│         │                     │                                 │
│    ┌────┴─────────────────────┴────┐                            │
│    │                               │                            │
│    ▼                               ▼                            │
│  ┌─────────────┐  ┌─────────────┐  ┌──────────────┐            │
│  │  NSG Check  │  │ Storage Chk │  │ KeyVault Chk │            │
│  │ (checks/)   │  │ (checks/)   │  │  (checks/)   │            │
│  └──────┬──────┘  └──────┬──────┘  └──────┬───────┘            │
│         │                │               │                     │
│         └────────┬───────┴───────────────┘                      │
│                  │                                              │
│                  ▼                                              │
│         ┌────────────────┐                                      │
│         │   Findings     │                                      │
│         │  (model.py)    │                                      │
│         └────────┬───────┘                                      │
│                  │                                              │
│         ┌────────┴────────┐                                     │
│         │                 │                                     │
│         ▼                 ▼                                     │
│    ┌─────────┐      ┌──────────┐                               │
│    │ HTML    │      │ JSON     │                               │
│    │ Report  │      │ Report   │                               │
│    └─────────┘      └──────────┘                               │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Component Details

### Entry Points

#### `scanner/src/main.py`
- CLI interface using argparse
- Arguments: `--out` (HTML path), `--json` (JSON path)
- Calls `scan.run_azure()` and passes findings to reporter
- Handles environment variable loading for Azure credentials

#### `scanner/src/scan.py`
- **Function:** `run_azure()`
- Initializes `AzureClients` with subscription/tenant/credentials
- Orchestrates all checks in sequence
- Aggregates findings from all checks
- Returns list of `Finding` objects

### Azure Integration

#### `scanner/src/core/clients.py`
- **Class:** `AzureClients`
- Wraps Azure SDK authentication
- Properties:
  - `.network` - Network client for NSG checks
  - `.storage` - Storage client for account checks
  - `.keyvault` - KeyVault client for vault checks

### Security Checks

#### `scanner/src/checks/`

**NSG Check** (`nsg.py`)
- **Function:** `check_nsg_world_open(net)`
- Input: Azure Network client
- Detects: Inbound Allow rules with world-accessible source (0.0.0.0/0)
- Ports: 22 (SSH), 3389 (RDP), others (HTTP)
- Output: List of `Finding` objects

**Storage Check** (`storage.py`)
- **Function:** `check_storage_public(stg)`
- Input: Azure Storage client
- Detects: Storage accounts with public blob access enabled
- Output: List of `Finding` objects

**KeyVault Check** (`keyvault.py`)
- **Function:** `check_keyvault_purge_protection(kv)`
- Input: Azure KeyVault client
- Detects: Key Vaults without purge protection enabled
- Output: List of `Finding` objects

### Data Models

#### `scanner/src/core/model.py`
- **Class:** `Finding`
- Attributes:
  - `id` - Unique identifier (e.g., "AZ-NSG-WORLD-SSH")
  - `service` - Cloud service (NSG, Storage, KeyVault)
  - `resource` - Affected resource name/path
  - `rule` - Check rule code (e.g., NSG_WORLD_SSH)
  - `description` - Human-readable description
  - `severity` - CVSS severity level
  - `mitre` - MITRE ATT&CK technique
- Serializable to JSON/HTML

### Severity & Mapping

#### `scanner/src/core/cvss.py`
- **Function:** `severity_for(rule_code)`
- Maps rule codes to CVSS severity scores
- Returns: severity level (Critical, High, Medium, Low)

#### `scanner/src/core/mitre.py`
- **Function:** `mitre_for(rule_code)`
- Maps security findings to MITRE ATT&CK techniques
- Provides framework context for findings

### Reporting

#### `scanner/src/core/reporter.py`
- **Functions:**
  - `write_html(cloud, findings, path)` - Generate HTML report
  - `write_json(findings, path)` - Generate JSON report
- Formats findings for human/machine consumption
- Supports multiple cloud providers

---

## Data Flow

### Execution Flow

```
1. User runs: python scanner/src/main.py
   ↓
2. main.py loads environment variables (.env)
   ↓
3. main.py calls scan.run_azure()
   ↓
4. run_azure() initializes AzureClients
   ↓
5. run_azure() calls each check:
   - check_nsg_world_open(clients.network)
   - check_storage_public(clients.storage)
   - check_keyvault_purge_protection(clients.keyvault)
   ↓
6. Each check queries Azure, returns findings
   ↓
7. run_azure() aggregates findings into list
   ↓
8. main.py passes findings to reporter
   ↓
9. reporter generates HTML + JSON outputs
   ↓
10. Reports written to disk (reports/)
   ↓
11. User views report in browser or parses JSON
```

### Finding Creation Flow

```
Check Function
   ↓
   └─→ Query Azure API (e.g., list all NSGs)
   ↓
   └─→ Iterate resources
   ↓
   └─→ Evaluate security rules
   ↓
   └─→ Create Finding object if vulnerable
       ├─ id = f"AZ-{SERVICE}-{RULE}"
       ├─ severity = severity_for(rule)
       ├─ mitre = mitre_for(rule)
       └─ description = human description
   ↓
   └─→ Return list of Finding objects
```

---

## Extension Points

### Adding New Azure Checks

1. Create new file in `scanner/src/checks/`
2. Implement function: `check_X(client)`
3. Function returns list of `Finding` objects
4. Import and call in `scan.run_azure()`

Example:
```python
# scanner/src/checks/sql.py
def check_sql_tls_version(sql_client):
    findings = []
    for server in sql_client.servers.list():
        if not check_tls_12_enforced(server):
            findings.append(Finding(
                id="AZ-SQL-TLS",
                service="SQL",
                resource=server.name,
                rule="SQL_OLD_TLS",
                description="TLS 1.2+ not enforced",
                severity=severity_for("SQL_OLD_TLS"),
                mitre=mitre_for("SQL_OLD_TLS")
            ))
    return findings
```

### Adding New Cloud Providers

1. Create `scanner/src/core/providers/gcp_clients.py`
2. Implement cloud-specific client wrapper
3. Create `scanner/src/checks/gcp/` for GCP checks
4. Create `scan.run_gcp()` function
5. Update main.py to support multi-cloud

---

## Testing Architecture

### Unit Tests
- Located: `scanner/tests/`
- Framework: pytest with unittest.mock
- Coverage: 45%+
- Test files:
  - `conftest.py` - Shared fixtures
  - `test_nsg.py` - NSG check tests
  - `test_storage.py` - Storage check tests
  - `test_keyvault.py` - KeyVault check tests

### Test Strategy
- Mock Azure clients to avoid live API calls
- Test both positive (vulnerable) and negative (secure) scenarios
- Verify Finding object creation with correct attributes
- Run on every push via GitHub Actions

---

## Deployment Architecture

### Containerization
- **Base Image:** Python 3.12-slim
- **Working Dir:** /app
- **Entry Point:** `python -m scanner.src.main`
- **Volumes:** /app/reports (for output)
- **Environment:** Azure credentials via env vars

### Orchestration (Planned)
- **Tool:** Terraform
- **Target:** Azure Container Instances (ACI) or similar
- **Triggers:** Manual or scheduled (daily scans)
- **Output Storage:** Azure Blob Storage or mounted volume

### CI/CD Pipeline
- **Platform:** GitHub Actions
- **Tests:** Run on every push (tests.yml)
- **Scans:** Scheduled daily + manual trigger (scan.yml)
- **Docker:** Build image, push to registry (planned)
- **Terraform:** Apply infrastructure changes (planned)

---

## Security Considerations

### Credential Management
- Azure credentials passed via environment variables
- `.env` file excluded from git (in .gitignore)
- GitHub Secrets for CI/CD pipeline
- No credentials logged or printed

### API Access
- Minimal permissions required (read-only scanning)
- Uses Azure SDK with managed identity support
- Each check only accesses required service

### Report Handling
- Findings may contain sensitive resource names
- Reports written to local disk or secure storage
- JSON format for programmatic processing
- HTML for human review

---

## Performance Considerations

### API Call Optimization
- Batch operations where possible
- Cache results if re-scanning same subscription
- Handle pagination for large resource lists
- Timeout handling for slow/unresponsive APIs

### Scalability
- Supports multiple subscriptions (planned)
- Can be containerized and parallelized
- Reports stored separately from scanning logic
- Modular design allows horizontal scaling

---

## Dependencies

### Runtime
- Python 3.12+
- Azure SDK libraries (azure-identity, azure-mgmt-network, etc.)
- See `requirements.txt`

### Development
- pytest (testing)
- pylint, flake8 (code quality)
- Docker (containerization)
- Terraform (infrastructure)

---

## Future Architecture Changes

### Planned Enhancements
- [ ] GCP support (Compute, Storage, Secrets)
- [ ] AWS support (EC2, S3, Secrets Manager)
- [ ] Persistence layer (database for historical findings)
- [ ] WebUI for result browsing
- [ ] Alert/notification system (email, Slack)
- [ ] Custom rule engine for user-defined checks

### Potential Refactoring
- Abstract check interface for consistency
- Plugin system for third-party checks
- Configuration file support (YAML/JSON)
- Caching layer for performance

---

**Last Updated:** Jan 9, 2026