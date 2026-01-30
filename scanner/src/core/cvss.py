RULE_SEVERITY = {
    "NSG_WORLD_SSH": "High",
    "NSG_WORLD_RDP": "High",
    "NSG_WORLD_HTTP": "Medium",
    "STG_PUBLIC_BLOB": "High",
    "KV_NO_PURGE_PROTECTION": "Medium",
}

# CVSS 3.1 scores for each rule (0.0 - 10.0)
# Critical: 9.0-10.0 | High: 7.0-8.9 | Medium: 4.0-6.9 | Low: 0.1-3.9
RULE_CVSS = {
    "NSG_WORLD_SSH": 9.8,           # Critical - Remote execution possible
    "NSG_WORLD_RDP": 9.8,           # Critical - Remote execution possible
    "NSG_WORLD_HTTP": 7.5,          # High - Exposure to attacks
    "STG_PUBLIC_BLOB": 9.1,         # Critical - Data exposure
    "KV_NO_PURGE_PROTECTION": 6.5,  # Medium - Recovery/deletion risk
}

def severity_for(rule: str) -> str:
    return RULE_SEVERITY.get(rule, "Low")

def cvss_for(rule: str) -> float:
    """Get CVSS 3.1 score for a rule"""
    return RULE_CVSS.get(rule, 0.0)
