# FUN Server Startup & Shutdown Guide

## Quick Start

### Start the Server

Using the provided PowerShell script:
```powershell
.\win_tool\start_server.ps1
```

Or directly with Python:
```bash
python -u src/server.py
# or
.venv\Scripts\python.exe -u src/server.py
```

The server runs on **http://127.0.0.1:5000**

### Stop the Server

Using the provided PowerShell script:
```powershell
.\win_tool\stop_server.ps1
```

Or manually kill the process:
```powershell
Stop-Process -Name python -Force  # kill all Python processes
# or find specific PID listening on port 5000
netstat -ano | Select-String ":5000"
```

---

## What the Startup Script Does

`win_tool/start_server.ps1`:
1. ✅ Checks if Python venv exists at `.venv\Scripts\python.exe`
2. ✅ Verifies server entrypoint exists at `src\server.py`
3. ✅ Checks if port 5000 is already in use
4. ✅ Starts the server in background (if not running)
5. ✅ Performs 10 health checks (2 sec interval)
6. ✅ Displays server URL on success

## What the Shutdown Script Does

`win_tool/stop_server.ps1`:
1. ✅ Finds processes listening on port 5000
2. ✅ Finds all Python processes running `server.py`
3. ✅ Identifies child processes
4. ✅ Gracefully terminates all matched processes (Force kill)

---

## Troubleshooting

### Port Already in Use
If port 5000 is already in use, the startup script will detect it and report "Server seems already running."

Kill manually:
```powershell
.\win_tool\stop_server.ps1
```

### See Server Logs
Run in foreground to see Flask debug output:
```powershell
.venv\Scripts\python.exe -u src/server.py
```

### Python Module Import Errors
Ensure dependencies are installed:
```bash
pip install -r requirements.txt
```

---

## Key Files

- `src/server.py` — Flask server entrypoint
- `win_tool/start_server.ps1` — Startup script with health checks
- `win_tool/stop_server.ps1` — Shutdown and cleanup script
- `.venv/Scripts/python.exe` — Virtual environment Python executable
- `requirements.txt` — Python dependencies
