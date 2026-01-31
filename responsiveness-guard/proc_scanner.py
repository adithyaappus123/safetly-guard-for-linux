"""
proc_scanner.py

Scans the kernel process table exposed via /proc.
Identifies active processes for monitoring.
"""

import os

class ProcessScanner:
    def __init__(self, ignore_pids=None):
        self.ignore_pids = ignore_pids or []

    def scan(self):
        """
        Yields PIDs of currently running processes.
        """
        if not os.path.exists('/proc'):
            return []

        pids = []
        for name in os.listdir('/proc'):
            if name.isdigit():
                pid = int(name)
                if pid not in self.ignore_pids:
                    pids.append(pid)
        return pids
