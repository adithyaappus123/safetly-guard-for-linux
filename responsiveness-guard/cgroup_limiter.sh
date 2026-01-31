#!/bin/bash
# cgroup_limiter.sh
# Enforces CPU limits using cgroup v2.
# Usage: 
#   ./cgroup_limiter.sh setup
#   ./cgroup_limiter.sh limit <PID>

CGROUP_ROOT="/sys/fs/cgroup"
GUARD_GROUP="responsiveness-guard"
FULL_PATH="$CGROUP_ROOT/$GUARD_GROUP"

# 50% Limit: 50000 quota / 100000 period
CPU_MAX="50000 100000"

setup() {
    if [ ! -d "$CGROUP_ROOT" ]; then
        echo "Error: cgroup v2 not mounted at $CGROUP_ROOT"
        exit 1
    fi

    # Create the guard group directory
    if [ ! -d "$FULL_PATH" ]; then
        echo "Creating cgroup: $GUARD_GROUP"
        mkdir -p "$FULL_PATH"
    fi

    # Enable cpu controller in root if needed (often enabled by default or systemd)
    # This might fail if we don't have permissions or if it's already delegated, 
    # but we try to ensure the controller is available.
    if [ -f "$CGROUP_ROOT/cgroup.subtree_control" ]; then
         # Only add if not present (heuristic)
         current=$(cat "$CGROUP_ROOT/cgroup.subtree_control")
         if [[ "$current" != *"cpu"* ]]; then
             echo "+cpu" > "$CGROUP_ROOT/cgroup.subtree_control" 2>/dev/null || true
         fi
    fi

    # Set the CPU limit
    if [ -f "$FULL_PATH/cpu.max" ]; then
        echo "$CPU_MAX" > "$FULL_PATH/cpu.max"
        echo "CPU limit set to 50% ($CPU_MAX) for $GUARD_GROUP"
    else
        echo "Error: cpu.max not found. Is the CPU controller enabled?"
        exit 1
    fi
}

limit_pid() {
    pid=$1
    if [ -z "$pid" ]; then
        echo "Usage: $0 limit <PID>"
        exit 1
    fi

    if [ ! -d "$FULL_PATH" ]; then
        setup
    fi

    # Add PID to cgroup.procs
    # Writing the PID moves it to this cgroup
    if echo "$pid" > "$FULL_PATH/cgroup.procs"; then
        echo "Throttled PID $pid (moved to $GUARD_GROUP)"
    else
        echo "Failed to throttle PID $pid (process might have exited)"
    fi
}

case "$1" in
    setup)
        setup
        ;;
    limit)
        limit_pid "$2"
        ;;
    *)
        echo "Usage: $0 {setup|limit <PID>}"
        exit 1
        ;;
esac
