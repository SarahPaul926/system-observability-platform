"""
stress_test.py
==============

SQLite concurrency test for the HELIOS telemetry database.

This test checks whether multiple Python threads can
write telemetry data to SQLite at the same time.

Tests:
    1 thread
    5 threads
    10 threads
    20 threads
    50 threads
"""

import threading
import time

from database.database import (
    create_Table,
    save_metric,
    get_connection
)


# ---------------------------------------------------------
# TEST CONFIGURATION
# ---------------------------------------------------------

THREAD_COUNTS = [1, 5, 10, 20, 50]


# ---------------------------------------------------------
# SHARED TEST COUNTERS
# ---------------------------------------------------------

success = 0
failed = 0

# Lock protects the success/failed counters
counter_lock = threading.Lock()


# ---------------------------------------------------------
# CREATE TEST TELEMETRY
# ---------------------------------------------------------

def create_test_metric(thread_id):

    return {
        "time": time.time(),

        "cpu": {
            "cpu_usage": 50.0 + thread_id
        },

        "ram": {
            "percent": 40.0 + thread_id
        },

        "disk": {
            "disk_usage": 30.0
        },

        "network_activity": {
            "network_sent": 100 + thread_id,
            "network_received": 200 + thread_id
        }
    }


# ---------------------------------------------------------
# GET CURRENT DATABASE ROW COUNT
# ---------------------------------------------------------

def get_record_count():

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute(
        "SELECT COUNT(*) FROM telemetry"
    )

    count = cursor.fetchone()[0]

    cursor.close()
    conn.close()

    return count


# ---------------------------------------------------------
# WORKER THREAD
# ---------------------------------------------------------

def worker(thread_id):

    global success
    global failed

    try:

        # Create fake telemetry
        metric = create_test_metric(thread_id)

        # No anomaly
        anomaly = 0

        # Save telemetry to SQLite
        save_metric(metric, anomaly)

        # Safely update success counter
        with counter_lock:
            success += 1

        print(
            f"Thread {thread_id}: SUCCESS"
        )

    except Exception as e:

        # Safely update failed counter
        with counter_lock:
            failed += 1

        print(
            f"Thread {thread_id}: FAILED -> {e}"
        )


# ---------------------------------------------------------
# RUN ONE CONCURRENCY TEST
# ---------------------------------------------------------

def run_test(number_of_threads):

    global success
    global failed

    # Reset counters
    success = 0
    failed = 0

    threads = []

    # Check database BEFORE test
    records_before = get_record_count()

    print()
    print("================================")
    print(
        f"Starting test with {number_of_threads} threads"
    )
    print(
        f"Records before: {records_before}"
    )
    print("================================")

    # Start timer
    start_time = time.time()

    # -----------------------------------------------------
    # CREATE AND START THREADS
    # -----------------------------------------------------

    for i in range(number_of_threads):

        thread = threading.Thread(
            target=worker,
            args=(i,),
            name=f"TelemetryThread-{i}"
        )

        threads.append(thread)

        thread.start()

    # -----------------------------------------------------
    # WAIT FOR ALL THREADS
    # -----------------------------------------------------

    for thread in threads:

        thread.join()

    # Stop timer
    end_time = time.time()

    elapsed = end_time - start_time

    # Check database AFTER test
    records_after = get_record_count()

    records_added = records_after - records_before

    # -----------------------------------------------------
    # RESULTS
    # -----------------------------------------------------

    print()
    print("--------------------------------")
    print(
        f"Threads       : {number_of_threads}"
    )
    print(
        f"Success       : {success}"
    )
    print(
        f"Failed        : {failed}"
    )
    print(
        f"Records added : {records_added}"
    )
    print(
        f"Records after : {records_after}"
    )
    print(
        f"Time          : {elapsed:.4f} seconds"
    )
    print("--------------------------------")

    # -----------------------------------------------------
    # VERIFY RESULT
    # -----------------------------------------------------

    if success == number_of_threads and failed == 0:

        print("RESULT: PASS")

    else:

        print("RESULT: FAIL")


# ---------------------------------------------------------
# MAIN
# ---------------------------------------------------------

if __name__ == "__main__":

    print()
    print("============================================")
    print(" HELIOS SQLite Database Concurrency Test")
    print("============================================")

    # Make sure telemetry table exists
    create_Table()

    print()
    print("Database table ready.")
    print()

    # Run all concurrency levels
    for thread_count in THREAD_COUNTS:

        run_test(thread_count)

    print()
    print("============================================")
    print(" All concurrency tests completed")
    print("============================================")

