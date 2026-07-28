# SPDX-License-Identifier: GPL-3.0-or-later
<#
.SYNOPSIS
Record a moment of retail Battle Engine Aquila with Time Travel Debugging,
while you are already playing it.

.DESCRIPTION
TTD instruments every instruction, so a game launched under it is a slideshow.
This attaches to a game that is ALREADY RUNNING at full speed, records for a
fixed number of seconds, then detaches and LEAVES THE GAME RUNNING so you can
carry on and record another moment later.

Recording needs an elevated token and this machine has no TTDService, so there
is one UAC prompt per recording. This script raises it for you.

.EXAMPLE
Play until a drone is attacking you, then:

    pwsh -File tools\Record-GameMoment.ps1 -Name dodge-beat -Seconds 45

.EXAMPLE
Longer capture of a fight, with a bigger ceiling:

    pwsh -File tools\Record-GameMoment.ps1 -Name combat -Seconds 90 -MaxFileMB 65536
#>
[CmdletBinding()]
param(
    # Short label. Becomes the trace directory under G:\bea-ttd\.
    [Parameter(Mandatory = $true)][string]$Name,

    # How long to record, in seconds. Cost is roughly 1.8 GB per minute, so 60 s
    # is about 1.8 GB. Short and targeted beats long and vague: a 45-second trace
    # of the exact moment answers more than 13 minutes of approach.
    [int]$Seconds = 60,

    # Ceiling on the trace file. The default here is deliberately smaller than
    # the recorder's, because an attach capture is meant to be a moment. Raise it
    # if you are recording something genuinely long.
    [int]$MaxFileMB = 8192
)

$ErrorActionPreference = 'Stop'
$repo = Split-Path $PSScriptRoot -Parent
$rec  = Join-Path $PSScriptRoot 'ttd_record.ps1'
$exe  = Join-Path $repo 'local-lab\safe-copy-bea-pristine\BEA.exe'

# Check the game is up BEFORE raising UAC. Prompting for elevation and then
# failing on "no game running" wastes a consent dialog and a screen blackout.
$running = @(Get-Process -Name 'BEA' -ErrorAction SilentlyContinue |
    Where-Object { $_.Path -ieq $exe })
if ($running.Count -eq 0) {
    Write-Host ''
    Write-Warning 'No copied-target BEA is running, so there is nothing to attach to.'
    Write-Host ''
    Write-Host 'Start the game first, at full speed, from:'
    Write-Host "  $exe"
    Write-Host 'Play to the moment you want captured, then run this again.'
    Write-Host ''
    exit 2
}

$elevated = ([Security.Principal.WindowsPrincipal] `
    [Security.Principal.WindowsIdentity]::GetCurrent()
    ).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

if (-not $elevated) {
    Write-Host ''
    Write-Host "Found the game (PID $($running[0].Id)). Raising the elevation prompt now."
    Write-Host 'Approve it and go back to the game - recording starts immediately.'
    Write-Host ''
    $self = $MyInvocation.MyCommand.Path
    Start-Process -FilePath 'pwsh.exe' -Verb RunAs -ArgumentList @(
        '-NoProfile', '-ExecutionPolicy', 'Bypass', '-File', $self,
        '-Name', $Name, '-Seconds', "$Seconds", '-MaxFileMB', "$MaxFileMB")
    exit 0
}

Write-Host ''
Write-Host '================================================================'
Write-Host ("  RECORDING '{0}' for {1} seconds." -f $Name, $Seconds)
Write-Host '  Go back to the game NOW. It will slow down while recording.'
Write-Host '  It speeds back up and KEEPS RUNNING when this finishes.'
Write-Host '================================================================'
Write-Host ''

& $rec -Name $Name -Attach -Seconds $Seconds -MaxFileMB $MaxFileMB
$code = $LASTEXITCODE

Write-Host ''
if ($code -eq 0) {
    Write-Host '================================================================'
    Write-Host ("  DONE. Trace is at G:\bea-ttd\{0}\." -f $Name)
    Write-Host '  The game is still running - keep playing, record again when'
    Write-Host '  you reach another moment worth capturing.'
    Write-Host '================================================================'
} else {
    Write-Warning ("Recorder exited {0} - see the messages above." -f $code)
}
Write-Host ''
Read-Host 'Press Enter to close'
exit $code
