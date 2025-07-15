#!/usr/bin/env python3
"""
Cleanup script for Relicon AI Video Generation Platform
Removes temporary files, old outputs, and optimizes storage
"""
import os
import shutil
import time
from pathlib import Path
from datetime import datetime, timedelta
from config.settings import settings

class ReliconCleanup:
    """Cleanup utility for Relicon system"""
    
    def __init__(self):
        self.temp_dir = Path(settings.TEMP_DIR)
        self.output_dir = Path(settings.OUTPUT_DIR)
        self.assets_dir = Path(settings.ASSETS_DIR)
        self.max_age_days = 7  # Keep files for 7 days
    
    def cleanup_temp_files(self):
        """Remove temporary files"""
        print("Cleaning up temporary files...")
        
        if self.temp_dir.exists():
            temp_files = list(self.temp_dir.glob("*"))
            for file_path in temp_files:
                try:
                    if file_path.is_file():
                        os.remove(file_path)
                    elif file_path.is_dir():
                        shutil.rmtree(file_path)
                except Exception as e:
                    print(f"Warning: Could not remove {file_path}: {e}")
            
            print(f"✓ Cleaned up {len(temp_files)} temporary files")
        else:
            print("✓ No temporary files to clean")
    
    def cleanup_old_outputs(self):
        """Remove old output videos"""
        print("Cleaning up old output videos...")
        
        if not self.output_dir.exists():
            print("✓ No output directory to clean")
            return
        
        cutoff_time = datetime.now() - timedelta(days=self.max_age_days)
        removed_count = 0
        
        for file_path in self.output_dir.glob("*.mp4"):
            try:
                file_time = datetime.fromtimestamp(file_path.stat().st_mtime)
                if file_time < cutoff_time:
                    os.remove(file_path)
                    removed_count += 1
            except Exception as e:
                print(f"Warning: Could not process {file_path}: {e}")
        
        print(f"✓ Removed {removed_count} old output videos")
    
    def cleanup_audio_files(self):
        """Remove temporary audio files"""
        print("Cleaning up temporary audio files...")
        
        audio_extensions = ['.mp3', '.wav', '.m4a']
        removed_count = 0
        
        # Check temp directory
        if self.temp_dir.exists():
            for ext in audio_extensions:
                for file_path in self.temp_dir.glob(f"*{ext}"):
                    try:
                        os.remove(file_path)
                        removed_count += 1
                    except Exception as e:
                        print(f"Warning: Could not remove {file_path}: {e}")
        
        # Check system temp directory
        system_temp = Path("/tmp")
        if system_temp.exists():
            for ext in audio_extensions:
                for file_path in system_temp.glob(f"tmp*{ext}"):
                    try:
                        # Only remove files older than 1 hour
                        file_time = datetime.fromtimestamp(file_path.stat().st_mtime)
                        if datetime.now() - file_time > timedelta(hours=1):
                            os.remove(file_path)
                            removed_count += 1
                    except Exception as e:
                        continue  # Skip files we can't access
        
        print(f"✓ Removed {removed_count} temporary audio files")
    
    def optimize_storage(self):
        """Optimize storage usage"""
        print("Optimizing storage usage...")
        
        # Get storage usage
        total_size = 0
        file_count = 0
        
        for directory in [self.temp_dir, self.output_dir, self.assets_dir]:
            if directory.exists():
                for file_path in directory.rglob("*"):
                    if file_path.is_file():
                        total_size += file_path.stat().st_size
                        file_count += 1
        
        # Convert to MB
        size_mb = total_size / (1024 * 1024)
        
        print(f"✓ Total storage usage: {size_mb:.2f} MB ({file_count} files)")
        
        # Warn if storage is getting large
        if size_mb > 1000:  # 1GB
            print("⚠ Warning: Storage usage is high, consider manual cleanup")
    
    def cleanup_logs(self):
        """Remove old log files"""
        print("Cleaning up old log files...")
        
        log_files = [
            Path("server.log"),
            Path("error.log"),
            Path("debug.log")
        ]
        
        removed_count = 0
        for log_file in log_files:
            if log_file.exists():
                try:
                    # Keep only last 100KB of log
                    if log_file.stat().st_size > 100 * 1024:
                        with open(log_file, 'r') as f:
                            lines = f.readlines()
                        
                        # Keep last 1000 lines
                        with open(log_file, 'w') as f:
                            f.writelines(lines[-1000:])
                        
                        removed_count += 1
                except Exception as e:
                    print(f"Warning: Could not process {log_file}: {e}")
        
        print(f"✓ Optimized {removed_count} log files")
    
    def run_full_cleanup(self):
        """Run complete cleanup process"""
        print("Starting Relicon cleanup process...")
        print(f"Timestamp: {datetime.now().isoformat()}")
        print("-" * 50)
        
        try:
            self.cleanup_temp_files()
            self.cleanup_old_outputs()
            self.cleanup_audio_files()
            self.cleanup_logs()
            self.optimize_storage()
            
            print("-" * 50)
            print("✅ Cleanup completed successfully!")
            
        except Exception as e:
            print(f"❌ Cleanup failed: {e}")
            return False
        
        return True

if __name__ == "__main__":
    cleanup = ReliconCleanup()
    cleanup.run_full_cleanup()