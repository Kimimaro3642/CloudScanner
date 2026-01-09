# Security Policy

## Overview

CloudScanner handles cloud security scanning and credential management. This document outlines security practices, policies, and guidelines for development, deployment, and usage.

---

## Credential Management

### Development

#### Local Credentials (.env)
```bash
# .env file (NEVER commit this)
AZURE_SUBSCRIPTION_ID=your-subscription-id
AZURE_CLIENT_ID=your-client-id
AZURE_CLIENT_SECRET=your-client-secret
AZURE_TENANT_ID=your-tenant-id
```

**Rules:**
- ✅ `.env` is in `.gitignore` - verified on every commit
- ✅ Use placeholder values for documentation
- ✅ Load only when needed (via `os.getenv()`)
- ❌ Never log or print credentials
- ❌ Never hardcode in source code
- ❌ Never commit to version control

#### GitHub Secrets (CI/CD)
For GitHub Actions workflows, store secrets as repository secrets:

**Settings → Secrets and variables → Actions**

Secrets needed:
- `AZURE_SUBSCRIPTION_ID`
- `AZURE_CLIENT_ID`
- `AZURE_CLIENT_SECRET`
- `AZURE_TENANT_ID`

**Rules:**
- ✅ Only available to GitHub Actions workflows
- ✅ Never printed in logs (GitHub masks them)
- ✅ Accessible via `${{ secrets.SECRET_NAME }}`
- ❌ Cannot be accessed by pull requests from forks
- ❌ Not visible in action logs

### Testing

#### Mock Credentials
Unit tests use placeholder credentials:
```python
mock_subscription_id = "placeholder-sub-id"
mock_client_id = "placeholder-client-id"
```

**Rules:**
- ✅ Never use real credentials in tests
- ✅ Mock Azure SDK clients to avoid API calls
- ✅ Safe to commit test code

#### Integration Testing (Live Azure)
When testing against real Azure environment:
- Use `.env` file with test credentials
- Use test/non-production subscriptions only
- Never commit `.env` file
- Document test environment setup separately

### Production Deployment

#### Container Deployment
When deploying CloudScanner container:

```bash
# Azure Container Instances example
az container create \
  --resource-group rg-scanner \
  --name cloudscanner \
  --image myregistry.azurecr.io/cloudscanner:latest \
  --environment-variables \
    AZURE_SUBSCRIPTION_ID=$SUBSCRIPTION_ID \
    AZURE_CLIENT_ID=$CLIENT_ID \
    AZURE_CLIENT_SECRET=$CLIENT_SECRET \
    AZURE_TENANT_ID=$TENANT_ID
```

**Rules:**
- ✅ Use managed identities where possible (avoids secrets)
- ✅ Store secrets in Azure Key Vault
- ✅ Reference Key Vault secrets in deployment
- ✅ Restrict container registry access
- ❌ Never pass secrets in Dockerfile
- ❌ Never embed in environment variable files in repo

#### Azure Key Vault Integration (Planned)
Future enhancement to retrieve credentials from Key Vault:
```python
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient

credential = DefaultAzureCredential()
client = SecretClient(vault_url="https://myvault.vault.azure.net/", credential=credential)
secret = client.get_secret("azure-client-secret")
```

---

## Code Security

### Input Validation
- Validate Azure subscription IDs format
- Validate resource names (alphanumeric, hyphens)
- Sanitize resource names before including in reports
- Validate file paths for report output

### Output Security

#### Report Contents
Reports may contain:
- Resource names (NSG, Storage account names)
- Subscription IDs
- Resource IDs and paths
- Security findings (vulnerabilities)

**Security Practices:**
- ✅ Reports stored in secure location (reports/ directory)
- ✅ Reports not world-readable
- ✅ Sensitive data in JSON for programmatic access
- ✅ HTML reports sanitized to prevent XSS
- ❌ Never include credentials in reports
- ❌ Never log full error messages with stack traces containing secrets
- ❌ Don't expose API keys in report metadata

#### Logging
```python
# ❌ BAD - logs credentials
logger.info(f"Authenticating with {client_secret}")

# ✅ GOOD - logs only safe info
logger.info("Authenticating with Azure")

# ✅ GOOD - logs action without sensitive data
logger.debug(f"Scanning NSG: {nsg_name}")
```

### Dependency Security

#### Requirements Management
- Pin specific versions in `requirements.txt`
- Regularly update Azure SDK packages
- Monitor for security advisories
- Use `pip audit` to check for vulnerabilities

```bash
# Check for known vulnerabilities
pip audit

# Update packages safely
pip install --upgrade -r requirements.txt
```

#### Automated Dependency Scanning
GitHub Dependabot monitors `requirements.txt`:
- Automatic pull requests for updates
- Security alert notifications
- Review before merging

---

## API Access & Permissions

### Principle of Least Privilege
CloudScanner uses read-only Azure permissions:

**Required Permissions:**
```
Microsoft.Network/networkSecurityGroups/read
Microsoft.Storage/storageAccounts/read
Microsoft.KeyVault/vaults/read
```

**Never needed:**
- Write/delete permissions (scanner only reads)
- Admin roles (use custom roles)
- Subscription owner access (too broad)

### Service Principal Setup

