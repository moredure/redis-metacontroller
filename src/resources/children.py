class Children:
    REDIS_CONTAINER = 0

    POD_V1 = 'Pod.v1'
    SERVICE_V1 = 'Service.v1'
    PVCS_V1 = 'PersistentVolumeClaim.v1'

    def __init__(self, data: dict):
        self._data = data

    @property
    def pods(self) -> dict:
        return self._data[self.POD_V1]

    @property
    def services(self) -> dict:
        return self._data[self.SERVICE_V1]

    @property
    def pvcs(self) -> dict:
        return self._data[self.PVCS_V1]

    def maxmemory(self, name: str) -> str:
        return self.pods[name]['spec']['containers'][self.REDIS_CONTAINER]['resources']['limits']['memory']

    def storage(self, name: str) -> str:
        return self.pvcs[name]['spec']['resources']['requests']['storage'] if self.pvcs.get(name) else '0M'

    def pod_phase(self, name: str) -> bool:
        return self.pods.get(name, {}).get('status', {}).get('phase')
