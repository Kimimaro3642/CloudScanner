RULE_MITRE = {
    "NSG_WORLD_SSH": "T1046",
    "NSG_WORLD_RDP": "T1046",
    "NSG_WORLD_HTTP": "T1190",
    "STG_PUBLIC_BLOB": "T1530",
    "KV_NO_PURGE_PROTECTION": "T1211",
}
def mitre_for(rule: str) -> str:
    return RULE_MITRE.get(rule, "-")
