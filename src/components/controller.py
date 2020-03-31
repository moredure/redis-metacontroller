from src.components.checker import Checker
from src.components.resolver import Resolver
from src.resources.children import Children
from src.resources.redis import Redis


class Controller:
    def __init__(self, checker: Checker, resolver: Resolver):
        self.checker = checker
        self.resolver = resolver

    def sync(self, redis: Redis, children: Children) -> dict:
        if self.checker.is_pending(redis):
            return self._on_pending(redis, children)
        elif self.checker.is_running(redis):
            return self._on_running(redis, children)
        elif self.checker.is_migrating(redis):
            return self._on_migrating(redis, children)
        else:
            raise AssertionError

    def _on_pending(self, redis: Redis, children: Children) -> dict:
        if self.checker.is_source_pod_ready(redis, children):
            return self.resolver.created(redis)
        else:
            return self.resolver.creating(redis)

    def _on_running(self, redis: Redis, children: Children) -> dict:
        if self.checker.is_source_pod_ready(redis, children):
            if self.checker.is_source_memory_or_storage_changed(redis, children):
                if self.checker.is_target_pod_ready(redis, children):
                    return self.resolver.migrating(redis)
                else:
                    return self.resolver.creating_target(redis)
            else:
                return self.resolver.created(redis)
        if self.checker.is_source_pod_failed(redis, children):
            return self.resolver.recreate(redis)
        else:
            return self.resolver.creating(redis)

    def _on_migrating(self, redis: Redis, children: Children) -> dict:
        if self.checker.is_source_pod_ready(redis, children):
            if self.checker.is_migration_job_completed(redis, children):
                return self.resolver.finished(redis)
            # need to rule for migration job error
            else:
                return self.resolver.migrating(redis)
        else:
            return self.resolver.finished(redis)
