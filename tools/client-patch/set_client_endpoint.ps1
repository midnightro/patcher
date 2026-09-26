<#
Switch the development Client between the safe production GRF list and the
optional Local endpoint override. Production mode must be active before any
patch or distributable package is built.
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [ValidateSet('Local', 'Production')]
    [string]$Mode,
    [string]$ClientDir = ''
)

$ErrorActionPreference = 'Stop'
if (-not $ClientDir) {
    $ClientDir = Join-Path $PSScriptRoot '..\..\..\MidnightROClient'
}
$ClientDir = (Resolve-Path -LiteralPath $ClientDir).Path
$dataIni = Join-Path $ClientDir 'DATA.INI'
$localGrf = Join-Path $ClientDir 'server_Local_endpoint.grf'

if ($Mode -eq 'Local') {
    if (-not (Test-Path -LiteralPath $localGrf -PathType Leaf)) {
        throw "Local endpoint GRF not found: $localGrf"
    }
    $grfs = @(
        'server_Local_endpoint.grf',
        'new_player_nfs.grf',
        'item_move_free.grf',
        'midnight.grf',
        'new_ai_final.grf',
        'data.grf'
    )
} else {
    $grfs = @(
        'new_player_nfs.grf',
        'item_move_free.grf',
        'midnight.grf',
        'new_ai_final.grf',
        'data.grf'
    )
}

foreach ($grf in $grfs) {
    if (-not (Test-Path -LiteralPath (Join-Path $ClientDir $grf) -PathType Leaf)) {
        throw "Required GRF not found: $grf"
    }
}

$lines = @('[Data]')
for ($index = 0; $index -lt $grfs.Count; $index++) {
    $lines += "$index=$($grfs[$index])"
}
[IO.File]::WriteAllText(
    $dataIni,
    (($lines -join "`r`n") + "`r`n"),
    [Text.Encoding]::ASCII
)

Write-Host "Client endpoint mode: $Mode" -ForegroundColor Green
$lines | ForEach-Object { Write-Host $_ }
