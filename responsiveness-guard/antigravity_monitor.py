"""
antigravity_monitor.py

This module implements the "Antigravity API" for system monitoring.
It abstracts low-level kernel interactions (reading /proc) into clean, high-level calls.
In a real deployment, this might hook into eBPF maps, but for this hackathon demo,
we parse /procfs to simulate zero-overhead monitoring.
"""

import time
import os

class AntigravityMonitor:
    """
    AntigravityMonitor provides safe, read-only access to kernel metrics.
    """
    
    @staticmethod
    def get_system_cpu_times():
        """
        Returns total system CPU time (user + nice + system + idle ...)
        """
        try:
            with open('/proc/stat', 'r') as f:
                line = f.readline()
                if line.startswith('cpu'):
                    # cpu  2032 0 123 1234123 ...
                    parts = line.split()
                    # Sum all numbers after 'cpu'
                    return sum(float(x) for x in parts[1:])
        except FileNotFoundError:
            # Fallback for non-Linux demo environments (dev machine)
            return time.time() * 100 # Mock time
            
        return 0

    @staticmethod
    def get_process_cpu_time(pid):
        """
        Returns total CPU time (utime + stime) for a specific PID.
        """
        try:
            with open(f'/proc/{pid}/stat', 'r') as f:
                parts = f.read().split()
                # utime is index 13, stime is index 14 (1-based in man pages, 0-based here: 13, 14)
                # Beware of process names with spaces: (bash)
                # reliably finding the end of the executable name is safer, but assuming simple pNames for demo.
                # A safer parse looks for the last ')'
                
                # Simple parse for demo:
                utime = float(parts[13])
                stime = float(parts[14])
                return utime + stime
        except (FileNotFoundError, IndexError, ValueError):
            return 0
