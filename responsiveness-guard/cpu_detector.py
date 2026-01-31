"""
cpu_detector.py

Stateful detector that calculates CPU percentage over time.
eBPF-style monitoring requires "maps" (state); here we use a Python dict.
"""

class CPUDetector:
    def __init__(self, monitor):
        self.monitor = monitor
        # State: {pid: {'last_proc_time': float, 'last_sys_time': float}}
        self.state = {}

    def update_and_get_usage(self, pid):
        """
        Updates state for PID and returns its CPU usage percentage [0-100].
        Returns None if not enough data (first tick).
        """
        current_sys_time = self.monitor.get_system_cpu_times()
        current_proc_time = self.monitor.get_process_cpu_time(pid)

        if pid not in self.state:
            # First observation
            self.state[pid] = {
                'last_proc_time': current_proc_time,
                'last_sys_time': current_sys_time
            }
            return None

        last_proc = self.state[pid]['last_proc_time']
        last_sys = self.state[pid]['last_sys_time']

        delta_proc = current_proc_time - last_proc
        delta_sys = current_sys_time - last_sys

        # Update state immediately
        self.state[pid]['last_proc_time'] = current_proc_time
        self.state[pid]['last_sys_time'] = current_sys_time

        # Avoid division by zero
        if delta_sys == 0:
            return 0.0

        # Calculate percentage (assuming 1 core scaling, or overall system load)
        # Usage = (process_delta / system_delta) * 100 * (Number of Cores? No, simplifying to single core equivalent usage or % of total)
        # actually /proc/stat lines are summing ticks across all CPUs usually.
        # This formula gives % of TOTAL system capacity used by process.
        # If I want % of A SINGLE CORE (like top), I would multiply by num_cpus.
        # For responsiveness guard, "Percentage of Total System Reponsiveness" is a good metric.
        # We'll use % of total capacity.
        
        usage = (delta_proc / delta_sys) * 100.0
        
        # Cleanup: if process died (proc time went backwards or 0?), handled by caller usually
        return usage
    
    def cleanup(self, current_pids):
        """Removes stale PIDs from state."""
        for pid in list(self.state.keys()):
            if pid not in current_pids:
                del self.state[pid]
