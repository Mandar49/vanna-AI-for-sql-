"""
Executive Intelligence Layer - Scheduler (Phase 3A)
Offline scheduler for automated report generation.
Uses only built-in threading and time modules.
"""

import threading
import time
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Callable, Dict, Optional, List
import os


# Global job registry
JOBS: Dict[int, Dict] = {}
JOB_COUNTER = 0
JOBS_LOCK = threading.Lock()

# Setup logging
LOG_DIR = "./reports"
Path(LOG_DIR).mkdir(parents=True, exist_ok=True)
LOG_FILE = os.path.join(LOG_DIR, "scheduler.log")

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


def _get_next_job_id() -> int:
    """Generate unique job ID."""
    global JOB_COUNTER
    with JOBS_LOCK:
        JOB_COUNTER += 1
        return JOB_COUNTER


def _calculate_next_run_interval(minutes: int) -> datetime:
    """Calculate next run time for interval-based job."""
    return datetime.now() + timedelta(minutes=minutes)


def _calculate_next_run_daily(hour: int, minute: int) -> datetime:
    """Calculate next run time for daily job."""
    now = datetime.now()
    next_run = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
    
    # If time has passed today, schedule for tomorrow
    if next_run <= now:
        next_run += timedelta(days=1)
    
    return next_run


def _job_loop_interval(job_id: int, minutes: int, job_fn: Callable):
    """
    Background loop for interval-based jobs.
    Checks every 30 seconds if it's time to run.
    """
    logger.info(f"Job {job_id} started (interval: {minutes} minutes)")
    
    while True:
        with JOBS_LOCK:
            if job_id not in JOBS or JOBS[job_id].get('cancelled', False):
                logger.info(f"Job {job_id} cancelled, stopping loop")
                break
            
            job = JOBS[job_id]
        
        # Check if it's time to run
        now = datetime.now()
        if now >= job['next_run']:
            try:
                logger.info(f"Job {job_id} executing: {job_fn.__name__}")
                job_fn()
                logger.info(f"Job {job_id} completed successfully")
            except Exception as e:
                logger.error(f"Job {job_id} failed: {str(e)}")
            
            # Schedule next run
            with JOBS_LOCK:
                if job_id in JOBS:
                    JOBS[job_id]['next_run'] = _calculate_next_run_interval(minutes)
                    JOBS[job_id]['last_run'] = now
        
        # Sleep for 30 seconds before next check
        time.sleep(30)


def _job_loop_daily(job_id: int, hour: int, minute: int, job_fn: Callable):
    """
    Background loop for daily jobs.
    Checks every 30 seconds if it's time to run.
    """
    logger.info(f"Job {job_id} started (daily at {hour:02d}:{minute:02d})")
    
    while True:
        with JOBS_LOCK:
            if job_id not in JOBS or JOBS[job_id].get('cancelled', False):
                logger.info(f"Job {job_id} cancelled, stopping loop")
                break
            
            job = JOBS[job_id]
        
        # Check if it's time to run
        now = datetime.now()
        if now >= job['next_run']:
            try:
                logger.info(f"Job {job_id} executing: {job_fn.__name__}")
                job_fn()
                logger.info(f"Job {job_id} completed successfully")
            except Exception as e:
                logger.error(f"Job {job_id} failed: {str(e)}")
            
            # Schedule next run (tomorrow at same time)
            with JOBS_LOCK:
                if job_id in JOBS:
                    JOBS[job_id]['next_run'] = _calculate_next_run_daily(hour, minute)
                    JOBS[job_id]['last_run'] = now
        
        # Sleep for 30 seconds before next check
        time.sleep(30)


def schedule_interval(minutes: int, job_fn: Callable) -> int:
    """
    Schedule a job to run at regular intervals.
    
    Args:
        minutes: Interval in minutes between runs
        job_fn: Function to execute (should take no arguments)
        
    Returns:
        Job handle (ID) for cancellation
        
    Example:
        def my_job():
            print("Running job")
        
        handle = schedule_interval(60, my_job)  # Run every hour
    """
    job_id = _get_next_job_id()
    next_run = _calculate_next_run_interval(minutes)
    
    # Create job entry
    job_info = {
        'id': job_id,
        'type': 'interval',
        'minutes': minutes,
        'function': job_fn.__name__,
        'next_run': next_run,
        'last_run': None,
        'cancelled': False,
        'thread': None
    }
    
    # Start background thread
    thread = threading.Thread(
        target=_job_loop_interval,
        args=(job_id, minutes, job_fn),
        daemon=True,
        name=f"Job-{job_id}-{job_fn.__name__}"
    )
    job_info['thread'] = thread
    
    with JOBS_LOCK:
        JOBS[job_id] = job_info
    
    thread.start()
    logger.info(f"Scheduled interval job {job_id}: {job_fn.__name__} every {minutes} minutes")
    
    return job_id


