#!/usr/bin/env python3
"""
Linux System Health Monitor
---------------------------
Checks CPU, memory, disk, uptime, top processes and network
connectivity against configured thresholds, then prints a
structured report to the terminal.

Usage:
    python3 monitor.py
    python3 monitor.py --watch
"""

import sys
import socket
import time
import datetime

import psutil


CPU_THRESHOLD = 80.0
MEMORY_THRESHOLD = 80.0
DISK_THRESHOLD = 85.0

DISK_PATH = "/"
TOP_PROCESS_COUNT = 5
WATCH_INTERVAL = 5

NETWORK_TEST_HOST = "8.8.8.8"
NETWORK_TEST_PORT = 53


def check_status(value, threshold):
    """Return a warning status when a metric reaches its threshold."""
    if value >= threshold:
        return f"[WARNING - above {threshold}% threshold]"
    return "[OK]"


def format_bytes(num_bytes):
    """Convert a byte count to a human-readable value."""
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if num_bytes < 1024:
            return f"{num_bytes:.1f} {unit}"
        num_bytes /= 1024
    return f"{num_bytes:.1f} PB"


def get_cpu_usage():
    """Return CPU utilization as a percentage."""
    return psutil.cpu_percent(interval=1)


def get_memory_info():
    """Return psutil virtual-memory information."""
    return psutil.virtual_memory()


def get_disk_info(path=DISK_PATH):
    """Return disk usage information for the configured filesystem."""
    return psutil.disk_usage(path)


def get_uptime():
    """Return system uptime as a datetime.timedelta."""
    boot_timestamp = psutil.boot_time()
    now_timestamp = time.time()
    uptime_seconds = now_timestamp - boot_timestamp
    return datetime.timedelta(seconds=int(uptime_seconds))


def get_top_processes(count=TOP_PROCESS_COUNT):
    """Return the processes using the most CPU."""
    processes = []

    for proc in psutil.process_iter(
        ["pid", "name", "cpu_percent", "memory_percent"]
    ):
        try:
            processes.append(proc.info)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue

    processes.sort(key=lambda p: p["cpu_percent"] or 0, reverse=True)
    return processes[:count]


def check_network():
    """Test outbound TCP connectivity to the configured host and port."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(3)
    try:
        sock.connect((NETWORK_TEST_HOST, NETWORK_TEST_PORT))
        return True
    except OSError:
        return False
    finally:
        sock.close()


def print_report():
    """Collect metrics and print a formatted health report."""
    cpu = get_cpu_usage()
    memory = get_memory_info()
    disk = get_disk_info()
    uptime = get_uptime()
    processes = get_top_processes()
    network_up = check_network()

    hostname = socket.gethostname()
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    print()
    print("=" * 52)
    print("           SYSTEM HEALTH REPORT")
    print("=" * 52)
    print(f"Hostname  : {hostname}")
    print(f"Timestamp : {timestamp}")
    print(f"Uptime    : {uptime}")
    print("-" * 52)

    print(f"CPU       : {cpu:>6.1f}%   {check_status(cpu, CPU_THRESHOLD)}")

    print(
        f"Memory    : {memory.percent:>6.1f}%   "
        f"{check_status(memory.percent, MEMORY_THRESHOLD)}"
    )
    print(
        f"            {format_bytes(memory.used)} used "
        f"of {format_bytes(memory.total)}"
    )

    print(
        f"Disk ({DISK_PATH})  : {disk.percent:>6.1f}%   "
        f"{check_status(disk.percent, DISK_THRESHOLD)}"
    )
    print(
        f"            {format_bytes(disk.used)} used "
        f"of {format_bytes(disk.total)}"
    )

    if network_up:
        print("Network   : reachable        [OK]")
    else:
        print("Network   : UNREACHABLE      [WARNING]")

    print("-" * 52)
    print(f"Top {len(processes)} processes by CPU:")

    for proc in processes:
        name = proc["name"] or "unknown"
        cpu_pct = proc["cpu_percent"] or 0
        mem_pct = proc["memory_percent"] or 0
        print(
            f"  {name:<20} CPU {cpu_pct:>5.1f}%   "
            f"MEM {mem_pct:>5.1f}%"
        )

    print("=" * 52)
    print()


def main():
    """Run one report or continuously refresh in watch mode."""
    watch_mode = "--watch" in sys.argv[1:]

    if watch_mode:
        print("Watch mode - press Ctrl+C to stop.")
        try:
            while True:
                print_report()
                time.sleep(WATCH_INTERVAL)
        except KeyboardInterrupt:
            print("\nStopped.")
    else:
        print_report()


if __name__ == "__main__":
    main()
