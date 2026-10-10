<#
Registers (or removes) a Windows scheduled task that scans all pairs before the entry window.

  .\scripts\schedule-scan.ps1            create the task
  .\scripts\schedule-scan.ps1 -Remove    delete it

The task runs `python app\scan.py --scheduled` every 30 minutes. That command does nothing
unless it is 12:30 to 12:59 AM New York Monday to Wednesday, or Sunday 17:00 to 17:29 New York,
so it follows US daylight saving by itself (12:30 AM New York is 12:30 PM Manila in US summer,
1:30 PM in winter; Sunday 17:00 New York is Monday 5 AM or 6 AM Manila). MetaTrader 5 must be
open and logged in at those times, and the PC must be awake.
#>
param([switch]$Remove)
$name = "TradingGuide scan"
if ($Remove) {
    schtasks /Delete /TN $name /F
    return
}
$repo = Split-Path -Parent $PSScriptRoot
$python = (Get-Command python).Source
$cmd = "`"$python`" `"$repo\app\scan.py`" --scheduled"
schtasks /Create /TN $name /SC MINUTE /MO 30 /TR $cmd /F
Write-Host "Created '$name'. Check it with: schtasks /Query /TN `"$name`""
