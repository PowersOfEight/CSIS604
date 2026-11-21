"""Exercise 3: 50 KV writes/s under the currently configured packet-loss level.

Set LOSS to match the tc netem rule before each run. Uses the Consul UI API
published at localhost:8500, not a container-only 10.99.0.x address.
"""

import csv
import math
import time
import uuid
from collections import Counter
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

LOSS = 25                # Change b/w 5/10/25. Does not actually implement loss, tc netem command does
RATE = 50                # Scheduled writes per second.
DURATION = 20            # Seconds of write submissions per trial.
TRIALS = 3               # three different trials.
TIMEOUT = 10             # Seconds per HTTP request; timeouts count as failures.
WORKERS = 100            # Avoid a 20-thread bottleneck at high tail latency.
URL = "http://127.0.0.1:8500/v1/kv/exercise3/load/"
CSV_FILE = "exercise3_results_corrected.csv"


#Calculates the p50/p99 values, 50th percentile is the median of values, 99th is time of approx of 99th percent values
def percentile(values, percent):
    if not values:
        return None
    values = sorted(values)
    index = (len(values) - 1) * percent / 100
    lower = math.floor(index)
    upper = math.ceil(index)
    return values[lower] + (values[upper] - values[lower]) * (index - lower)

#send the KV write request to the consul and measure response time
def write(key):
    request = Request(URL + key, data=b"test-value", method="PUT")
    started = time.perf_counter()
    try:
        with urlopen(request, timeout=TIMEOUT) as response:
            ok = response.status == 200 and response.read().strip().lower() == b"true"
            error = "" if ok else f"unexpected_response_{response.status}"
    except HTTPError as exc:
        ok, error = False, f"http_{exc.code}"
    except (URLError, TimeoutError, OSError) as exc:
        ok, error = False, type(exc).__name__
    return (time.perf_counter() - started) * 1000, ok, error

#creates threads for simultaneous writes, target 1 write/20 ms
def run_trial(trial, run_id):
    futures = []
    started = time.perf_counter()
    with ThreadPoolExecutor(max_workers=WORKERS) as pool:
        for i in range(RATE * DURATION):
            target = started + i / RATE
            wait = target - time.perf_counter()
            if wait > 0:
                time.sleep(wait)
            futures.append(pool.submit(write, f"{run_id}-{trial}-{i}"))
        observations = [future.result() for future in as_completed(futures)]
    elapsed = time.perf_counter() - started
    successful_ms = [ms for ms, ok, _ in observations if ok]
    errors = Counter(error for _, ok, error in observations if not ok)
    return {
        "run_id": run_id,
        "loss_pct": LOSS,
        "trial": trial,
        "target_writes_per_sec": RATE,
        "attempted": len(observations),
        "successful": len(successful_ms),
        "failed": len(observations) - len(successful_ms),
        "p50_ms": percentile(successful_ms, 50),
        "p99_ms": percentile(successful_ms, 99),
        "elapsed_sec": elapsed,
        "errors": "; ".join(f"{error}: {count}" for error, count in sorted(errors.items())),
    }

#quick decimal format
def fmt(value):
    return "N/A" if value is None else f"{value:.2f}"

#main, triggers the trial when running file
#3 trials at the same packet loss with a 20 second trial time
#each trial is 1000 writes because 50 writes/sec for 20 sec
def main():
    run_id = uuid.uuid4().hex[:8]
    print(f"{LOSS}% loss | {TRIALS} trials | {RATE} writes/sec for {DURATION}s per trial")
    print(f"Endpoint: {URL}")
    results = []
    for trial in range(1, TRIALS + 1):
        row = run_trial(trial, run_id)
        results.append(row)
        print(
            f"Trial {trial}: p50={fmt(row['p50_ms'])} ms, "
            f"p99={fmt(row['p99_ms'])} ms, "
            f"successful={row['successful']}, failed={row['failed']}, "
            f"elapsed={row['elapsed_sec']:.1f}s"
        )
        if row["errors"]:
            print(f"  Errors: {row['errors']}")

    # Keep earlier valid runs, but avoid the old CSV's unreachable-address data.
    fields = list(results[0].keys())
    try:
        with open(CSV_FILE, "r", newline="") as file:
            has_header = bool(file.read(1))
    except FileNotFoundError:
        has_header = False
    with open(CSV_FILE, "a", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fields)
        if not has_header:
            writer.writeheader()
        writer.writerows(results)

    total_success = sum(r["successful"] for r in results)
    total_failed = sum(r["failed"] for r in results)
    print(f"Totals: {total_success} successful, {total_failed} failed")
    print(f"Saved: {CSV_FILE}")
    print("Percentiles include successful writes only; timeouts are counted as failures.")


if __name__ == "__main__":
    main()