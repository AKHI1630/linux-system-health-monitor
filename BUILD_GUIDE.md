# Build Guide — Linux System Health Monitor

This guide takes the project from an empty Linux environment to a runnable GitHub repository.

## 1. Get Linux Running

### Native Linux

Skip directly to Python installation.

### Windows

Install WSL with Ubuntu from an elevated PowerShell:

```powershell
wsl --install
```

Restart if prompted, then open Ubuntu from the Start menu.

## 2. Install Python and psutil

```bash
sudo apt update
sudo apt install python3 python3-pip python3-venv -y
```

Create a project environment:

```bash
mkdir -p ~/system-health-monitor
cd ~/system-health-monitor
python3 -m venv .venv
source .venv/bin/activate
```

Install psutil:

```bash
pip install psutil
```

Verify the installation:

```bash
python3 -c "import psutil; print(psutil.cpu_percent(interval=1))"
```

## 3. Run the Monitor

Place `monitor.py` in the project directory and run:

```bash
python3 monitor.py
```

For continuous monitoring:

```bash
python3 monitor.py --watch
```

Press `Ctrl+C` to stop watch mode.

## 4. Demonstrate Threshold Alerts

Open a second Linux terminal.

Generate CPU load:

```bash
yes > /dev/null &
```

On a multi-core machine, additional load generators may be needed:

```bash
yes > /dev/null &
yes > /dev/null &
yes > /dev/null &
```

Run the monitor and observe the CPU status.

Stop the test processes:

```bash
killall yes
```

An alternative is to temporarily lower the CPU threshold, run the monitor, capture the warning output, and restore the default value before committing.

## 5. Schedule Automatic Reports

Create a log directory:

```bash
mkdir -p ~/system-health-monitor/logs
```

Open cron:

```bash
crontab -e
```

Add:

```cron
*/10 * * * * /usr/bin/python3 /home/YOUR_USERNAME/system-health-monitor/monitor.py >> /home/YOUR_USERNAME/system-health-monitor/logs/health.log 2>&1
```

Replace `YOUR_USERNAME` with the output of:

```bash
whoami
```

Verify:

```bash
crontab -l
```

Read the log later with:

```bash
cat ~/system-health-monitor/logs/health.log
```

### Cron fields

```text
*/10  *  *  *  *
  |   |  |  |  |
  |   |  |  |  +-- day of week
  |   |  |  +----- month
  |   |  +-------- day of month
  |   +----------- hour
  +--------------- minute
```

`*/10` in the minute field means every 10 minutes.

### WSL note

WSL installations may require cron to be started manually:

```bash
sudo service cron start
```

## 6. GitHub Setup

The project repository is:

https://github.com/AKHI1630/linux-system-health-monitor

Clone it:

```bash
git clone https://github.com/AKHI1630/linux-system-health-monitor.git
cd linux-system-health-monitor
```

Install dependencies:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## 7. Suggested Development Workflow

Use small, meaningful commits while developing:

```text
Add initial monitor
Add configurable thresholds
Add process reporting
Add network connectivity check
Add watch mode
Add requirements
Add documentation
```

This makes the history easier to understand and review.

## 8. Common Problems

| Error | Fix |
|---|---|
| `ModuleNotFoundError: No module named 'psutil'` | Activate the virtual environment and install requirements |
| `python3: command not found` | Install Python with apt |
| `externally-managed-environment` | Use the virtual-environment workflow |
| Permission error for logs | Check the log directory and cron path |
| Cron does not run in WSL | Start cron with `sudo service cron start` |
| Network is always unreachable | Check outbound firewall rules or adjust the configured test host |

## 9. Verification Checklist

Before considering the project complete:

- [ ] `python3 monitor.py` runs successfully
- [ ] CPU, memory, and disk values are displayed
- [ ] Uptime is displayed
- [ ] Top processes are listed
- [ ] Network status is displayed
- [ ] Warning threshold can be demonstrated
- [ ] Watch mode refreshes every 5 seconds
- [ ] Cron entry is registered
- [ ] Log file receives scheduled reports
- [ ] Repository contains no virtual environment or log files