def schedule_daily(hour: int, minute: int, job_fn: Callable) -> int:
    """
    Schedule a job to run daily at a specific time.
    
    Args:
        hour: Hour (0-23)
        minute: Minute (0-59)
        job_fn: Function to execute (should take no arguments)
        
    Returns:
        Job handle (ID) for cancellation
        
    Example:
        def daily_report():
            print("Generating daily report")
        
        handle = schedule_daily(9, 0, daily_report)  # Run at 9:00 AM daily
    """
    if not (0 <= hour <= 23):
        raise ValueError("Hour must be between 0 and 23")
    if not (0 <= minute <= 59):
        raise ValueError("Minute must be between 0 and 59")
    
    job_id = _get_next_job_id()
    next_run = _calculate_next_run_daily(hour, minute)
    
    # Create job entry
    job_info = {
        'id': job_id,
        'type': 'daily',
        'hour': hour,
        'minute': minute,
        'function': job_fn.__name__,
        'next_run': next_run,
        'last_run': None,
        'cancelled': False,
        'thread': None
    }
    
    # Start background thread
    thread = threading.Thread(
        target=_job_loop_daily,
        args=(job_id, hour, minute, job_fn),
        daemon=True,
        name=f"Job-{job_id}-{job_fn.__name__}"
    )
    job_info['thread'] = thread
    
    with JOBS_LOCK:
        JOBS[job_id] = job_info
    
    thread.start()
    logger.info(f"Scheduled daily job {job_id}: {job_fn.__name__} at {hour:02d}:{minute:02d}")
    
    return job_id


def cancel(handle: int) -> bool:
    """
    Cancel a scheduled job.
    
    Args:
        handle: Job ID returned by schedule_interval or schedule_daily
        
    Returns:
        True if job was cancelled, False if job not found
        
    Example:
        handle = schedule_interval(60, my_job)
        cancel(handle)  # Stop the job
    """
    with JOBS_LOCK:
        if handle not in JOBS:
            logger.warning(f"Cannot cancel job {handle}: not found")
            return False
        
        JOBS[handle]['cancelled'] = True
        job_name = JOBS[handle]['function']
        logger.info(f"Cancelled job {handle}: {job_name}")
        
        # Remove from registry after marking as cancelled
        # Thread will stop on next check
        del JOBS[handle]
    
    return True


def list_jobs() -> List[Dict]:
    """
    List all active scheduled jobs.
    
    Returns:
        List of job information dictionaries
        
    Example:
        jobs = list_jobs()
        for job in jobs:
            print(f"Job {job['id']}: {job['function']} - next run: {job['next_run']}")
    """
    with JOBS_LOCK:
        jobs = []
        for job_id, job_info in JOBS.items():
            jobs.append({
                'id': job_info['id'],
                'type': job_info['type'],
                'function': job_info['function'],
                'next_run': job_info['next_run'],
                'last_run': job_info['last_run'],
                'details': {
                    'minutes': job_info.get('minutes'),
                    'hour': job_info.get('hour'),
                    'minute': job_info.get('minute')
                }
            })
        return jobs


def daily_kpi_summary():
    """
    Default job: Generate daily KPI summary report.
    This is a placeholder that will be enhanced with actual report generation.
    """
    logger.info("Daily KPI Summary triggered")
    
    # Create daily reports directory
    daily_dir = "./reports/daily"
    Path(daily_dir).mkdir(parents=True, exist_ok=True)
    
    # Generate report filename
    date_str = datetime.now().strftime("%Y%m%d")
    report_path = os.path.join(daily_dir, f"{date_str}_summary.md")
    
    # Create simple summary report
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    content = f"""# Daily KPI Summary

**Generated:** {timestamp}

## Overview

This is an automated daily summary report.

## Key Metrics

- Report Generation: Successful
- Timestamp: {timestamp}
- Status: Operational

## Next Steps

1. Review daily metrics
2. Check for anomalies
3. Update stakeholders

---

*This report was automatically generated by the Executive Intelligence Layer Scheduler.*
"""
    
    # Save report
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    logger.info(f"Daily KPI Summary saved to: {report_path}")
    print(f"✓ Daily KPI Summary generated: {report_path}")


if __name__ == "__main__":
    print("="*70)
    print("SCHEDULER TEST")
    print("="*70)
    print()
    
    # Test interval job
    print("1. Testing interval job (runs every 1 minute)...")
    
    def test_job():
        print(f"  → Test job executed at {datetime.now().strftime('%H:%M:%S')}")
    
    handle1 = schedule_interval(1, test_job)
    print(f"   Scheduled job {handle1}")
    
    # Test daily job
    print("\n2. Testing daily job (scheduled for tomorrow)...")
    handle2 = schedule_daily(9, 0, daily_kpi_summary)
    print(f"   Scheduled job {handle2}")
    
    # List jobs
    print("\n3. Active jobs:")
    jobs = list_jobs()
    for job in jobs:
        print(f"   Job {job['id']}: {job['function']}")
        print(f"      Type: {job['type']}")
        print(f"      Next run: {job['next_run']}")
    
    # Wait a bit
    print("\n4. Waiting 90 seconds to see interval job run...")
    time.sleep(90)
    
    # Cancel jobs
    print("\n5. Cancelling jobs...")
    cancel(handle1)
    cancel(handle2)
    
    print("\n" + "="*70)
    print("✅ Scheduler ready")
    print("="*70)
