from azure.identity import ClientSecretCredential
from azure.mgmt.network import NetworkManagementClient
from azure.mgmt.storage import StorageManagementClient
from azure.mgmt.keyvault import KeyVaultManagementClient

class AzureClients:
    def __init__(self, subscription_id, tenant_id, client_id, client_secret):
        self.subscription_id = subscription_id
        self.credential = ClientSecretCredential(tenant_id=tenant_id, client_id=client_id, client_secret=client_secret)
        self._net=None; self._stg=None; self._kv=None

    @property
    def network(self):
        if not self._net:
            self._net = NetworkManagementClient(self.credential, self.subscription_id)
        return self._net

    @property
    def storage(self):
        if not self._stg:
            self._stg = StorageManagementClient(self.credential, self.subscription_id)
        return self._stg

    @property
    def keyvault(self):
        if not self._kv:
            self._kv = KeyVaultManagementClient(self.credential, self.subscription_id)
        return self._kv
