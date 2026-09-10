<#
    make_patch.ps1 - build one THOR patch for the MIDNIGHT RO launcher and
    publish it to the `patches` release of the patch repository.

    Usage:
        # everything that changed since the last published patch
        .\make_patch.ps1 -Name thai-ui-fix

        # an explicit list of client-relative paths
        .\make_patch.ps1 -Name hotfix -Files "DATA.INI","thai_ui.grf"

        # build locally without touching GitHub
        .\make_patch.ps1 -Name test -NoUpload

        # only record the current client state as "what players have"
        .\make_patch.ps1 -SnapshotOnly

    Hard rules enforced here (see BUGS.md 063-069 and PROJECT_PLAN.md):
      * loose-file mode remains the default for the game directory and GRF
        0x300 bases; explicit member-merging is allowed only for a named GRF
        0x200 target such as midnight.grf.
      * no huge GRFs, no backups, no per-user state, no running launcher exe.
      * patch indexes only ever increase; released patches are never rewritten.
      * every produced .thor must actually carry a THOR header (BUG-068).
#>
[CmdletBinding()]
param(
    [ValidatePattern('^[a-z0-9][a-z0-9-]*$')]
    [string]$Name,

    [string[]]$Files,

    # Client-relative paths to remove when applying this patch. This is kept
    # explicit because deletions cannot be discovered from the current client
    # directory and must never be inferred from a missing local file.
    [string[]]$RemoveFiles,

    [string]$ClientDir       = '',
    [string]$BaselineArchive = '',
    [string]$Repo            = 'midnightro/patcher',
    [string]$ReleaseTag      = 'patches',
    [switch]$NoUpload,

    # Future custom-asset patches can carry individual members and merge them
    # into the GRF 0x200 archive instead of replacing the whole archive.
    [switch]$UseGrfMerging,
    [string]$TargetGrfName = 'midnight.grf',
    [string]$PatchDataDir,

    # One-time bootstrap only: permit the complete midnight.grf in a loose-file
    # migration patch. Other large/base GRFs remain blocked.
    [switch]$AllowLargeMidnightMigration,

    # MidnightRO.yml is normally protected because a bad config can disable
    # updates for everyone. Use this only for a reviewed, explicit file list.
    [switch]$AllowLauncherConfig,

    # Write released_state.json from the client as it is right now, then exit.
    [switch]$SnapshotOnly
)

$ErrorActionPreference = 'Stop'
$sevenZip = 'C:\Program Files\7-Zip\7z.exe'

$mkpatchCandidates = @(
    (Join-Path $PSScriptRoot '..\bin\mkpatch.exe'),
    (Join-Path $PSScriptRoot '..\..\..\MidnightROClient\tools\mkpatch.exe'),
    (Join-Path $PSScriptRoot '..\..\rpatchur\mkpatch.exe')
)
$mkpatch = $null
foreach ($cand in $mkpatchCandidates) {
    if (Test-Path $cand) { $mkpatch = (Resolve-Path $cand).Path; break }
}
if (-not $mkpatch) { throw "Required tool mkpatch.exe not found in candidates." }
if (-not (Test-Path $sevenZip)) { throw "Required tool not found: $sevenZip" }

if (-not $ClientDir) {
    $clientCandidates = @(
        (Join-Path $PSScriptRoot '..\..\..\MidnightROClient'),
        (Join-Path $PSScriptRoot '..\..\..\server\Client'),
        (Join-Path $PSScriptRoot '..\..\Client')
    )
    foreach ($cand in $clientCandidates) {
        if (Test-Path $cand) { $ClientDir = (Resolve-Path $cand).Path; break }
    }
} else {
    $ClientDir = (Resolve-Path $ClientDir).Path
}
if (-not $ClientDir -or -not (Test-Path $ClientDir)) { throw "Client directory not found: $ClientDir" }

