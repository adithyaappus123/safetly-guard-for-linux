"""
main.py

Orchestrates the responsiveness guard.
Connects monitoring + detection + rules + enforcement.
"""

import time
import sys
import subprocess
import os
import platform

# Import local modules
from antigravity_monitor import AntigravityMonitor
from proc_scanner import ProcessScanner
from cpu_detector import CPUDetector
from rule_engine import RuleEngine

# Configuration
CHECK_INTERVAL_SECONDS = 2.0
DRY_RUN = False

# Platform check for Hackathon Demo safety
if platform.system() == "Windows":
    print("[!] Detected Windows Environment. Enabling DRY_RUN mode.")
    print("[!] cgroup_limiter.sh calls will be printed, not executed.")
    DRY_RUN = True
elif os.geteuid() != 0:
    print("[!] Not running as root. Cgroup enforcement might fail.")

def enforce_limit(pid):
    """
    Calls the external bash script to limit the process.
    """
    cmd = ["bash", "./cgroup_limiter.sh", "limit", str(pid)]
    
    if DRY_RUN:
        print(f"[DRY_RUN] Executing: {' '.join(cmd)}")
        return

    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error limiting PID {pid}: {e}")
    except FileNotFoundError:
        print("Error: bash or cgroup_limiter.sh not found.")

def main():
    print("=== Responsiveness Guard Initialized ===")
    print("Monitor: Antigravity API (Simulated)")
    print("Enforcer: cgroup v2")
    
    monitor = AntigravityMonitor()
    scanner = ProcessScanner(ignore_pids=[os.getpid()]) # Don't limit ourselves
    detector = CPUDetector(monitor)
    rules = RuleEngine(limit_threshold=70.0)

    # Initial setup for cgroups
    if not DRY_RUN:
        subprocess.run(["bash", "./cgroup_limiter.sh", "setup"])
    else:
        print("[DRY_RUN] Setup cgroup hierarchy...")

    try:
        while True:
            current_pids = scanner.scan()
            
            # If no PIDs found (e.g. Windows demo with simple /proc mock or empty)
            # functionality relies on scanner finding something.
            # On Windows, scanner.scan() returns [] unless we mock /proc.
            # For the demo on linux, it works.
            # For the demo on Windows, we might want to fake a PID if none exist 
            # effectively testing the logic. 
            # But the requirement is "Single Linux project", so standard code is fine.
            
            for pid in current_pids:
                usage = detector.update_and_get_usage(pid)
                
                if usage is None:
                    continue # Need more data points

                action = rules.evaluate(pid, usage)
                
                # Pretty print significant usage
                if usage > 10.0:
                    print(f"PID {pid:5}: {usage:5.1f}% CPU -> {action}")

                if action == "THROTTLE":
                    print(f"!!! VIOLATION DETECTED: PID {pid} using {usage:.1f}% CPU !!!")
                    enforce_limit(pid)
            
            # Prune old state
            detector.cleanup(current_pids)
            
            time.sleep(CHECK_INTERVAL_SECONDS)

    except KeyboardInterrupt:
        print("\nStopping Responsiveness Guard.")

if __name__ == "__main__":
    main()
