# Linux System Health Monitor

A lightweight Python command-line utility for checking the health of a Linux system from the terminal.

The monitor collects CPU, memory, disk, uptime, process, and network metrics, compares resource usage against configurable thresholds, and prints a structured health report. It also supports a continuous watch mode and can be scheduled with cron.

## Features

- CPU utilization monitoring
- Memory utilization monitoring
- Disk utilization monitoring
- System uptime reporting
- Top CPU-consuming process listing
- Network reachability test
- Configurable warning thresholds
- One-shot report mode
- Continuous `--watch` mode
- Clean handling of interrupted watch mode
- Compatible with cron-based scheduled execution

## Tech Stack

| Component | Technology |
|---|---|
| Language | Python 3 |
| System metrics | psutil |
| Networking | Python socket |
| CLI control | `sys.argv` |
| Scheduling | cron |
| Platform | Linux / WSL |

## How It Works

The program follows a simple monitoring pipeline:

```text
Start
  |
  v
Collect system metrics
  |
  +--> CPU usage
  +--> Memory usage
  +--> Disk usage
  +--> System uptime
  +--> Top CPU processes
  +--> Network reachability
  |
  v
Compare resource usage with thresholds
  |
  v
Generate structured terminal report
  |
  +--> One-time mode
  |
  +--> Watch mode (repeat every 5 seconds)
```

The code separates metric collection from reporting so individual checks can be extended or tested independently.

## Project Structure

```text
linux-system-health-monitor/
├── monitor.py
├── requirements.txt
├── README.md
├── BUILD_GUIDE.md
└── .gitignore
```

## Requirements

- Linux environment
- Python 3
- `psutil`

### Windows users

The project can be run through WSL with Ubuntu. See [BUILD_GUIDE.md](BUILD_GUIDE.md) for the complete setup flow.

## Installation

Clone the repository:

```bash
git clone https://github.com/AKHI1630/linux-system-health-monitor.git
cd linux-system-health-monitor
```

Create and activate a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

## Usage

### One-time report

```bash
python3 monitor.py
```

### Continuous watch mode

```bash
python3 monitor.py --watch
```

Watch mode refreshes the report every 5 seconds. Press `Ctrl+C` to stop cleanly.

## Configuration

The main configuration values are defined near the top of `monitor.py`.

| Setting | Default | Purpose |
|---|---:|---|
| `CPU_THRESHOLD` | 80.0% | CPU warning threshold |
| `MEMORY_THRESHOLD` | 80.0% | Memory warning threshold |
| `DISK_THRESHOLD` | 85.0% | Disk warning threshold |
| `DISK_PATH` | `/` | Filesystem to inspect |
| `TOP_PROCESS_COUNT` | 5 | Number of top CPU processes |
| `WATCH_INTERVAL` | 5 sec | Watch-mode refresh interval |
| `NETWORK_TEST_HOST` | `8.8.8.8` | Network test destination |
| `NETWORK_TEST_PORT` | 53 | TCP port used for connectivity test |

A metric is reported as `[WARNING]` when the measured percentage reaches or exceeds its configured threshold.

## Example Output

```text
====================================================
           SYSTEM HEALTH REPORT
====================================================
Hostname  : ubuntu
Timestamp : 2026-09-20 22:00:00
Uptime    : 2 days, 03:15:21
----------------------------------------------------
CPU       :   34.7%   [OK]
Memory    :   48.2%   [OK]
            7.7 GB used of 16.0 GB
Disk (/)  :   61.4%   [OK]
            98.2 GB used of 160.0 GB
Network   : reachable        [OK]
----------------------------------------------------
Top 5 processes by CPU:
  python3              CPU  11.2%   MEM   2.1%
  code                 CPU   7.4%   MEM   4.8%
  ...
====================================================
```

Values above are illustrative. Actual output depends on the machine where the monitor runs.

## Alert Demonstration

To generate real CPU load on Linux, you can use:

```bash
yes > /dev/null &
```

On multi-core systems, multiple `yes` processes may be needed to push total CPU usage above the configured threshold.

Stop the load generators with:

```bash
killall yes
```

Another safe demonstration method is temporarily lowering `CPU_THRESHOLD`, running the monitor, and restoring the default before committing changes.

## Cron Automation

