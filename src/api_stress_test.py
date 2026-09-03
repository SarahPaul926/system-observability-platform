"""
api_stress_test.py
==================

Test 2:
Flask API concurrency/load testing.

This test sends multiple concurrent requests
to the HELIOS /api/metrics/live endpoint.
"""

import threading
import time
import requests


# ---------------------------------------------------------
# CONFIGURATION
# ---------------------------------------------------------

API_URL = "http://127.0.0.1:5000/api/metrics/live"

THREAD_COUNTS = [1, 5, 10, 20, 50]


# ---------------------------------------------------------
# SHARED TEST DATA
# ---------------------------------------------------------

success = 0
failed = 0

response_times = []

counter_lock = threading.Lock()


# ---------------------------------------------------------
# WORKER
# ---------------------------------------------------------

def worker(thread_id):

    global success
    global failed

    start_time = time.time()

    try:

        response = requests.get(
            API_URL,
            timeout=30
        )

        end_time = time.time()

        response_time = end_time - start_time

        with counter_lock:

            response_times.append(response_time)

            if response.status_code == 200:

                success += 1

                print(
                    f"Request {thread_id}: "
                    f"SUCCESS "
                    f"({response_time:.4f}s)"
                )

            else:

                failed += 1

                print(
                    f"Request {thread_id}: "
                    f"FAILED "
                    f"HTTP {response.status_code}"
                )

    except Exception as e:

        with counter_lock:

            failed += 1

        print(
            f"Request {thread_id}: "
            f"FAILED -> {e}"
        )


# ---------------------------------------------------------
# RUN ONE TEST
# ---------------------------------------------------------

def run_test(number_of_threads):

    global success
    global failed
    global response_times

    # Reset results

    success = 0
    failed = 0
    response_times = []

    threads = []

    print()
    print("================================")
    print(
        f"Starting API test with "
        f"{number_of_threads} requests"
    )
    print("================================")

    # Start timer

    start_time = time.time()

    # -----------------------------------------------------
    # CREATE THREADS
    # -----------------------------------------------------

    for i in range(number_of_threads):

        thread = threading.Thread(
            target=worker,
            args=(i,),
            name=f"API-Thread-{i}"
        )

        threads.append(thread)

    # -----------------------------------------------------
    # START ALL THREADS
    # -----------------------------------------------------

    for thread in threads:

        thread.start()

    # -----------------------------------------------------
    # WAIT FOR ALL THREADS
    # -----------------------------------------------------

    for thread in threads:

        thread.join()

    # End timer

    end_time = time.time()

    total_time = end_time - start_time

    # -----------------------------------------------------
    # CALCULATE STATISTICS
    # -----------------------------------------------------

    if response_times:

        average_response = (
            sum(response_times)
            / len(response_times)
        )

        maximum_response = max(response_times)
        minimum_response = min(response_times)

    else:

        average_response = 0
        maximum_response = 0
        minimum_response = 0

    # -----------------------------------------------------
    # RESULTS
    # -----------------------------------------------------

    print()
    print("--------------------------------")
    print(
        f"Requests          : {number_of_threads}"
    )
    print(
        f"Success           : {success}"
    )
    print(
        f"Failed            : {failed}"
    )
    print(
        f"Total time        : {total_time:.4f}s"
    )
    print(
        f"Average response  : "
        f"{average_response:.4f}s"
    )
    print(
        f"Minimum response  : "
        f"{minimum_response:.4f}s"
    )
    print(
        f"Maximum response  : "
        f"{maximum_response:.4f}s"
    )
    print("--------------------------------")

    # -----------------------------------------------------
    # PASS / FAIL
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
    print(" HELIOS Flask API Concurrency Test")
    print("============================================")

    print()
    print(
        f"Testing endpoint: {API_URL}"
    )

    print()

    # Run all test levels

    for thread_count in THREAD_COUNTS:

        run_test(thread_count)

    print()
    print("============================================")
    print(" All API tests completed")
    print("============================================")
