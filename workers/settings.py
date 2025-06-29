"""
Celery Worker Configuration Settings
Extends main settings for worker-specific configuration
"""
from config.settings import settings as base_settings
from celery import Celery


class WorkerSettings:
    """
    Worker-specific settings that extend the main application settings
    """
    
    # Celery Configuration
    CELERY_BROKER_URL = base_settings.redis_url
    CELERY_RESULT_BACKEND = base_settings.redis_result_backend
    
    # Task Configuration
    TASK_SERIALIZER = 'json'
    RESULT_SERIALIZER = 'json'
    ACCEPT_CONTENT = ['json']
    
    # Worker Configuration
    WORKER_PREFETCH_MULTIPLIER = 1
    WORKER_MAX_TASKS_PER_CHILD = 50  # Restart worker after 50 tasks to prevent memory leaks
    WORKER_DISABLE_RATE_LIMITS = False
    
    # Task Time Limits
    TASK_SOFT_TIME_LIMIT = base_settings.max_job_duration - 30  # 30 seconds before hard limit
    TASK_TIME_LIMIT = base_settings.max_job_duration
    
    # Retry Configuration
    TASK_DEFAULT_RETRY_DELAY = 60  # 1 minute
    TASK_MAX_RETRIES = 3
    TASK_ACKS_LATE = True
    
    # Queue Configuration
    TASK_DEFAULT_QUEUE = 'default'
    TASK_QUEUES = {
        'video_generation': {
            'exchange': 'video_generation',
            'exchange_type': 'direct',
            'routing_key': 'video_generation',
        },
        'maintenance': {
            'exchange': 'maintenance',
            'exchange_type': 'direct', 
            'routing_key': 'maintenance',
        },
        'health': {
            'exchange': 'health',
            'exchange_type': 'direct',
            'routing_key': 'health',
        }
    }
    
    # Monitoring Configuration
    WORKER_SEND_TASK_EVENTS = True
    TASK_SEND_SENT_EVENT = True
    TASK_TRACK_STARTED = True
    
    # Result Backend Configuration
    RESULT_EXPIRES = 3600  # Results expire after 1 hour
    RESULT_PERSISTENT = True
    
    # Security Configuration
    WORKER_HIJACK_ROOT_LOGGER = False
    WORKER_LOG_COLOR = base_settings.debug
    
    # Resource Limits
    CELERYD_MAX_MEMORY_PER_CHILD = 500000  # 500MB per worker child
    
    @classmethod
    def get_celery_config(cls) -> dict:
        """Get configuration dictionary for Celery"""
        return {
            'broker_url': cls.CELERY_BROKER_URL,
            'result_backend': cls.CELERY_RESULT_BACKEND,
            'task_serializer': cls.TASK_SERIALIZER,
            'result_serializer': cls.RESULT_SERIALIZER,
            'accept_content': cls.ACCEPT_CONTENT,
            'worker_prefetch_multiplier': cls.WORKER_PREFETCH_MULTIPLIER,
            'worker_max_tasks_per_child': cls.WORKER_MAX_TASKS_PER_CHILD,
            'task_soft_time_limit': cls.TASK_SOFT_TIME_LIMIT,
            'task_time_limit': cls.TASK_TIME_LIMIT,
            'task_default_retry_delay': cls.TASK_DEFAULT_RETRY_DELAY,
            'task_max_retries': cls.TASK_MAX_RETRIES,
            'task_acks_late': cls.TASK_ACKS_LATE,
            'worker_send_task_events': cls.WORKER_SEND_TASK_EVENTS,
            'task_send_sent_event': cls.TASK_SEND_SENT_EVENT,
            'task_track_started': cls.TASK_TRACK_STARTED,
            'result_expires': cls.RESULT_EXPIRES,
            'result_persistent': cls.RESULT_PERSISTENT,
            'worker_hijack_root_logger': cls.WORKER_HIJACK_ROOT_LOGGER,
            'worker_log_color': cls.WORKER_LOG_COLOR,
            'timezone': 'UTC',
            'enable_utc': True,
        }


# Export settings instance
worker_settings = WorkerSettings()

