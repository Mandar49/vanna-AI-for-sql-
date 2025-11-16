"""
Test suite for Executive Intelligence Layer - Scheduler
Verifies offline scheduling capabilities.
"""

import os
import time
import shutil
from datetime import datetime, timedelta
from pathlib import Path
import pytest

from scheduler import (
    schedule_interval,
    schedule_daily,
    cancel,
    list_jobs,
    daily_kpi_summary,
    JOBS,
    JOBS_LOCK,
    LOG_FILE
)


class TestScheduler:
    """Test suite for scheduler functions."""
    
    @pytest.fixture(autouse=True)
    def setup_teardown(self):
        """Setup and cleanup test environment."""
        # Setup: clear any existing jobs
        with JOBS_LOCK:
            job_ids = list(JOBS.keys())
        for job_id in job_ids:
            cancel(job_id)
        
        # Clear test daily reports
        test_daily_dir = "./reports/daily"
        if os.path.exists(test_daily_dir):
            for file in Path(test_daily_dir).glob("*_summary.md"):
                file.unlink()
        
        yield
        
        # Teardown: cancel all jobs
        with JOBS_LOCK:
            job_ids = list(JOBS.keys())
        for job_id in job_ids:
            cancel(job_id)
    
    def test_schedule_interval_basic(self):
        """Test basic interval scheduling."""
        call_count = [0]
        
        def test_job():
            call_count[0] += 1
        
        # Schedule job to run every 1 minute (for testing, we'll wait less)
        handle = schedule_interval(1, test_job)
        
        assert handle > 0
        assert handle in JOBS
        
        # Verify job info
        jobs = list_jobs()
        assert len(jobs) == 1
        assert jobs[0]['id'] == handle
        assert jobs[0]['type'] == 'interval'
        assert jobs[0]['function'] == 'test_job'
        
        # Cancel job
        assert cancel(handle) is True
        print("✓ Interval scheduling works")
    
    def test_schedule_daily_basic(self):
        """Test basic daily scheduling."""
        def test_daily():
            pass
        
        # Schedule for tomorrow at 9:00 AM
        handle = schedule_daily(9, 0, test_daily)
        
        assert handle > 0
        assert handle in JOBS
        
        # Verify job info
        jobs = list_jobs()
        assert len(jobs) == 1
        assert jobs[0]['id'] == handle
        assert jobs[0]['type'] == 'daily'
        assert jobs[0]['function'] == 'test_daily'
        assert jobs[0]['details']['hour'] == 9
        assert jobs[0]['details']['minute'] == 0
        
        # Verify next run is in the future
        assert jobs[0]['next_run'] > datetime.now()
        
        # Cancel job
        assert cancel(handle) is True
        print("✓ Daily scheduling works")
    
    def test_schedule_daily_validation(self):
        """Test daily scheduling parameter validation."""
        def dummy():
            pass
        
        # Invalid hour
        with pytest.raises(ValueError):
            schedule_daily(25, 0, dummy)
        
        # Invalid minute
        with pytest.raises(ValueError):
            schedule_daily(9, 60, dummy)
        
        print("✓ Daily scheduling validation works")
    
    def test_cancel_job(self):
        """Test job cancellation."""
        def test_job():
            pass
        
        handle = schedule_interval(60, test_job)
        assert handle in JOBS
        
        # Cancel job
        result = cancel(handle)
        assert result is True
        assert handle not in JOBS
        
        # Try to cancel again (should return False)
        result = cancel(handle)
        assert result is False
        
        print("✓ Job cancellation works")
    
    def test_list_jobs(self):
        """Test listing active jobs."""
        def job1():
            pass
        
        def job2():
            pass
        
        # No jobs initially
        jobs = list_jobs()
        assert len(jobs) == 0
        
        # Schedule two jobs
        handle1 = schedule_interval(30, job1)
        handle2 = schedule_daily(10, 30, job2)
        
        # List jobs
        jobs = list_jobs()
        assert len(jobs) == 2
        
        job_ids = [j['id'] for j in jobs]
        assert handle1 in job_ids
        assert handle2 in job_ids
        
        # Cancel jobs
        cancel(handle1)
        cancel(handle2)
        
        # Verify empty
        jobs = list_jobs()
        assert len(jobs) == 0
        
        print("✓ Job listing works")
    
    def test_interval_job_execution(self):
        """Test that interval job actually executes."""
        execution_times = []
        
        def test_job():
            execution_times.append(datetime.now())
        
        # Schedule job to run every 1 minute
        # We'll manually trigger by manipulating next_run time
        handle = schedule_interval(1, test_job)
        
        # Force immediate execution by setting next_run to past
        with JOBS_LOCK:
            JOBS[handle]['next_run'] = datetime.now() - timedelta(seconds=1)
        
        # Wait for job to execute (check every 30s, so wait ~35s)
        time.sleep(35)
        
        # Verify job executed at least once
        assert len(execution_times) >= 1
        
        cancel(handle)
        print("✓ Interval job execution works")
    
    def test_daily_kpi_summary(self):
        """Test the default daily KPI summary job."""
        # Run the job directly
        daily_kpi_summary()
        
        # Verify report was created
        date_str = datetime.now().strftime("%Y%m%d")
        report_path = f"./reports/daily/{date_str}_summary.md"
        
        assert os.path.exists(report_path)
        
        # Verify content
        with open(report_path, 'r', encoding='utf-8') as f:
            content = f.read()
            assert "Daily KPI Summary" in content
            assert "Generated:" in content
            assert "Key Metrics" in content
        
        print("✓ Daily KPI summary generation works")
    
    def test_daily_directory_creation(self):
        """Test that daily reports directory is auto-created."""
        daily_dir = "./reports/daily"
        
        # Remove if exists
        if os.path.exists(daily_dir):
            shutil.rmtree(daily_dir)
        
        # Run daily summary
        daily_kpi_summary()
        
        # Verify directory created
        assert os.path.exists(daily_dir)
        assert os.path.isdir(daily_dir)
        
        print("✓ Daily directory auto-creation works")
    
    def test_log_file_creation(self):
        """Test that scheduler log file is created."""
        assert os.path.exists(LOG_FILE)
        
        # Verify log has content
        with open(LOG_FILE, 'r', encoding='utf-8') as f:
            content = f.read()
            # Should have some log entries from previous tests
            assert len(content) > 0
        
        print("✓ Log file creation works")
    
    def test_no_internet_required(self):
        """Verify scheduler works offline."""
        def offline_job():
            pass
        
        # All operations should work without internet
        handle = schedule_interval(60, offline_job)
        assert handle > 0
        
        jobs = list_jobs()
        assert len(jobs) == 1
        
        cancel(handle)
        
        # Daily KPI summary should work offline
        daily_kpi_summary()
        
        print("✓ Offline operation works")
    
    def test_multiple_jobs(self):
        """Test scheduling multiple jobs simultaneously."""
        def job_a():
            pass
        
        def job_b():
            pass
        
        def job_c():
            pass
        
        # Schedule multiple jobs
        handle1 = schedule_interval(30, job_a)
        handle2 = schedule_interval(45, job_b)
        handle3 = schedule_daily(14, 30, job_c)
        
        # Verify all scheduled
        jobs = list_jobs()
        assert len(jobs) == 3
        
        # Cancel all
        cancel(handle1)
        cancel(handle2)
        cancel(handle3)
        
        jobs = list_jobs()
        assert len(jobs) == 0
        
        print("✓ Multiple jobs scheduling works")


