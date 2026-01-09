RULE_SEVERITY = {
    "NSG_WORLD_SSH": "High",
    "NSG_WORLD_RDP": "High",
    "NSG_WORLD_HTTP": "Medium",
    "STG_PUBLIC_BLOB": "High",
    "KV_NO_PURGE_PROTECTION": "Medium",
}
def severity_for(rule: str) -> str:
    return RULE_SEVERITY.get(rule, "Low")
