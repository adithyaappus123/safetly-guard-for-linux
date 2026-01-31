Responsiveness Guard System

 Overview
The Responsiveness Guard System is a Linux-based performance management framework designed to keep a system responsive under high load. It continuously monitors system activity, detects performance degradation (such as input lag or CPU starvation), and dynamically controls misbehaving processes using modern Linux kernel mechanisms.

The system is especially useful for desktops, developer machines, and interactive environments where user experience must be preserved even when background tasks consume heavy resources.

 Key Goals
- Maintain smooth user interaction
- Detect and mitigate input lag and CPU contention
- Prevent background tasks from degrading system responsiveness
- Apply controls safely and automatically recover when load decreases

 High-Level Architecture
The system is organized into four logical layers:

1. Monitoring Layer – collects real-time system data
2. Detection Engine – analyzes metrics and makes decisions
3. Control Layer – applies throttling and recovery actions
4. Linux Kernel Interfaces – enforces actions at kernel level

Each layer has a clear responsibility and communicates through well-defined data flow.



 1. Monitoring Layer
 Purpose
Collect real-time metrics about system performance, process behavior, and user activity with minimal overhead.

 Components
 eBPF Monitor
- Tracks CPU cycles, wakeups, and run queue pressure
- Uses eBPF for efficient kernel-level monitoring

 /proc Scanner
- Reads process information from `/proc`
- Collects CPU usage, memory stats, and I/O statistics

 System Events Tracker
- Monitors keyboard input, mouse activity, and window focus changes
- Helps determine whether the user is actively interacting with the system

 Metrics Aggregator
- Runs at a fixed interval (e.g., every 10 ms)
- Maintains process tables
- Computes performance scores and lag indicators

Output: Normalized metrics and scores per process

 2. Detection Engine
 Purpose
Analyze collected metrics to identify responsiveness issues and determine corrective actions.

 Components
 Process Classifier
Categorizes processes into:
- GUI applications
- CLI applications
- Background jobs
- System services

This helps prioritize user-facing workloads.

 Rule Engine
Applies threshold-based rules such as:
- CPU usage > 70%
- Run queue length > 5
- Input latency > 100 ms

Processes violating rules are flagged.
 Context-Aware Logic
Considers system context:
- User activity state
- Time of day
- Overall system load

This prevents unnecessary throttling during acceptable high-load scenarios.
 Decision Maker
- Determines throttling intensity
- Selects target processes
- Assigns priorities

Output: Throttle and control commands



 3. Control Layer
 Purpose
Safely apply performance controls while ensuring system stability and reversibility.

 Components
 Gradual Throttler
- Applies incremental adjustments
- Modifies process priority (nice values)
- Applies cgroup resource limits
- Supports CPU core isolation when needed

 Safety Manager
- Uses watchdog timers
- Monitors system health
- Automatically rolls back changes on failure

 Recovery Manager
- Removes throttles when conditions normalize
- Performs timeout checks
- Restores original process states

 Linux Kernel Integration
Acts as an abstraction layer over kernel APIs, ensuring controlled and consistent enforcement.



 4. Linux Kernel Interfaces
 Purpose
Directly enforce decisions using native Linux kernel mechanisms.
 Components
 cgroup v2 API
Controls resource allocation using:
- `cpu.max`
- `memory.max`
- `io.max`
- `pids.max`

 Process Scheduler API
Adjusts scheduling behavior via:
- `sched_setscheduler()`
- `sched_setaffinity()`
- `setpriority()`

 eBPF Runtime
- Uses BPF system calls
- Maintains BPF maps
- Attaches tracepoints and kprobes


 Data Flow Summary
1. System metrics are collected in real time
2. Metrics are analyzed for responsiveness issues
3. Decisions are made based on rules and context
4. Kernel-level controls are applied
5. System recovers automatically when load decreases

 Technologies Used
- Linux Kernel APIs
- eBPF (Extended Berkeley Packet Filter)
- cgroup v2
- procfs
- Linux Scheduler

Use Cases
- Desktop and laptop performance management
- Developer workstations
- Systems running heavy background workloads
- Interactive Linux environments

 Future Enhancements
- Machine learning–based anomaly detection
- User-configurable policies
- Visualization dashboard
- Per-application responsiveness profiles