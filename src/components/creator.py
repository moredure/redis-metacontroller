from src.resources.redis import Redis
from src.tools.config import Config


class Creator:
    def __init__(self, config: Config):
        self.config = config

    def create_instance(self, name: str, redis: Redis) -> list:
        return [
            self._create_headless_service(name),
            self._create_pod(name, redis)
        ]

    def recreate_instance(self, name: str) -> list:
        return [
            self._create_headless_service(name),
        ]

    def create_job(self, redis: Redis) -> dict:
        return {
            'apiVersion': 'v1',
            'kind': 'Pod',
            'metadata': {
                'name': redis.migration_job
            },
            'spec': {
                'terminationGracePeriodSeconds': 0,
                'restartPolicy': 'Never',
                'imagePullSecrets': [
                    {
                        'name': self.config.private_image_registry
                    }
                ],
                'containers': [
                    {
                        'name': 'migrator',
                        'image': self.config.migrator_image,
                        'imagePullPolicy': 'Always',
                        'env': self._create_migrator_env(redis)
                    }
                ]
            }
        }

    def create_service(self, redis: Redis, target: str) -> dict:
        return {
            'apiVersion': 'v1',
            'kind': 'Service',
            'metadata': {
                'name': redis.name
            },
            'spec': {
                'selector': {
                    'app': target
                },
                'ports': [
                    {
                        'name': 'redis',
                        'protocol': 'TCP',
                        'port': self.config.redis_port,
                        'targetPort': self.config.redis_port
                    },
                    {
                        'name': 'agent',
                        'protocol': 'TCP',
                        'port': self.config.agent_port,
                        'targetPort': self.config.agent_port
                    }
                ]
            }
        }

    def create_pvc(self, name: str, redis: Redis) -> dict:
        return {
            'apiVersion': 'v1',
            'kind': 'PersistentVolumeClaim',
            'metadata': {
                'name': name
            },
            'spec': {
                'storageClassName': self.config.storage_class,
                'accessModes': [
                    'ReadWriteOnce'
                ],
                'resources': {
                    'requests': {
                        'storage': redis.storage
                    }
                }
            }
        }

    def _create_headless_service(self, name: str) -> dict:
        return {
            'apiVersion': 'v1',
            'kind': 'Service',
            'metadata': {
                'name': name
            },
            'spec': {
                'clusterIP': 'None',
                'selector': {
                    'app': name
                },
                'ports': [
                    {
                        'name': 'redis',
                        'port': self.config.redis_port
                    }
                ]
            }
        }

    def _create_pod(self, name: str, redis: Redis) -> dict:
        return {
            'apiVersion': 'v1',
            'kind': 'Pod',
            'metadata': {
                'name': name,
                'labels': {
                    'app': name
                }
            },
            'spec': {
                'terminationGracePeriodSeconds': 0,
                'imagePullSecrets': [
                    {
                        'name': self.config.private_image_registry
                    }
                ],
                'initContainers': [
                    {
                        'name': 'initializer',
                        'image': self.config.initializer_image,
                        'imagePullPolicy': 'Always',
                        'env': self._create_initializer_env(redis),
                        'volumeMounts': [
                            _create_mount(self.config.data_volume, self.config.volume_path)
                        ]
                    }
                ],
                'containers': [
                    {
                        'name': 'redis',
                        'image': redis.redisimage,
                        'imagePullPolicy': 'Always',
                        'command': [redis.rediscommand, self.config.config_path],
                        'ports': [
                            {
                                'name': 'redis',
                                'containerPort': self.config.redis_port
                            }
                        ],
                        'volumeMounts': [
                            _create_mount(self.config.data_volume, self.config.volume_path)
                        ],
                        'resources': {
                            'limits': {
                                'memory': redis.maxmemory
                            }
                        },
                    },
                    {
                        'name': 'agent',
                        'image': self.config.agent_image,
                        'resources': {
                            'limits': {
                                'memory': self.config.agent_memory
                            }
                        },
                        'imagePullPolicy': 'Always',
                        'ports': [
                            {
                                'name': 'agent',
                                'containerPort': self.config.agent_port
                            }
                        ],
                        'env': self._create_agent_env(redis),
                        'volumeMounts': [
                            _create_mount(self.config.data_volume, self.config.volume_path)
                        ]
                    },
                ],
                'volumes': self._volumes(name, redis)
            }
        }

    def _volumes(self, name: str, redis: Redis) -> list:
        return [
            {
                'name': self.config.data_volume,
                'emptyDir': {}
            } if redis.empty_storage else {
                'name': self.config.data_volume,
                'persistentVolumeClaim': {
                    'claimName': name
                }
            }
        ]

    def _create_migrator_env(self, redis: Redis) -> list:
        return [
            _create_variable('REDIS_SOURCE', f'redis://:{redis.requirepass}@{redis.source}:6379'),
            _create_variable('REDIS_DESTINATION', f'redis://:{redis.requirepass}@{redis.target}:6379'),
            _create_variable('CONFIG', redis.config)
        ]

    def _create_initializer_env(self, redis: Redis) -> list:
        return [
            _create_variable('REDIS_CONFIG', self._create_config(redis)),
            _create_variable('REDIS_CONFIG_PATH', self.config.config_path),
            _create_variable('AWS_REGION', self.config.aws_region),
            _create_variable('AWS_ACCESS_KEY_ID', self.config.aws_access_key_id),
            _create_variable('AWS_SECRET_ACCESS_KEY', self.config.aws_secret_access_key),
            _create_variable('SNAPSHOT_KEY', redis.snapshot),
            _create_variable('SNAPSHOT_BUCKET', self.config.aws_snapshot_bucket),
            _create_variable('SNAPSHOT_PATH', self.config.snapshot_path)
        ]

    def _create_agent_env(self, redis: Redis) -> list:
        return [
            _create_variable('AWS_REGION', self.config.aws_region),
            _create_variable('AWS_ACCESS_KEY_ID', self.config.aws_access_key_id),
            _create_variable('AWS_SECRET_ACCESS_KEY', self.config.aws_secret_access_key),
            _create_variable('MR_SNAPSHOT_PATH', self.config.snapshot_path),
            _create_variable('MR_SNAPSHOTS_BUCKET', self.config.aws_snapshot_bucket),
            _create_variable('MR_CONFIG_PATH', self.config.config_path),
            _create_variable('MR_INSTANCE_ID', redis.instance_id),
            _create_variable('MR_NODE_NAME', redis.name),
            _create_variable('MR_NODE_ID', redis.node_id),
            _create_variable('MR_USER_ID', redis.user_id),
            _create_variable('MR_PLAN_ID', redis.plan_id),
        ]

    def _create_config(self, redis: Redis) -> str:
        return f'''maxmemory {redis.maxmemory}
maxclients {redis.maxclients}
databases {redis.databases}
requirepass {redis.requirepass}
dbfilename {self.config.db_filename}
rename-command SHUTDOWN {redis.shutdown}
rename-command CONFIG {redis.config}
rename-command SAVE {redis.save}
rename-command BGSAVE {redis.bgsave}
rename-command BGREWRITEAOF {redis.bgwriteaof}
rename-command MONITOR {redis.bgwriteaof + 'MONITOR'}
maxmemory-policy {redis.maxmemory_policy}
logfile {self.config.log_filename}
'''


def _create_variable(name: str, value: str) -> dict:
    return {
        'name': name,
        'value': value
    }


def _create_key(key: str, path: str) -> dict:
    return {
        'key': key,
        'path': path
    }


def _create_mount(name: str, mount_path: str) -> dict:
    return {
        'name': name,
        'mountPath': mount_path
    }
