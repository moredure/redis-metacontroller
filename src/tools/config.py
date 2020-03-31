class Config:
    def __init__(self, env: dict):
        self.db_filename = 'dump.rdb'
        self.data_volume = 'data'
        self.volume_path = '/data'
        self.log_filename = f'{self.volume_path}/redis.log'
        self.config_path = f'{self.volume_path}/redis.conf'
        self.snapshot_path = f'{self.volume_path}/{self.db_filename}'

        self.redis_port = 6379
        self.agent_port = 80

        self.storage_class = env.get('STORAGE_CLASS', 'standard')

        self.redis_image = env.get('MR_REDIS_IMAGE', 'redis:5-alpine')
        self.redis_command = env.get('MR_REDIS_COMMAND', 'redis-server')
        self.agent_image = env.get('MR_AGENT_IMAGE')
        self.agent_memory = env.get('MR_AGENT_MEMORY', '25Mi')

        self.migrator_image = env.get('MR_MIGRATOR_IMAGE')
        self.initializer_image = env.get('MR_INITIALIZER_IMAGE')

        self.aws_access_key_id = env.get('AWS_ACCESS_KEY_ID')
        self.aws_secret_access_key = env.get('AWS_SECRET_KEY')
        self.aws_region = env.get('AWS_REGION')
        self.aws_snapshot_bucket = env.get('AWS_SNAPSHOT_BUCKET')

        self.private_image_registry = env.get('PRIVATE_IMAGE_REGISTRY')

        self.port = int(env.get('PORT', '3000'))

    @property
    def address(self) -> tuple:
        return '', self.port
