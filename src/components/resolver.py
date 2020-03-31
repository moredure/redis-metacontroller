from src.components.creator import Creator
from src.resources.redis import Redis


class Resolver:
    def __init__(self, creator: Creator):
        self.creator = creator

    def creating(self, redis: Redis) -> dict:
        return self._template(redis, redis.source, Redis.PENDING)

    def created(self, redis: Redis) -> dict:
        return self._template(redis, redis.source, Redis.RUNNING)

    def finished(self, redis: Redis) -> dict:
        return self._template(redis, redis.target, Redis.PENDING)

    def _template(self, redis: Redis, pod_name: str, phase: str) -> dict:
        return {
            'status': {
                'source': pod_name,
                'phase': phase,
                'storage': redis.empty_storage
            },
            'children': [
                self.creator.create_service(redis, pod_name),

                *self.creator.create_instance(pod_name, redis),
                None if redis.empty_storage else self.creator.create_pvc(pod_name, redis)
            ]
        }

    def recreate(self, redis: Redis) -> dict:
        return {
            'status': {
                'source': redis.source,
                'phase': Redis.PENDING,
                'storage': redis.empty_storage
            },
            'children': [
                self.creator.create_service(redis, redis.source),

                *self.creator.recreate_instance(redis.source),
                None if redis.empty_storage else self.creator.create_pvc(redis.source, redis)
            ]
        }

    def creating_target(self, redis: Redis) -> dict:
        return {
            'status': {
                'source': redis.source,
                'target': redis.target,
                'phase': Redis.RUNNING,
                'storage': redis.source_empty_storage
            },
            'children': [
                self.creator.create_service(redis, redis.source),

                *self.creator.create_instance(redis.source, redis),
                None if redis.source_empty_storage else self.creator.create_pvc(redis.source, redis),

                *self.creator.create_instance(redis.target, redis),
                None if redis.empty_storage else self.creator.create_pvc(redis.target, redis)
            ]
        }

    def migrating(self, redis: Redis) -> dict:
        return {
            'status': {
                'source': redis.source,
                'target': redis.target,
                'migration_job': redis.migration_job,
                'phase': Redis.MIGRATING,
                'storage': redis.source_empty_storage
            },
            'children': [
                self.creator.create_service(redis, redis.source),

                *self.creator.create_instance(redis.source, redis),
                None if redis.source_empty_storage else self.creator.create_pvc(redis.source, redis),

                *self.creator.create_instance(redis.target, redis),
                None if redis.empty_storage else self.creator.create_pvc(redis.target, redis),

                self.creator.create_job(redis)
            ]
        }