Create dedicated service principal for scanning:
```bash
# Create service principal
az ad sp create-for-rbac \
  --name "cloudscanner" \
  --role Reader \
  --scopes /subscriptions/{subscription-id}
```

**Permissions:**
- Assign `Reader` role (read-only)
- Scope to specific subscription
- Don't use Owner or Contributor roles

### Audit & Monitoring
- Monitor scanner authentication in Azure audit logs
- Track resource access patterns
- Alert on suspicious activity
- Regular access reviews (quarterly)

---

## Secrets Scanning

### GitHub Push Protection
GitHub automatically scans commits for secrets:
- Azure credentials detected and blocked
- Connection strings detected and blocked
- API keys detected and blocked

**If Secrets Detected:**
1. DO NOT push with `--force`
2. Remove secret from commit
3. Rotate compromised credentials
4. Amend commit and push again
5. Document incident

### Pre-commit Hooks (Recommended)
Local scanning before commit:
```bash
pip install detect-secrets
detect-secrets scan --baseline .secrets.baseline
```

---

## Infrastructure Security

### Container Security
When deploying Docker container:

```dockerfile
# ✅ Use specific Python version
FROM python:3.12-slim

# ✅ Don't run as root
USER appuser

# ✅ Use minimal base image (slim)
# ❌ DON'T use python:latest (unknown version)
# ❌ DON'T RUN as root (security risk)
# ❌ DON'T include secrets in Dockerfile
```

### Network Security
- Only expose necessary ports (none for scanner - read-only)
- Use Azure Network Security Groups to restrict access
- Encrypt data in transit (Azure SDK uses HTTPS by default)
- Run scanner in isolated network (not internet-facing)

### Storage Security
For report storage:
- Use Azure Blob Storage with authentication
- Enable encryption at rest
- Restrict access via RBAC
- Enable auditing on read/write operations
- Don't store reports publicly

---

## Incident Response

### Credential Compromise
**If Azure credentials are exposed:**

1. **Immediately rotate credentials:**
   ```bash
   # In Azure Portal or CLI
   az ad sp credential reset --id {object-id}
   ```

2. **Remove from git history:**
   ```bash
   # Remove file from all commits
   git filter-branch --tree-filter 'rm -f config-notes.txt' HEAD
   git push origin --force --all
   ```

3. **Audit access logs:**
   - Check Azure audit logs for unauthorized API calls
   - Review report access in storage logs

4. **Update secrets everywhere:**
   - Update `.env` file locally
   - Update GitHub Secrets
   - Update deployed containers
   - Notify team members

5. **Document incident:**
   - What was exposed
   - When discovered
   - Actions taken
   - Prevention measures

### Vulnerability Disclosure
If you discover a vulnerability in CloudScanner:

1. **DO NOT** post in public issues
2. **Email:** (future: add contact)
3. Provide vulnerability details
4. Allow 90 days for patch before public disclosure

---

## Compliance & Standards

### OWASP Top 10
CloudScanner follows OWASP security practices:
- No hardcoded secrets (Broken Access Control)
- Input validation (Injection)
- No sensitive data in logs (Sensitive Data Exposure)
- Dependency scanning (Using Components with Known Vulnerabilities)

### Azure Security Best Practices
- Follows Azure SDK security guidelines
- Uses Azure SDK authentication patterns
- Respects RBAC and managed identities

### NIST Cybersecurity Framework
Applicable standards:
- **Identify:** Asset inventory (Azure resources)
- **Protect:** Security configuration scanning
- **Detect:** Vulnerability detection
- **Respond:** Report generation for incident response
- **Recover:** Audit trails for recovery

---

## Security Checklist

### Before Committing Code
- [ ] No hardcoded credentials
- [ ] No secrets in comments
- [ ] `.env` file not included
- [ ] All sensitive data is in `.gitignore`
- [ ] Run `git diff --cached` to verify

### Before Pushing to GitHub
- [ ] GitHub push protection passed
- [ ] No secrets detected in commits
- [ ] Code review completed (for shared repo)
- [ ] All tests passing

### Before Deploying
- [ ] Credentials stored in Key Vault (not in code)
- [ ] Environment variables set in deployment
- [ ] Container image scanned for vulnerabilities
- [ ] Network access restricted appropriately
- [ ] Audit logging enabled
- [ ] Access permissions follow least privilege

### Regular Maintenance
- [ ] Review Azure audit logs monthly
- [ ] Update dependencies quarterly
- [ ] Rotate service principal credentials annually
- [ ] Review access permissions semi-annually
- [ ] Run security vulnerability scan (`pip audit`)

---

## References

- [Azure Security Best Practices](https://docs.microsoft.com/azure/security/fundamentals/best-practices-and-patterns)
- [Azure SDK Authentication](https://docs.microsoft.com/python/api/azure-identity/)
- [OWASP Secure Coding Practices](https://owasp.org/www-community/controls/)
- [GitHub Secrets Management](https://docs.github.com/en/actions/security-guides/encrypted-secrets)
- [Python Security Best Practices](https://python.readthedocs.io/en/latest/library/security_warnings.html)

---

**Last Updated:** Jan 9, 2026  
**Status:** Initial Security Policy (to be reviewed during production deployment)