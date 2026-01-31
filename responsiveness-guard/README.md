# Responsiveness Guard

A minimal, end-to-end Linux system stability tool that monitors process CPU usage and automatically throttles offenders using `cgroup v2`.

## Project Structure

- **`antigravity_monitor.py`**: A high-level abstraction API ("Antigravity API") for standard Linux kernel metrics (`/proc`).
- **`proc_scanner.py`**: Scans the process table efficiently.
- **`cpu_detector.py`**: Stateful engine that calculates delta CPU usage per process.
- **`rule_engine.py`**: Evaluates business logic (e.g., `CPU > 70%`).
- **`cgroup_limiter.sh`**: The enforcement mechanism using pure Bash and cgroup v2.
- **`main.py`**: The conductor that runs the monitoring loop.

## Architecture Flow

1. **Collect**: `main.py` asks `proc_scanner` for active PIDs.
2. **Measure**: `antigravity_monitor` reads kernel counters; `cpu_detector` computes the delta over time.
3. **Decide**: `rule_engine` checks if usage > 70%.
4. **Act**: If violated, `cgroup_limiter.sh` writes the PID to the `responsiveness-guard` cgroup, capping it at 50% CPU.

## How to Run

### Prerequisites
- Linux Kernel 4.15+ (cgroup v2 support).
- Root privileges (for cgroup file writing).
- Python 3.

### Running the Demo
```bash
# 1. Start the guard (requires root for real enforcement)
sudo python3 main.py
```

### Simulating a CPU Spike
In another terminal:
```bash
# Generate 100% CPU load (1 core)
yes > /dev/null &
# Watch main.py detect and throttle it!
```

## Safety
- Does **not** kill processes (`kill -9` is avoided).
- Uses standard Linux kernel features (cgroups) for "soft" control.
- Degrades gracefully if metrics are unavailable.
