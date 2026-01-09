import os
from .core.clients import AzureClients
from .checks.nsg import check_nsg_world_open
from .checks.storage import check_storage_public
from .checks.keyvault import check_keyvault_purge_protection

def run_azure():
    sub=os.getenv("AZURE_SUBSCRIPTION_ID")
    ten=os.getenv("AZURE_TENANT_ID")
    cid=os.getenv("AZURE_CLIENT_ID")
    sec=os.getenv("AZURE_CLIENT_SECRET")
    c=AzureClients(sub,ten,cid,sec)
    f=[]
    f+=check_nsg_world_open(c.network)
    f+=check_storage_public(c.storage)
    f+=check_keyvault_purge_protection(c.keyvault)
    return f