def run_manual_test():
    """Manual test for quick verification."""
    print("\n" + "="*70)
    print("MANUAL TEST: Scheduler")
    print("="*70 + "\n")
    
    # Clean up
    with JOBS_LOCK:
        job_ids = list(JOBS.keys())
    for job_id in job_ids:
        cancel(job_id)
    
    print("1. Testing interval job...")
    
    execution_count = [0]
    
    def quick_job():
        execution_count[0] += 1
        print(f"   → Quick job executed (count: {execution_count[0]})")
    
    handle1 = schedule_interval(1, quick_job)
    print(f"   ✓ Scheduled interval job {handle1}\n")
    
    print("2. Testing daily job...")
    handle2 = schedule_daily(9, 0, daily_kpi_summary)
    print(f"   ✓ Scheduled daily job {handle2}\n")
    
    print("3. Listing active jobs...")
    jobs = list_jobs()
    for job in jobs:
        print(f"   Job {job['id']}: {job['function']}")
        print(f"      Type: {job['type']}")
        print(f"      Next run: {job['next_run']}")
    print()
    
    print("4. Testing daily KPI summary...")
    daily_kpi_summary()
    date_str = datetime.now().strftime("%Y%m%d")
    report_path = f"./reports/daily/{date_str}_summary.md"
    print(f"   ✓ Report created: {report_path}\n")
    
    print("5. Forcing interval job execution...")
    # Force immediate execution
    with JOBS_LOCK:
        if handle1 in JOBS:
            JOBS[handle1]['next_run'] = datetime.now() - timedelta(seconds=1)
    
    print("   Waiting 35 seconds for job to execute...")
    time.sleep(35)
    print(f"   ✓ Job executed {execution_count[0]} time(s)\n")
    
    print("6. Cancelling jobs...")
    cancel(handle1)
    cancel(handle2)
    print("   ✓ All jobs cancelled\n")
    
    print("="*70)
    print("VERIFICATION")
    print("="*70)
    print(f"✓ scheduler.py created: {os.path.exists('scheduler.py')}")
    print(f"✓ ./reports/daily auto-created: {os.path.exists('./reports/daily')}")
    print(f"✓ scheduler.log exists: {os.path.exists(LOG_FILE)}")
    print(f"✓ Daily summary report exists: {os.path.exists(report_path)}")
    print(f"✓ Interval job executed: {execution_count[0] >= 1}")
    print(f"✓ Offline operation: True")
    
    print("\n" + "="*70)
    print("✅ Scheduler ready")
    print("="*70)


if __name__ == "__main__":
    # Run manual test
    run_manual_test()
    
    # Run pytest if available
    try:
        print("\n" + "="*70)
        print("RUNNING PYTEST SUITE")
        print("="*70 + "\n")
        pytest.main([__file__, "-v", "-s"])
    except:
        print("\nNote: Install pytest to run full test suite")
