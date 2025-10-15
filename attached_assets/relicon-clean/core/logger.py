"""
  Enterprise-grade structured JSON logging system.
  Implements ECS-compliant single-line JSON logging with trace correlation.
"""

import json
import logging
import sys
import time
import uuid
from datetime import datetime, timezone
from typing import Dict, Any, Optional
from contextvars import ContextVar


# Context variables for trace correlation
trace_context: ContextVar[str] = ContextVar('trace_id', default='')
transaction_context: ContextVar[str] = ContextVar('transaction_id', default='')


class StructuredJSONFormatter(logging.Formatter):
    """ECS-compliant JSON formatter for structured logging."""
    
    def __init__(self, service_name: str = "relicon", service_environment: str = "development"):
        super().__init__()
        self.service_name = service_name
        self.service_environment = service_environment
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record as single-line JSON."""
        
        # Base ECS structure
        log_entry = {
            "@timestamp": datetime.now(timezone.utc).isoformat(),
            "ecs.version": "8.11.0",
            "log.level": record.levelname.lower(),
            "log.severity": self._get_severity(record.levelno),
            "service.name": self.service_name,
            "service.environment": self.service_environment,
            "trace.id": trace_context.get() or self._generate_trace_id(),
            "transaction.id": transaction_context.get() or str(uuid.uuid4())[:8],
            "message": record.getMessage()
        }
        
        # Extract module and action from extra data (not direct record attributes)
        extra_data = getattr(record, 'extra_data', {})
        module_name = extra_data.get('module', record.name.split('.')[-1])
        action_name = extra_data.get('action', 'log')
        dataset_name = extra_data.get('dataset', f"{self.service_name}.{module_name}")
        
        log_entry.update({
            "event.module": module_name,
            "event.action": action_name,
            "event.dataset": dataset_name
        })
        
        # Add structured fields from extra data
        if 'extra_fields' in extra_data:
            log_entry.update(extra_data['extra_fields'])
        
        # Add exception info if present
        if record.exc_info:
            log_entry["error.message"] = str(record.exc_info[1])
            log_entry["error.type"] = record.exc_info[0].__name__
        
        return json.dumps(log_entry, separators=(',', ':'))
    
    def _get_severity(self, level: int) -> int:
        """Convert Python log level to numeric severity."""
        severity_map = {
            logging.DEBUG: 0,
            logging.INFO: 1,
            logging.WARNING: 2,
            logging.ERROR: 3,
            logging.CRITICAL: 4
        }
        return severity_map.get(level, 1)
    
    def _generate_trace_id(self) -> str:
        """Generate a new trace ID."""
        return str(uuid.uuid4())[:16]


class StructuredLogger:
    """Enterprise logging wrapper with domain-specific structured fields."""
    
    def __init__(self, name: str, service_name: str = "relicon"):
        self.logger = logging.getLogger(name)
        self.service_name = service_name
        
        # Configure logger if not already configured
        if not self.logger.handlers:
            handler = logging.StreamHandler(sys.stdout)
            formatter = StructuredJSONFormatter(service_name)
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.INFO)
    
    def _log(self, level: int, message: str, action: str = "log", **structured_fields):
        """Internal logging method with structured fields."""
        extra_data = {
            'module': self.logger.name.split('.')[-1],
            'action': action,
            'extra_fields': structured_fields
        }
        self.logger.log(level, message, extra={'extra_data': extra_data})
    
    def info(self, message: str, action: str = "info", **fields):
        """Log info message with structured fields."""
        self._log(logging.INFO, message, action, **fields)
    
    def debug(self, message: str, action: str = "debug", **fields):
        """Log debug message with structured fields."""
        self._log(logging.DEBUG, message, action, **fields)
    
    def warning(self, message: str, action: str = "warning", **fields):
        """Log warning message with structured fields."""
        self._log(logging.WARNING, message, action, **fields)
    
    def error(self, message: str, action: str = "error", **fields):
        """Log error message with structured fields."""
        self._log(logging.ERROR, message, action, **fields)
    
    def critical(self, message: str, action: str = "critical", **fields):
        """Log critical message with structured fields."""
        self._log(logging.CRITICAL, message, action, **fields)
    
    # Domain-specific logging methods
    def video_generation_start(self, job_id: str, provider: str, prompt_length: int):
        """Log video generation start."""
        self.info("Video generation started", "video.generation.start",
                  **{"video.job_id": job_id, "video.provider": provider, "video.prompt_length": prompt_length})
    
    def video_generation_complete(self, job_id: str, duration_s: float, cost: float, output_path: str):
        """Log video generation completion."""
        self.info("Video generation completed", "video.generation.complete",
                  **{"video.job_id": job_id, "video.duration_s": duration_s, "video.cost": cost, "video.output_path": output_path})
    
    def audio_processing_start(self, job_id: str, voice_provider: str, music_provider: str):
        """Log audio processing start."""
        self.info("Audio processing started", "audio.processing.start",
                  **{"audio.job_id": job_id, "audio.voice_provider": voice_provider, "audio.music_provider": music_provider})
    
    def audio_mixing_complete(self, job_id: str, voice_level_db: float, music_level_db: float, final_duration_s: float):
        """Log audio mixing completion."""
        self.info("Audio mixing completed", "audio.mixing.complete",
                  **{"audio.job_id": job_id, "audio.voice_level_db": voice_level_db, "audio.music_level_db": music_level_db, "audio.final_duration_s": final_duration_s})
    
    def cost_tracking_update(self, job_id: str, total_cost: float, breakdown: Dict[str, float]):
        """Log cost tracking update."""
        self.info("Cost tracking updated", "cost.tracking.update",
                  **{"cost.job_id": job_id, "cost.total": total_cost, "cost.breakdown": breakdown})
    
    def job_progress_update(self, job_id: str, progress_pct: int, status: str, current_step: str):
        """Log job progress update."""
        self.info("Job progress updated", "job.progress.update",
                  **{"job.id": job_id, "job.progress_pct": progress_pct, "job.status": status, "job.current_step": current_step})
    
    def assembly_timing_debug(self, job_id: str, target_duration_s: float, actual_duration_s: float, adjustment_applied: bool):
        """Log assembly timing debug info."""
        self.debug("Assembly timing debug", "assembly.timing.debug",
                   **{"assembly.job_id": job_id, "assembly.target_duration_s": target_duration_s, "assembly.actual_duration_s": actual_duration_s, "assembly.adjustment_applied": adjustment_applied})


def set_trace_context(trace_id: str, transaction_id: Optional[str] = None):
    """Set trace context for correlation."""
    trace_context.set(trace_id)
    if transaction_id:
        transaction_context.set(transaction_id)
    else:
        transaction_context.set(str(uuid.uuid4())[:8])


def get_logger(name: str, service_name: str = "relicon") -> StructuredLogger:
    """Get a structured logger instance."""
    return StructuredLogger(name, service_name)


# Pre-configured loggers for common components
video_logger = get_logger("video_service")
audio_logger = get_logger("audio_service") 
orchestrator_logger = get_logger("orchestrator")
assembly_logger = get_logger("assembly_service")
planning_logger = get_logger("planning_service")
