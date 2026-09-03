"""
ai_stress_test.py
=================

Test 3:
Background AI investigation concurrency testing.

This test directly tests the threading mechanism used
inside core metric.py.

Purpose:
    Verify that multiple concurrent anomaly events
    start only ONE background AI investigation.

The real Gemini/LLM call is replaced temporarily with
a simulated AI function so that this test does not
consume Gemini API quota.

Tested components from metric.py:

    - ai_lock
    - ai_investigation_running
    - ai_latest_result
    - run_ai()
    - threading.Thread

Expected result:

    50 concurrent anomaly events
                ↓
        ONE AI investigation
                ↓
        remaining requests
             are skipped
"""


import threading
import time
from api import metrics



# ============================================================
# TEST CONFIGURATION
# ============================================================

THREAD_COUNTS = [1, 5, 10, 20, 50]


# ============================================================
# TEST COUNTERS
# ============================================================

ai_start_count = 0
ai_complete_count = 0

counter_lock = threading.Lock()


# ============================================================
# FAKE AI FUNCTION
# ============================================================

def fake_analyze_incident(incident):

    """
    Simulates the Gemini/LLM call.

    We deliberately make this take a few seconds so that
    concurrent requests have time to arrive while the
    first AI investigation is still running.
    """

    global ai_complete_count

    print()
    print("    [FAKE AI] Gemini analysis started")

    # Simulate LLM processing time
    time.sleep(2)

    print("    [FAKE AI] Gemini analysis completed")

    with counter_lock:
        ai_complete_count += 1

    return {
        "summary": "Simulated AI investigation completed.",
        "root_cause": "Simulated high CPU process.",
        "contributors": [
            "Test Process"
        ],
        "recommendations": [
            "Inspect the high CPU process."
        ],
        "confidence": 0.95
    }


# ============================================================
# FAKE PROCESS MONITOR
# ============================================================

def fake_get_process():

    """
    Simulates the process monitor.

    This prevents the stress test from depending on
    real running processes.
    """

    print("    [FAKE PROCESS] Getting process information")

    return [
        {
            "process_id": 1234,
            "name": "Test Process",
            "cpu_percent": 90.0,
            "memory_percent": 10.0
        }
    ]


# ============================================================
# FAKE SYSTEM SNAPSHOT
# ============================================================

def fake_system_snapshot(
    metrics,
    anomaly,
    issues,
    process
):

    """
    Simulates creation of the incident snapshot.
    """

    print("    [FAKE SNAPSHOT] Creating incident snapshot")

    return {
        "metric": metrics,
        "anomaly": anomaly,
        "issues": issues,
        "processes": process
    }


# ============================================================
# PATCH THE REAL FUNCTIONS
# ============================================================

"""
IMPORTANT:

We are NOT rewriting run_ai().

We are using the REAL run_ai() from metric.py.

We only replace the expensive external dependencies:

    analyze_incident()
    get_process()
    system_snapshot()

This means the threading logic being tested is your
actual production code.
"""

metrics.analyze_incident = fake_analyze_incident
metrics.get_process = fake_get_process
metrics.system_snapshot = fake_system_snapshot


# ============================================================
# SIMULATE ANOMALY EVENT
# ============================================================

def trigger_anomaly(thread_id):

    """
    Simulates the anomaly section of metric.py.

    This reproduces the exact logic used by your
    /api/metrics/live route after anomaly == -1.

    We do this directly because we need to guarantee
    that every test request is an anomaly.
    """

    global ai_start_count

    print(
        f"Request {thread_id}: "
        f"ANOMALY DETECTED"
    )

    with metrics.ai_lock:

        if not metrics.ai_investigation_running:

            metrics.ai_investigation_running = True

            metrics.ai_latest_result = None

            with counter_lock:
                ai_start_count += 1

            print(
                f"Request {thread_id}: "
                f"STARTING background AI"
            )

            thread = threading.Thread(
                target=metrics.run_ai,
                args=(
                    {
                        "cpu": {
                            "cpu_usage": 95
                        },
                        "ram": {
                            "percent": 85
                        }
                    },
                    -1,
                    [
                        {
                            "resource": "CPU",
                            "message": "High CPU usage"
                        }
                    ]
                ),
                name="AI-Investigation"
            )

            thread.start()

        else:

            print(
                f"Request {thread_id}: "
                f"AI already running -> SKIPPED"
            )


