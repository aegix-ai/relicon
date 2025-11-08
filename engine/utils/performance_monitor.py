"""
Performance monitoring utilities for Relicon backend
"""

import time
import psutil
import threading
from typing import Dict, Any, Optional
from collections import defaultdict, deque
import logging

logger = logging.getLogger("performance_monitor")

class PerformanceMonitor:
    """Real-time performance monitoring for the Relicon backend"""
    
    def __init__(self, history_size: int = 100):
        self.history_size = history_size
        self.metrics = {
            'cpu_usage': deque(maxlen=history_size),
            'memory_usage': deque(maxlen=history_size),
            'disk_usage': deque(maxlen=history_size),
            'active_jobs': deque(maxlen=history_size),
            'response_times': defaultdict(lambda: deque(maxlen=history_size)),
            'error_rates': defaultdict(lambda: deque(maxlen=history_size))
        }
        
        self.start_time = time.time()
        self.request_count = 0
        self.error_count = 0
        
        # Start monitoring thread
        self.monitoring = True
        self.monitor_thread = threading.Thread(target=self._monitor_system, daemon=True)
        self.monitor_thread.start()
        
        logger.info("Performance monitor initialized")
    
    def _monitor_system(self):
        """Background system monitoring"""
        while self.monitoring:
            try:
                # CPU usage
                cpu_percent = psutil.cpu_percent(interval=1)
                self.metrics['cpu_usage'].append({
                    'timestamp': time.time(),
                    'value': cpu_percent
                })
                
                # Memory usage
                memory = psutil.virtual_memory()
                self.metrics['memory_usage'].append({
                    'timestamp': time.time(),
                    'value': memory.percent,
                    'available_mb': memory.available / 1024 / 1024
                })
                
                # Disk usage
                disk = psutil.disk_usage('/')
                self.metrics['disk_usage'].append({
                    'timestamp': time.time(),
                    'value': disk.percent,
                    'free_gb': disk.free / 1024 / 1024 / 1024
                })
                
            except Exception as e:
                logger.error(f"System monitoring error: {e}")
            
            time.sleep(5)  # Monitor every 5 seconds
    
    def record_request(self, endpoint: str, response_time: float, success: bool = True):
        """Record API request metrics"""
        self.request_count += 1
        
        # Record response time
        self.metrics['response_times'][endpoint].append({
            'timestamp': time.time(),
            'value': response_time
        })
        
        # Record error rate
        if not success:
            self.error_count += 1
        
        error_rate = (self.error_count / self.request_count) * 100
        self.metrics['error_rates'][endpoint].append({
            'timestamp': time.time(),
            'value': error_rate
        })
    
    def record_job_count(self, active_jobs: int):
        """Record active job count"""
        self.metrics['active_jobs'].append({
            'timestamp': time.time(),
            'value': active_jobs
        })
    
    def get_current_metrics(self) -> Dict[str, Any]:
        """Get current performance metrics"""
        uptime = time.time() - self.start_time
        
        # Get latest values
        latest_cpu = self.metrics['cpu_usage'][-1]['value'] if self.metrics['cpu_usage'] else 0
        latest_memory = self.metrics['memory_usage'][-1] if self.metrics['memory_usage'] else {'value': 0, 'available_mb': 0}
        latest_disk = self.metrics['disk_usage'][-1] if self.metrics['disk_usage'] else {'value': 0, 'free_gb': 0}
        latest_jobs = self.metrics['active_jobs'][-1]['value'] if self.metrics['active_jobs'] else 0
        
        # Calculate averages
        avg_response_time = self._calculate_average_response_time()
        current_error_rate = (self.error_count / max(1, self.request_count)) * 100
        
        return {
            'timestamp': time.time(),
            'uptime_seconds': uptime,
            'system': {
                'cpu_percent': latest_cpu,
                'memory_percent': latest_memory['value'],
                'memory_available_mb': latest_memory.get('available_mb', 0),
                'disk_percent': latest_disk['value'],
                'disk_free_gb': latest_disk.get('free_gb', 0)
            },
            'application': {
                'active_jobs': latest_jobs,
                'total_requests': self.request_count,
                'total_errors': self.error_count,
                'error_rate_percent': current_error_rate,
                'average_response_time_ms': avg_response_time
            },
            'health_status': self._determine_health_status(latest_cpu, latest_memory['value'], current_error_rate)
        }
    
    def _calculate_average_response_time(self) -> float:
        """Calculate average response time across all endpoints"""
        all_times = []
        for endpoint_times in self.metrics['response_times'].values():
            all_times.extend([entry['value'] for entry in endpoint_times])
        
        return sum(all_times) / len(all_times) * 1000 if all_times else 0  # Convert to ms
    
    def _determine_health_status(self, cpu: float, memory: float, error_rate: float) -> str:
        """Determine overall health status"""
        if cpu > 90 or memory > 90 or error_rate > 10:
            return 'critical'
        elif cpu > 70 or memory > 70 or error_rate > 5:
            return 'warning'
        else:
            return 'healthy'
    
    def get_historical_data(self, metric: str, minutes: int = 10) -> list:
        """Get historical data for a specific metric"""
        cutoff_time = time.time() - (minutes * 60)
        
        if metric in self.metrics:
            return [
                entry for entry in self.metrics[metric]
                if entry['timestamp'] > cutoff_time
            ]
        
        return []
    
    def get_endpoint_stats(self) -> Dict[str, Any]:
        """Get per-endpoint statistics"""
        stats = {}
        
        for endpoint in self.metrics['response_times']:
            times = [entry['value'] for entry in self.metrics['response_times'][endpoint]]
            errors = [entry['value'] for entry in self.metrics['error_rates'][endpoint]]
            
            if times:
                stats[endpoint] = {
                    'request_count': len(times),
                    'avg_response_time_ms': (sum(times) / len(times)) * 1000,
                    'min_response_time_ms': min(times) * 1000,
                    'max_response_time_ms': max(times) * 1000,
                    'current_error_rate': errors[-1] if errors else 0
                }
        
        return stats
    
    def generate_alert(self, threshold_cpu: float = 85, threshold_memory: float = 85, threshold_error_rate: float = 5) -> Optional[Dict[str, Any]]:
        """Generate alert if thresholds are exceeded"""
        current = self.get_current_metrics()
        alerts = []
        
        if current['system']['cpu_percent'] > threshold_cpu:
            alerts.append({
                'type': 'high_cpu',
                'message': f"CPU usage is {current['system']['cpu_percent']:.1f}%",
                'severity': 'warning' if current['system']['cpu_percent'] < 95 else 'critical'
            })
        
        if current['system']['memory_percent'] > threshold_memory:
            alerts.append({
                'type': 'high_memory',
                'message': f"Memory usage is {current['system']['memory_percent']:.1f}%",
                'severity': 'warning' if current['system']['memory_percent'] < 95 else 'critical'
            })
        
        if current['application']['error_rate_percent'] > threshold_error_rate:
            alerts.append({
                'type': 'high_error_rate',
                'message': f"Error rate is {current['application']['error_rate_percent']:.1f}%",
                'severity': 'critical'
            })
        
        if alerts:
            return {
                'timestamp': time.time(),
                'alerts': alerts,
                'system_status': current['health_status']
            }
        
        return None
    
    def shutdown(self):
        """Shutdown the performance monitor"""
        self.monitoring = False
        if self.monitor_thread.is_alive():
            self.monitor_thread.join(timeout=5)
        logger.info("Performance monitor shutdown")

# Global instance
performance_monitor = PerformanceMonitor()

# Decorator for automatic request timing
def monitor_performance(endpoint_name: str):
    """Decorator to automatically monitor endpoint performance"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            start_time = time.time()
            success = True
            
            try:
                result = func(*args, **kwargs)
                return result
            except Exception as e:
                success = False
                raise
            finally:
                response_time = time.time() - start_time
                performance_monitor.record_request(endpoint_name, response_time, success)
        
        return wrapper
    return decorator
