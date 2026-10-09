# Download one video and produce a study report (captions + frames) with the local engine. No API key needed.
#   .\scripts\study-video.ps1 -Url https://www.youtube.com/watch?v=VIDEOID -OutDir D:\work\VIDEOID
# Output: OutDir\report.md (stdout of watch.py), plus frames and the downloaded video under OutDir\watch-*\
# Long videos (hours) take a long time. Use -DryRun to see the command first.
param(
    [Parameter(Mandatory)][string]$Url,
    [Parameter(Mandatory)][string]$OutDir,
    [string]$Detail = 'balanced',
    [string]$Question = 'Extract the complete trading strategy as explicit rules: structure, bias, areas of interest, entries, confluences, stops, targets, risk.',
    [switch]$DryRun
)

$watch = Get-ChildItem "$env:USERPROFILE\.claude\plugins\cache\claude-video\watch\*\skills\watch\scripts\watch.py" -ErrorAction Stop |
    Sort-Object FullName | Select-Object -Last 1
$argsList = @($watch.FullName, $Url, '--engine', 'local', '--detail', $Detail, '--question', $Question, '--out-dir', $OutDir)

if ($DryRun) { "python " + (($argsList | ForEach-Object { if ($_ -match '\s') { "`"$_`"" } else { $_ } }) -join ' '); return }

New-Item -ItemType Directory -Force $OutDir | Out-Null
$env:PYTHONUTF8 = '1'
[Console]::OutputEncoding = [Text.Encoding]::UTF8
python @argsList | Set-Content -Encoding UTF8 (Join-Path $OutDir 'report.md')
"Report: $(Join-Path $OutDir 'report.md')"