$dataIniSafetyPath = Join-Path $ClientDir 'DATA.INI'
if ((Test-Path -LiteralPath $dataIniSafetyPath) -and
    (Get-Content -LiteralPath $dataIniSafetyPath -Raw) -match '(?im)^\s*\d+\s*=\s*server_Local_endpoint\.grf\s*$') {
    throw ('DATA.INI is in Local developer mode. Run ' +
        '.\tools\client-patch\set_client_endpoint.ps1 -Mode Production before building or publishing a patch.')
}
$patchDataRoot = $ClientDir
if ($UseGrfMerging) {
    if (-not $Files) { throw '-UseGrfMerging requires an explicit -Files list.' }
    if (-not $PatchDataDir) { throw '-UseGrfMerging requires -PatchDataDir.' }
    $patchDataRoot = (Resolve-Path $PatchDataDir).Path
    if ($TargetGrfName -notmatch '^[A-Za-z0-9_.-]+\.grf$') {
        throw "Unsafe target GRF name: $TargetGrfName"
    }
} elseif ($PatchDataDir) {
    throw '-PatchDataDir is only valid with -UseGrfMerging.'
}
if ($AllowLargeMidnightMigration -and ($UseGrfMerging -or -not $Files)) {
    throw '-AllowLargeMidnightMigration is valid only for an explicit loose-file migration patch.'
}
$stamp     = Get-Date -Format 'yyyyMMdd_HHmm'
$today     = Get-Date -Format 'yyyyMMdd'

$defsDir     = Join-Path $PSScriptRoot 'patch_defs'
$releasedDir = Join-Path $PSScriptRoot 'released'
$stagingRoot = Join-Path $PSScriptRoot 'staging'
$plist       = Join-Path $PSScriptRoot 'plist.txt'
$stateFile   = Join-Path $PSScriptRoot 'released_state.json'
$patchStatus = Join-Path $PSScriptRoot 'patch_status.js'
foreach ($d in @($defsDir, $releasedDir, $stagingRoot)) {
    if (-not (Test-Path $d)) { New-Item -ItemType Directory -Force $d | Out-Null }
}
if (-not (Test-Path $plist)) { New-Item -ItemType File $plist | Out-Null }

# --------------------------------------------------------------- exclusions
# Same shape as tools\pack_client.ps1: working files, per-user state, backups.
$excludeDirs = @(
    'savedata', 'ScreenShot', 'Replay', 'memo', 'tmp',
    'ai_system_ui_assets', 'custom_ai_system',
    # Guild emblem cache the game writes while playing - not part of the client.
    'emblem',
    # The webview holds the UI page open for the whole session, so patching it
    # fails with "os error 32" and takes the whole patch down (BUG-069).
    'launcher_ui',
    # Retired two-process launcher directory; never let stale files return.
    'launcher'
)
$excludePatterns = @(
    '*.bak', '*.bak_*', '*.before_*', '*.orig_backup', '*.old_v*', '*.old_*',
    '*.en_backup', '*.kr_backup', '*.broken_*', '*.status_font_*',
    '*.log', 'Thumbs.db', 'desktop.ini', 'CLIENT-CHECK-RESULT.txt',
    # Optional developer override. It must never be published; Ragexe crashes
    # if DATA.INI names this archive on a machine where the file is absent.
    'server_Local_endpoint.grf',
    # The launcher cannot replace itself while running. MidnightRO.yml is
    # guarded separately and is allowed only with -AllowLauncherConfig.
    'MidnightRO.exe',
    'MidnightRO-Patcher.exe', 'MidnightRO-Patcher.yml',
    # Runtime state the launcher writes next to itself: the .lock exists while
    # it runs and the .dat cache is per-player.
    '*.lock', '*.dat'
)
# GRFs bigger than this are shipped out of band, not inside a patch.
$grfSizeLimitMB = 8

function Test-Win1252Safe {
    param([string]$Path)
    # THOR stores entry paths as windows-1252. A Thai/Korean name makes mkpatch
    # fail while writing the file table, and it still exits 0 (BUG-068).
    foreach ($ch in $Path.ToCharArray()) {
        if ([int]$ch -gt 255) { return $false }
    }
    return $true
}

