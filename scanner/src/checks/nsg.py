from ..core.model import Finding
from ..core.cvss import severity_for, cvss_for
from ..core.mitre import mitre_for

def check_nsg_world_open(net):
    findings=[]
    for nsg in net.network_security_groups.list_all():
        rg = nsg.id.split("/resourceGroups/")[1].split("/")[0]
        rules = (nsg.security_rules or []) + (nsg.default_security_rules or [])
        for r in rules:
            if getattr(r,"access","")!="Allow": continue
            if getattr(r,"direction","")!="Inbound": continue
            src=getattr(r,"source_address_prefix","")
            if src=="0.0.0.0/0":
                port=str(getattr(r,"destination_port_range",""))
                if port=="22":
                    code="NSG_WORLD_SSH"
                elif port=="3389":
                    code="NSG_WORLD_RDP"
                else:
                    code="NSG_WORLD_HTTP"
                findings.append(Finding(
                    id=f"AZ-NSG-{code}",service="NSG",
                    resource=f"{rg}/{nsg.name}/{r.name}",
                    rule=code,description=f"World access to {port}",
                    severity=severity_for(code),mitre=mitre_for(code),
                    cvss_score=cvss_for(code)))
    return findings
