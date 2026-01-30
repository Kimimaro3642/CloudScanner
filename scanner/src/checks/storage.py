from ..core.model import Finding
from ..core.cvss import severity_for, cvss_for
from ..core.mitre import mitre_for

def check_storage_public(stg):
    findings=[]
    for acct in stg.storage_accounts.list():
        rg = acct.id.split("/resourceGroups/")[1].split("/")[0]
        props=stg.storage_accounts.get_properties(rg,acct.name)
        if getattr(props,"allow_blob_public_access",None):
            findings.append(Finding(
                id="AZ-STG-PUBLIC-BLOB",service="Storage",
                resource=acct.name,rule="STG_PUBLIC_BLOB",
                description="Public blob access enabled",
                severity=severity_for("STG_PUBLIC_BLOB"),
                mitre=mitre_for("STG_PUBLIC_BLOB"),
                cvss_score=cvss_for("STG_PUBLIC_BLOB")
            ))
    return findings
