# Check (and optionally install) everything the study and PDF workflow needs. Windows, PowerShell.
#   .\scripts\setup.ps1            check only, changes nothing
#   .\scripts\setup.ps1 -Install   install what is missing
param([switch]$Install)

$repo = Split-Path -Parent $PSScriptRoot
$missing = 0

function Check($label, $ok, $fix) {
    if ($ok) { "OK       $label" }
    else { $script:missing++; "MISSING  $label    -> $fix" }
}

$tools = @(
    @{ Cmd = 'python'; Id = 'Python.Python.3.12' },
    @{ Cmd = 'yt-dlp'; Id = 'yt-dlp.yt-dlp' },
    @{ Cmd = 'ffmpeg'; Id = 'Gyan.FFmpeg' },
    @{ Cmd = 'deno';   Id = 'DenoLand.Deno' },
    @{ Cmd = 'git';    Id = 'Git.Git' },
    @{ Cmd = 'gh';     Id = 'GitHub.cli' }
)
foreach ($t in $tools) {
    $found = [bool](Get-Command $t.Cmd -ErrorAction SilentlyContinue)
    Check $t.Cmd $found "winget install --id $($t.Id) --exact"
    if (-not $found -and $Install) { winget install --id $t.Id --exact }
}

$edge = "C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
Check 'Microsoft Edge (renders the PDF)' (Test-Path $edge) 'install Edge'

$py = [bool](Get-Command python -ErrorAction SilentlyContinue)
$hasMu = $false
if ($py) { python -c "import pymupdf" 2>$null; $hasMu = ($LASTEXITCODE -eq 0) }
Check 'python package pymupdf' $hasMu "python -m pip install --user -r requirements.txt"
if ($py -and -not $hasMu -and $Install) { python -m pip install --user -r "$repo\requirements.txt" }

$watch = Get-ChildItem "$env:USERPROFILE\.claude\plugins\cache\claude-video\watch\*\skills\watch\scripts\watch.py" -ErrorAction SilentlyContinue |
    Sort-Object FullName | Select-Object -Last 1
Check 'Claude Code plugin watch@claude-video' ([bool]$watch) 'in Claude Code: /plugin marketplace add bradautomates/claude-video , then /plugin install watch@claude-video'

if ($watch) {
    $setup = Join-Path (Split-Path $watch.FullName) 'setup.py'
    $envFile = "$env:USERPROFILE\.config\watch\.env"
    $local = (Test-Path $envFile) -and (Select-String -Path $envFile -Pattern '^WATCH_ENGINE="?local"?\s*$' -Quiet)
    Check 'watch engine set to local (no API key needed)' $local "python `"$setup`" --engine local"
    if (-not $local -and $Install) { python $setup --engine local }
}

gh auth status *> $null
Check 'gh logged in to GitHub' ($LASTEXITCODE -eq 0) 'gh auth login'

""
if ($missing -eq 0) { "All set." } else { "$missing item(s) missing. Re-run with -Install, or run the command shown." }