function Test-Excluded {
    param([string]$RelPath)
    $leaf = Split-Path $RelPath -Leaf
    if ($leaf -eq 'MidnightRO.yml' -and -not $AllowLauncherConfig) { return $true }
    foreach ($d in $excludeDirs) {
        if ($RelPath -like "$d\*" -or $RelPath -eq $d) { return $true }
    }
    foreach ($p in $excludePatterns) {
        if ($leaf -like $p) { return $true }
    }
    if ($leaf -match '\.grf\.') { return $true }
    if ($leaf -eq 'data.grf') { return $true }
    return $false
}

function Initialize-Crc32 {
    if ('ProjectRO.Crc32' -as [type]) { return }
    Add-Type -TypeDefinition @'
using System;
using System.IO;
namespace ProjectRO {
    public static class Crc32 {
        static readonly uint[] T = Build();
        static uint[] Build() {
            uint[] t = new uint[256];
            for (uint i = 0; i < 256; i++) {
                uint c = i;
                for (int k = 0; k < 8; k++) c = ((c & 1) != 0) ? (0xEDB88320u ^ (c >> 1)) : (c >> 1);
                t[i] = c;
            }
            return t;
        }
        public static string File(string path) {
            uint crc = 0xFFFFFFFFu;
            byte[] buf = new byte[1 << 20];
            using (FileStream fs = new FileStream(path, FileMode.Open, FileAccess.Read, FileShare.ReadWrite, buf.Length)) {
                int n;
                while ((n = fs.Read(buf, 0, buf.Length)) > 0)
                    for (int i = 0; i < n; i++) crc = T[(crc ^ buf[i]) & 0xFF] ^ (crc >> 8);
            }
            return (crc ^ 0xFFFFFFFFu).ToString("X8");
        }
    }
}
'@
}

function Write-ReleasedState {
    # Snapshot of everything a patch could carry, so the next diff sees only
    # real changes instead of re-shipping every file that ever changed.
    Initialize-Crc32
    $state = @{}
    foreach ($f in (Get-ChildItem -Path $ClientDir -Recurse -File)) {
        $rel = $f.FullName.Substring($ClientDir.Length + 1)
        if (Test-Excluded -RelPath $rel) { continue }
        if (-not (Test-Win1252Safe -Path $rel)) { continue }
        $state[$rel.ToLowerInvariant()] = [ProjectRO.Crc32]::File($f.FullName)
    }
    if (Test-Path $stateFile) {
        Copy-Item $stateFile ("{0}.bak_{1}" -f $stateFile, $stamp) -Force
    }
    $json = ($state | ConvertTo-Json).Replace("`r`n", "`n") + "`n"
    [IO.File]::WriteAllText($stateFile, $json, [Text.UTF8Encoding]::new($false))
    Write-Host ("released_state.json updated ({0} files)" -f $state.Count) -ForegroundColor Cyan
}

if ($SnapshotOnly) {
    Write-ReleasedState
    return
}
if (-not $Name) { throw 'Specify -Name <patch-name> (or -SnapshotOnly).' }

# ------------------------------------------------------- pick the file list
if ($Files) {
    $relPaths = @($Files)
} else {
    # Diff against what players already have (the state left by the last patch),
    # falling back to the hand-delivered archive when there is no state yet.
    $useState = Test-Path $stateFile
    if (-not $useState -and -not (Test-Path $BaselineArchive)) {
        throw "No released_state.json and no baseline archive at $BaselineArchive"
    }
    if ($useState) {
        Write-Host "Diffing client against released state: $stateFile" -ForegroundColor Cyan
    } else {
        Write-Host "Diffing client against baseline archive: $BaselineArchive" -ForegroundColor Cyan
    }

    Initialize-Crc32
    $baseline = @{}
    if ($useState) {
        $json = Get-Content $stateFile -Raw | ConvertFrom-Json
        foreach ($prop in $json.PSObject.Properties) { $baseline[$prop.Name] = $prop.Value }
    } else {
        # -sccUTF-8: emit archive paths as UTF-8 so non-ASCII names (Korean/Thai
        # texture folders) match what PowerShell reads from disk.
        $curPath = $null
        & $sevenZip l -slt -sccUTF-8 $BaselineArchive | ForEach-Object {
            if ($_ -match '^Path = (.+)$') { $curPath = $matches[1] }
            elseif ($_ -match '^CRC = ([0-9A-Fa-f]+)$' -and $curPath) {
                $rel = $curPath
                if ($rel.Length -gt 7 -and $rel.Substring(0,7).ToLowerInvariant() -eq ('client' + [char]92)) {
                    $rel = $rel.Substring(7)
                }
                $baseline[$rel.ToLowerInvariant()] = $matches[1].ToUpperInvariant()
                $curPath = $null
            }
        }
    }
    if ($baseline.Count -eq 0) { throw 'Baseline produced no CRC entries' }
    Write-Host ("Baseline entries: {0}" -f $baseline.Count)

    $relPaths = @()
    foreach ($f in (Get-ChildItem -Path $ClientDir -Recurse -File)) {
        $rel = $f.FullName.Substring($ClientDir.Length + 1)
        if (Test-Excluded -RelPath $rel) { continue }
        $key = $rel.ToLowerInvariant()
        if ($baseline.ContainsKey($key)) {
            if ([ProjectRO.Crc32]::File($f.FullName) -eq $baseline[$key]) { continue }
        }
        if (-not (Test-Win1252Safe -Path $rel)) {
            Write-Host ("  ! skipped (non-windows-1252 path): {0}" -f $rel) -ForegroundColor Yellow
            continue
        }
        $relPaths += $rel
    }
}