The monitor can be executed automatically every 10 minutes and its output appended to a log.

Create the log directory:

```bash
mkdir -p ~/system-health-monitor/logs
```

Edit the cron table:

```bash
crontab -e
```

Add:

```cron
*/10 * * * * /usr/bin/python3 /home/YOUR_USERNAME/system-health-monitor/monitor.py >> /home/YOUR_USERNAME/system-health-monitor/logs/health.log 2>&1
```

Verify:

```bash
crontab -l
```

Read the resulting log:

```bash
cat ~/system-health-monitor/logs/health.log
```

### WSL note

In WSL, cron may need to be started manually:

```bash
sudo service cron start
```

## Technical Details

### CPU

CPU usage is collected with `psutil.cpu_percent(interval=1)`. The one-second sampling interval provides a meaningful utilization measurement instead of relying on an initial instantaneous reading.

### Memory

`psutil.virtual_memory()` provides memory percentage plus used and total memory values.

### Disk

`psutil.disk_usage("/")` reports usage for the configured filesystem path.

### Uptime

The monitor reads the system boot timestamp and subtracts it from the current time to produce a human-readable uptime duration.

### Processes

`psutil.process_iter()` collects PID, process name, CPU percentage, and memory percentage. Processes are sorted by CPU usage and the top configured number are displayed. Processes that disappear during iteration or cannot be accessed are skipped safely.

### Network

The network check opens a TCP socket to `8.8.8.8:53`. Because the destination is an IP address, DNS name resolution is intentionally avoided; this check therefore focuses on outbound network connectivity rather than DNS functionality.

## Design Decisions

### Why psutil?

The project needs operating-system metrics that are not conveniently exposed through Python's standard library alone. `psutil` provides a compact cross-platform interface for CPU, memory, disk, process, and boot-time information.

### Why threshold checks?

The project is designed as a small diagnostic utility. A threshold turns raw utilization numbers into an immediately readable health signal:

- `[OK]` — metric is below the configured threshold
- `[WARNING]` — metric reached or exceeded the threshold

### Why a command-line report?

The terminal output keeps the tool lightweight and easy to deploy on a remote Linux machine without requiring a dashboard or additional server infrastructure.

## Limitations

- Alerts are printed to the terminal; there is no email, Slack, webhook, or SMS notification layer.
- The project stores point-in-time reports only when output is redirected or scheduled into logs.
- The network test checks reachability to one configured destination; it is not a complete network diagnostic.
- Containerized environments may report host-level memory depending on the runtime and psutil behavior.
- Cron automation is demonstrated externally to the Python program rather than managed internally.

## Future Enhancements

- Persistent historical metrics using SQLite
- CSV/JSON export
- Email and webhook alerts
- Configurable command-line arguments or a YAML/TOML config file
- Systemd service and timer support
- Container/cgroup-aware resource reporting
- Trend charts and a lightweight web dashboard
- Health history and alert state tracking
- Automated tests for metric helpers

## Troubleshooting

### psutil is missing

```text
ModuleNotFoundError: No module named 'psutil'
```

Install the dependency:

```bash
pip install -r requirements.txt
```

### Ubuntu blocks global pip installation

Use a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Network shows unreachable

A firewall may block outbound TCP connections to port 53. Change the configured test destination or use an alternative connectivity check appropriate to your environment.

### Cron does not run in WSL

Start cron:

```bash
sudo service cron start
```

## Resume-Ready Description

> Built a Python-based Linux system health monitoring utility using psutil to track CPU, memory, disk utilization, uptime, running processes, and network reachability, with configurable threshold-based warnings and continuous watch-mode diagnostics; integrated cron scheduling for automated terminal logging.

## Interview / Viva Talking Points

- Why `psutil.cpu_percent(interval=1)` uses an interval
- Difference between resource measurement and threshold evaluation
- Why process iteration catches `NoSuchProcess` and `AccessDenied`
- How cron's five scheduling fields work
- Why a TCP socket check is used for connectivity
- Difference between network connectivity testing and DNS resolution
- Why `if __name__ == "__main__"` is used
- How the program can evolve into a production monitoring agent

## Author

**AKHI1630**

GitHub: https://github.com/AKHI1630

## License

This project is provided for educational and portfolio use.
