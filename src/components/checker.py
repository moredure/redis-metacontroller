from src.resources.children import Children
from src.resources.redis import Redis


class Checker:
    SUCCEEDED = 'Succeeded'
    RUNNING = 'Running'
    FAILED = 'Failed'

    def is_pending(self, redis: Redis) -> bool:
        return redis.phase == Redis.PENDING

    def is_pending_volume(self, redis: Redis) -> bool:
        return redis.phase == Redis.PENDING_VOLUME

    def is_running(self, redis: Redis) -> bool:
        return redis.phase == Redis.RUNNING

    def is_migrating(self, redis: Redis) -> bool:
        return redis.phase == Redis.MIGRATING

    def is_source_memory_changed(self, redis: Redis, children: Children) -> bool:
        return children.maxmemory(redis.source) != redis.maxmemory

    def is_source_storage_changed(self, redis: Redis, children: Children) -> bool:
        return children.storage(redis.source) != redis.storage

    def is_source_memory_or_storage_changed(self, redis: Redis, children: Children) -> bool:
        return self.is_source_memory_changed(redis, children) or self.is_source_storage_changed(redis, children)

    def is_migration_job_completed(self, redis: Redis, children: Children) -> bool:
        return children.pod_phase(redis.migration_job) == self.SUCCEEDED

    def is_migration_job_failed(self, redis: Redis, children: Children) -> bool:
        return children.pod_phase(redis.migration_job) == self.FAILED

    def is_target_pod_ready(self, redis: Redis, children: Children) -> bool:
        return children.pod_phase(redis.target) == self.RUNNING

    def is_target_pod_failed(self, redis: Redis, children: Children) -> bool:
        return children.pod_phase(redis.target) == self.FAILED

    def is_source_pod_ready(self, redis: Redis, children: Children) -> bool:
        return children.pod_phase(redis.source) == self.RUNNING

    def is_source_pod_failed(self, redis: Redis, children: Children) -> bool:
        return children.pod_phase(redis.source) == self.FAILED
