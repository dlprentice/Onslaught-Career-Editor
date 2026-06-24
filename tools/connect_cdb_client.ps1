param(
    [string]$Server = "127.0.0.1",
    [int]$Port = 5005,
    [string]$Password = "secret",
    [switch]$PrintOnly
)

$ErrorActionPreference = "Stop"

if ($Password -notmatch '^[A-Za-z0-9_]+$') {
    Write-Error "Password must contain only letters, digits, or underscores. CDB can reject punctuation in TCP server passwords."
    exit 1
}

$scriptRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$cdbPath = & (Join-Path $scriptRoot "get_cdb_path.ps1") -AsLiteral

$arguments = @(
    "-remote", ("tcp:server={0},port={1},password={2}" -f $Server, $Port, $Password),
    "-bonc"
)

$commandPreview = '& "{0}" {1}' -f $cdbPath, (($arguments | ForEach-Object {
    if ($_ -match '\s') { '"{0}"' -f $_ } else { $_ }
}) -join ' ')

if ($PrintOnly) {
    Write-Output $commandPreview
    exit 0
}

& $cdbPath @arguments