$removeRelPaths = @($RemoveFiles | Where-Object { $_ -and $_.Trim() -ne '' })

if ((-not $relPaths -or $relPaths.Count -eq 0) -and $removeRelPaths.Count -eq 0) {
    Write-Host 'Nothing to patch - the client matches what players already have.' -ForegroundColor Yellow
    return
}

# ------------------------------------------------------------ verify + stage
$problems = @()
foreach ($rel in $relPaths) {
    if ([IO.Path]::IsPathRooted($rel) -or $rel -match '(^|[\/])\.\.([\/]|$)') {
        $problems += "unsafe file path: $rel"
        continue
    }
    $full = Join-Path $patchDataRoot $rel
    if (-not (Test-Path $full)) { $problems += "file does not exist: $rel"; continue }
    if (-not (Test-Win1252Safe -Path $rel)) {
        $problems += ("non-windows-1252 character in path: {0} - pack this file into a GRF instead" -f $rel)
        continue
    }
    if (Test-Excluded -RelPath $rel) { $problems += "excluded file in patch: $rel"; continue }
    $item = Get-Item $full
    $largeMidnightMigration =
        $AllowLargeMidnightMigration -and
        -not $UseGrfMerging -and
        $rel.ToLowerInvariant() -eq 'midnight.grf'
    if ($item.Extension -eq '.grf' -and $item.Length / 1MB -gt $grfSizeLimitMB -and -not $largeMidnightMigration) {
        $problems += ("GRF too large for a patch ({0:N0} MB): {1} - ship it out of band" -f ($item.Length / 1MB), $rel)
    }
}
foreach ($rel in $removeRelPaths) {
    if ([IO.Path]::IsPathRooted($rel) -or $rel -match '(^|[\\/])\.\.([\\/]|$)') {
        $problems += "unsafe removal path: $rel"
        continue
    }
    if (-not (Test-Win1252Safe -Path $rel)) {
        $problems += "non-windows-1252 removal path: $rel"
        continue
    }
    # Per-user state and launcher files are normally excluded from every patch.
    # Cleanup may remove only explicitly named retired launcher families and UI
    # paths. The active MidnightRO.exe/.yml/.dat/.lock remain protected.
    $legacyLauncherRemoval =
        $rel -match '(?i)^(MidnightRO-(Patcher|Launcher)|MidnightROClient|MIDNIGHT RO)\.(exe|yml|dat|lock)$' -or
        $rel -match '(?i)^MidnightRO-v\d+\.(exe|yml|dat|lock)$' -or
        $rel -match '(?i)^(MIDNIGHT RO|START-MIDNIGHT-RO)\.bat$' -or
        $rel -match '(?i)^launcher[\\/](MidnightRO-Patcher\.(exe|yml|dat|lock))$' -or
        $rel -match '(?i)^launcher_ui(_v\d+)?[\\/]'
    $removalException =
        $rel.ToLowerInvariant() -eq 'savedata\chatwndinfo_u.lua' -or
        $legacyLauncherRemoval
    if ((Test-Excluded -RelPath $rel) -and -not $removalException) {
        $problems += "excluded removal path: $rel"
    }
}
if ($problems) {
    Write-Host 'PATCH ABORTED:' -ForegroundColor Red
    $problems | ForEach-Object { Write-Host ("  - " + $_) -ForegroundColor Red }
    throw 'verification failed'
}