# ============================================================
# RUN ONE TEST
# ============================================================

def run_test(number_of_threads):

    global ai_start_count
    global ai_complete_count

    # Reset test counters

    ai_start_count = 0
    ai_complete_count = 0

    # Reset REAL state from metric.py

    with metrics.ai_lock:

        metrics.ai_investigation_running = False

        metrics.ai_latest_result = None

    threads = []

    print()
    print("============================================")
    print(
        f"AI concurrency test: "
        f"{number_of_threads} anomaly requests"
    )
    print("============================================")

    start_time = time.time()

    # ========================================================
    # CREATE ALL REQUEST THREADS
    # ========================================================

    for i in range(number_of_threads):

        thread = threading.Thread(
            target=trigger_anomaly,
            args=(i,),
            name=f"Anomaly-Request-{i}"
        )

        threads.append(thread)

    # ========================================================
    # START ALL REQUEST THREADS
    # ========================================================

    for thread in threads:
        thread.start()

    # ========================================================
    # WAIT FOR REQUEST THREADS
    # ========================================================

    for thread in threads:
        thread.join()

    # ========================================================
    # WAIT FOR BACKGROUND AI
    # ========================================================

    print()
    print(
        "Waiting for background AI investigation..."
    )

    while True:

        with metrics.ai_lock:

            if not metrics.ai_investigation_running:
                break

        time.sleep(0.1)

    end_time = time.time()

    total_time = end_time - start_time

    # ========================================================
    # RESULTS
    # ========================================================

    print()
    print("--------------------------------------------")

    print(
        f"Anomaly requests       : "
        f"{number_of_threads}"
    )

    print(
        f"AI investigations      : "
        f"{ai_start_count}"
    )

    print(
        f"AI investigations done : "
        f"{ai_complete_count}"
    )

    print(
        f"AI result stored       : "
        f"{metrics.ai_latest_result is not None}"
    )

    print(
        f"Total time             : "
        f"{total_time:.4f}s"
    )

    print("--------------------------------------------")

    # ========================================================
    # PASS CONDITION
    # ========================================================

    if (
        ai_start_count == 1
        and ai_complete_count == 1
        and metrics.ai_latest_result is not None
        and metrics.ai_investigation_running is False
    ):

        print("RESULT: PASS")

        print(
            "Only ONE background AI investigation "
            "was started and completed."
        )

        return True

    else:

        print("RESULT: FAIL")

        print(
            "The AI concurrency mechanism did not "
            "behave as expected."
        )

        return False


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    print()
    print("============================================")
    print(" HELIOS AI CONCURRENCY STRESS TEST")
    print("============================================")

    print()
    print(
        "Testing the REAL threading logic from metric.py."
    )

    print(
        "Gemini is replaced with a simulated AI function."
    )

    print()

    results = []

    for thread_count in THREAD_COUNTS:

        result = run_test(thread_count)

        results.append(result)

    # ========================================================
    # FINAL SUMMARY
    # ========================================================

    print()
    print("============================================")
    print(" FINAL TEST 3 RESULTS")
    print("============================================")

    for i in range(len(THREAD_COUNTS)):

        thread_count = THREAD_COUNTS[i]

        result = results[i]

        status = "PASS" if result else "FAIL"

        print(
            f"{thread_count:>3} anomaly requests "
            f"-> {status}"
        )

    print()

    if all(results):

        print(
            "OVERALL RESULT: PASS"
        )

        print(
            "The HELIOS background AI investigation "
            "mechanism successfully prevented duplicate "
            "simultaneous AI investigations."
        )

    else:

        print(
            "OVERALL RESULT: FAIL"
        )

        print(
            "The AI concurrency mechanism requires "
            "further investigation."
        )

    print()
    print("============================================")
    print(" Test 3 completed")
    print("============================================")