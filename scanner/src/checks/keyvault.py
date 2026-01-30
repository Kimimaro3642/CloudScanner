from ..core.model import Finding
from ..core.cvss import severity_for, cvss_for
from ..core.mitre import mitre_for

def check_keyvault_purge_protection(kv):
    findings=[]
    for v in kv.vaults.list_by_subscription():
        enabled=getattr(getattr(v,"properties",None),"enable_purge_protection",None)
        if not enabled:
            findings.append(Finding(
                id="AZ-KV-PURGE-PROTECTION-DISABLED",service="KeyVault",
                resource=v.name,rule="KV_NO_PURGE_PROTECTION",
                description="Purge protection disabled",
                severity=severity_for("KV_NO_PURGE_PROTECTION"),
                mitre=mitre_for("KV_NO_PURGE_PROTECTION"),
                cvss_score=cvss_for("KV_NO_PURGE_PROTECTION")
            ))
    return findings