# next index = last index in plist.txt + 1
$lastIndex = 0
foreach ($line in (Get-Content $plist)) {
    if ($line -match '^\s*(\d+)\s+\S+') {
        $i = [int]$matches[1]
        if ($i -gt $lastIndex) { $lastIndex = $i }
    }
}
$index    = $lastIndex + 1
$thorName = ('{0:0000}_{1}_{2}.thor' -f $index, $today, $Name)
$thorPath = Join-Path $releasedDir $thorName
if (Test-Path $thorPath) { throw "A patch with this name already exists: $thorPath" }

$stage = Join-Path $stagingRoot ('{0:0000}_{1}' -f $index, $stamp)
if (Test-Path $stage) { Remove-Item -Recurse -Force $stage }
New-Item -ItemType Directory -Force $stage | Out-Null

foreach ($rel in $relPaths) {
    $dest = Join-Path $stage $rel
    $destDir = Split-Path $dest -Parent
    if (-not (Test-Path $destDir)) { New-Item -ItemType Directory -Force $destDir | Out-Null }
    Copy-Item -LiteralPath (Join-Path $patchDataRoot $rel) -Destination $dest -Force
    Write-Host ("  + {0}" -f $rel)
}
$entryCount = $relPaths.Count + $removeRelPaths.Count
Write-Host ("Staged {0} added/replaced and {1} removed file(s) for patch {2:0000}" -f $relPaths.Count, $removeRelPaths.Count, $index) -ForegroundColor Cyan

# ------------------------------------------------------- patch definition
$defPath = Join-Path $defsDir ('{0:0000}_{1}_{2}.yml' -f $index, $today, $Name)
$def = New-Object System.Collections.Generic.List[string]
$def.Add('# Generated by tools/patcher/make_patch.ps1 - do not edit by hand.')
if ($UseGrfMerging) {
    $def.Add('# Member-level patch for the MIDNIGHT RO GRF 0x200 custom archive.')
    $def.Add('use_grf_merging: true')
    $def.Add(("target_grf_name: {0}" -f $TargetGrfName))
} else {
    $def.Add('# Loose-file patch for the game directory or one-time GRF migration.')
    $def.Add('use_grf_merging: false')
}
$def.Add('include_checksums: true')
$def.Add('entries:')
foreach ($rel in $relPaths) {
    $def.Add(("  - relative_path: {0}" -f $rel))
}
foreach ($rel in $removeRelPaths) {
    $def.Add(("  - relative_path: {0}" -f $rel))
    $def.Add('    is_removed: true')
}
# serde_yaml rejects a UTF-8 BOM, so write the definition without one.
[IO.File]::WriteAllText($defPath, (($def -join "`n") + "`n"), (New-Object Text.UTF8Encoding($false)))

$defCheck = Get-Content $defPath -Raw
if ($UseGrfMerging) {
    if ($defCheck -notmatch '(?m)^use_grf_merging:\s*true\s*$' -or
        $defCheck -notmatch ("(?m)^target_grf_name:\s*{0}\s*$" -f [regex]::Escape($TargetGrfName))) {
        throw 'Generated patch definition does not enable the requested GRF target.'
    }
} elseif ($defCheck -notmatch '(?m)^use_grf_merging:\s*false\s*$') {
    throw 'Generated patch definition does not set use_grf_merging: false.'
}

# --------------------------------------------------------------- build
Write-Host "Building $thorName ..." -ForegroundColor Cyan
& $mkpatch $defPath -p $stage -o $thorPath
if ($LASTEXITCODE -ne 0) { throw "mkpatch failed with exit code $LASTEXITCODE" }
if (-not (Test-Path $thorPath)) { throw "mkpatch produced no output at $thorPath" }

