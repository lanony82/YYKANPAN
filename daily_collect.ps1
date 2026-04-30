# daily_collect.ps1
# Runs the stock collector. Schedule this with Windows Task Scheduler for daily runs.
#
# Quick setup (run once as Admin to schedule at 6 PM every weekday):
#   .\daily_collect.ps1 -Register
#
# Manual run:
#   .\daily_collect.ps1

param(
    [switch]$Register
)

$ScriptDir   = $PSScriptRoot
$PythonScript = Join-Path $ScriptDir "src\\collect_stocks.py"
$LogDir       = Join-Path $ScriptDir "logs"
$LogFile      = Join-Path $LogDir ("collect_" + (Get-Date -Format "yyyy-MM-dd") + ".log")

if (-not (Test-Path $LogDir)) { New-Item -ItemType Directory -Path $LogDir | Out-Null }

if ($Register) {
    $action  = New-ScheduledTaskAction -Execute "python" -Argument "`"$PythonScript`"" -WorkingDirectory $ScriptDir
    $trigger = New-ScheduledTaskTrigger -Weekly -DaysOfWeek Monday,Tuesday,Wednesday,Thursday,Friday -At 6:00PM
    $settings = New-ScheduledTaskSettingsSet -StartWhenAvailable -RunOnlyIfNetworkAvailable
    Register-ScheduledTask -TaskName "DailyStockCollect" -Action $action -Trigger $trigger -Settings $settings -Force
    Write-Host "Task registered: DailyStockCollect — runs weekdays at 6 PM" -ForegroundColor Green
    return
}

Write-Host "Running stock collector at $(Get-Date)..." -ForegroundColor Cyan
python $PythonScript 2>&1 | Tee-Object -FilePath $LogFile
Write-Host "Log saved to $LogFile" -ForegroundColor DarkGray
