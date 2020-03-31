from src.tools.lazy import lazy


class Redis:
    PENDING = 'Pending'
    PENDING_VOLUME = 'PendingVolume'
    RUNNING = 'Running'
    MIGRATING = 'Migrating'

    IN_MEMORY = 'InMemory'
    PERSISTENT = 'Persistent'
    EMPTY_DIR = 'EmptyDir'

    _POD_0 = 'pod-0'
    _POD_1 = 'pod-1'

    def __init__(self, data: dict):
        self._data = data

    @lazy
    def _pod_1(self) -> str:
        return f'{self.name}-{self._POD_1}'

    @lazy
    def _pod_0(self) -> str:
        return f'{self.name}-{self._POD_0}'

    @lazy
    def _default_target(self) -> str:
        return self._pod_0 if self.source == self._pod_1 else self._pod_1

    @lazy
    def _default_source(self) -> str:
        return self._pod_0

    @lazy
    def _default_migration_job(self) -> str:
        return f'from-{self.source}-to-{self.target}'

    @lazy
    def _status(self) -> dict:
        return self._data.get('status', {})

    @property
    def target(self) -> str:
        return self._status.get('target', self._default_target)

    @property
    def migration_job(self) -> str:
        return self._status.get('migration_job', self._default_migration_job)

    @property
    def source(self) -> str:
        return self._status.get('source', self._default_source)

    @property
    def shutdown(self) -> str:
        return self._data['spec']['shutdown']

    @property
    def phase(self) -> str:
        return self._status.get('phase', self.PENDING)

    @property
    def config(self) -> str:
        return self._data['spec']['config']

    @property
    def snapshot(self) -> str:
        return self._data['spec'].get('snapshot', '')

    @property
    def save(self) -> str:
        return self._data['spec']['save']

    @property
    def bgsave(self) -> str:
        return self._data['spec']['bgsave']

    @property
    def bgwriteaof(self) -> str:
        return self._data['spec']['bgwriteaof']

    @property
    def maxmemory(self) -> str:
        return self._data['spec']['maxmemory']

    @property
    def storage(self) -> str:
        return self._data['spec']['storage']

    @property
    def empty_storage(self) -> bool:
        return self.storage == '0M'

    @property
    def storage_class_name(self) -> str:
        return self._data['spec'].get('storageClassName', self.IN_MEMORY)

    @property
    def name(self) -> str:
        return self._data['metadata']['name']

    @property
    def plan_id(self) -> str:
        return self._data['spec']['plan_id']

    @property
    def user_id(self) -> str:
        return self._data['spec']['user_id']

    @property
    def node_id(self) -> str:
        return self._data['spec']['node_id']

    @property
    def instance_id(self) -> str:
        return self._data['spec']['instance_id']

    @property
    def maxclients(self) -> str:
        return self._data['spec']['maxclients']

    @property
    def databases(self) -> str:
        return self._data['spec']['databases']

    @property
    def requirepass(self) -> str:
        return self._data['spec']['requirepass']

    @property
    def source_empty_storage(self) -> bool:
        return self._data['status']['storage']

    @property
    def maxmemory_policy(self) -> str:
        return self._data['spec'].get('maxmemory_policy', 'volatile-lru')

    @property
    def rediscommand(self) -> str:
        return self._data['spec'].get('rediscommand', 'redis-server')

    @property
    def redisimage(self) -> str:
        return self._data['spec'].get('redisimage', 'redis:5-alpine')