# mkpatch writes the header in a destructor and swallows failures, so a
# "successful" run can still leave an archive with no magic at all (BUG-068).
$magic = [Text.Encoding]::ASCII.GetString([IO.File]::ReadAllBytes($thorPath)[0..23])
if ($magic -ne 'ASSF (C) 2007 Aeomin DEV') {
    Remove-Item $thorPath -Force
    throw "mkpatch produced an archive with no THOR header (magic was '$magic'). The patch was NOT created."
}

$thorHash = (Get-FileHash $thorPath -Algorithm SHA256).Hash
$thorSize = [math]::Round((Get-Item $thorPath).Length / 1MB, 2)
Write-Host ("Built {0} ({1} MB)" -f $thorName, $thorSize) -ForegroundColor Green
Write-Host ("SHA-256 {0}" -f $thorHash)

# --------------------------------------------------------------- plist.txt
Copy-Item $plist ("{0}.bak_{1}_before_{2:0000}" -f $plist, $stamp, $index) -Force
$plistLines = @(Get-Content $plist | Where-Object { $_.Trim() -ne '' })
$plistLines += ("{0} {1}" -f $index, $thorName)
# LF endings, no trailing blank line: the patcher parses this line by line.
[IO.File]::WriteAllText($plist, (($plistLines -join "`n") + "`n"), (New-Object Text.UTF8Encoding($false)))
Write-Host "plist.txt updated:" -ForegroundColor Cyan
Get-Content $plist | ForEach-Object { Write-Host ("  " + $_) }

# The Launcher UI cannot read plist.txt with XHR because the release asset is
# cross-origin. Publish the same latest index as ES5 JavaScript, which MSHTML
# can load through a cache-busted <script> tag. This is generated for every
# patch so the UI never needs another hand-edited N/N count.
$statusTimestamp = Get-Date -Format 'yyyy-MM-ddTHH:mm:ssK'
$statusLines = @(
    '/* Generated by tools/patcher/make_patch.ps1 after plist.txt is updated.'
    '   Loaded by the Launcher UI as a cross-origin script; keep this ES5. */'
    'window.MIDNIGHT_PATCH_STATUS = {'
    ("    latestIndex: {0}," -f $index)
    ("    latestFile: '{0}'," -f $thorName)
    ("    updatedAt: '{0}'" -f $statusTimestamp)
    '};'
)
[IO.File]::WriteAllText($patchStatus, (($statusLines -join "`n") + "`n"), (New-Object Text.UTF8Encoding($false)))
Write-Host ("Launcher patch status updated: {0}/{0} ({1})" -f $index, $thorName) -ForegroundColor Cyan

# --------------------------------------------------------------- upload
if ($NoUpload) {
    Write-Host "-NoUpload set: skipping GitHub release upload and state snapshot." -ForegroundColor Yellow
} else {
    Write-Host "Uploading to $Repo release '$ReleaseTag' ..." -ForegroundColor Cyan
    & gh release upload $ReleaseTag $thorPath --repo $Repo --clobber
    if ($LASTEXITCODE -ne 0) { throw "gh release upload failed for $thorName" }
    # Upload dynamic UI status before plist.txt. If this fails, the new patch
    # is not published in the list and players stay on the previous index.
    & gh release upload $ReleaseTag $patchStatus --repo $Repo --clobber
    if ($LASTEXITCODE -ne 0) { throw 'gh release upload failed for patch_status.js' }
    & gh release upload $ReleaseTag $plist --repo $Repo --clobber
    if ($LASTEXITCODE -ne 0) { throw 'gh release upload failed for plist.txt' }
    Write-Host "Uploaded patch, dynamic Launcher status, and plist." -ForegroundColor Green

    # Players now have this state; the next patch diffs against it.
    Write-ReleasedState
}

Remove-Item -Recurse -Force $stage
Write-Host ""
Write-Host ("DONE - patch {0:0000} '{1}' with {2} entries" -f $index, $Name, $entryCount) -ForegroundColor Green
Write-Host "Log this in changelog/03-client-grf-lua.md with the SHA-256 above."
