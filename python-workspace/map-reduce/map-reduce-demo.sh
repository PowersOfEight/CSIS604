#!/usr/bin/env bash

# Author: James Daniel Johnson
# CWID: 20183229
# Course: CSIS 604 - Distributed Systems
# Assignment: 2.2 - Mini Map Reduce

# Create the PIDS array to capture process IDs
PIDS=()

terminate() {
  # Unbind the traps immediately so Ctrl+C doesn't re-trigger this function
  trap - SIGINT SIGTERM

  echo -e "\n[!] Cleaning up background processes..."

  if [ ${#PIDS[@]} -ne 0 ]; then
    echo "Sending SIGTERM to PIDs: ${PIDS[*]}"
    # Force a rapid termination instead of waiting on Python's slow grace period
    kill -15 "${PIDS[@]}" 2>/dev/null

    # Give them exactly 1 second to pack up, then force kill anything left
    sleep 1
    kill -9 "${PIDS[@]}" 2>/dev/null
  fi

  exit 0
}

# Trap both Ctrl+C (SIGINT) and system termination (SIGTERM)
trap terminate SIGINT SIGTERM

# Use the direct venv binary + Python's '-u' flag for instant log streaming
PYTHON_EXEC=".venv/bin/python -u"

# Use the generator in daemon mode
echo "Starting generator in daemon mode..."
$PYTHON_EXEC generator.py --daemon --interval 5 &
PIDS+=($!)
echo "Started generator with PID=${PIDS[-1]}" # '${PIDS[-1]}' fetches the last added item

sleep 5

# Start the coordinator service
echo "Starting coordinator service..."
$PYTHON_EXEC coordinator.py &
PIDS+=($!)
echo "Started coordinator service with PID=${PIDS[-1]}"

sleep 5

# Start worker processes
echo "Starting 5 worker processes..."
for i in {1..5}; do
  $PYTHON_EXEC worker.py &
  PIDS+=($!)
  echo "Started worker process $i with PID=${PIDS[-1]}"
done

echo "------------------------------------------------"
echo "All processes started. Press Ctrl+C to stop them."
echo "------------------------------------------------"

# 'wait' without arguments waits for ALL background PIDs.
# If one worker dies early, 'wait' will still stay open for the others.
wait
