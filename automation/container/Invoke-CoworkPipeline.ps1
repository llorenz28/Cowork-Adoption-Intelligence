#!/usr/bin/env pwsh
[CmdletBinding()]
param(
    [string]$DataRoot = $(if ($env:COWORK_DATA_ROOT) { $env:COWORK_DATA_ROOT } else { '/data' }),
    [string]$PaxScriptPath = $(if ($env:COWORK_PAX_SCRIPT) { $env:COWORK_PAX_SCRIPT } else { '/app/PAX_Purview_Audit_Log_Processor.ps1' }),
    [string]$PreprocessorPath = $(if ($env:COWORK_PREPROCESSOR) { $env:COWORK_PREPROCESSOR } else { '/app/Cowork_Purview_Preprocessor_v0.1.0.py' }),
    [string]$CompatibilityValidatorPath = $(if ($env:COWORK_COMPATIBILITY_VALIDATOR) { $env:COWORK_COMPATIBILITY_VALIDATOR } else { '/app/Validate-CoworkCompatibility.py' }),
    [string]$PythonCommand = $(if ($env:COWORK_PYTHON) { $env:COWORK_PYTHON } else { 'python3' }),
    [string]$PowerShellCommand = $(if ($env:COWORK_PWSH) { $env:COWORK_PWSH } else { 'pwsh' }),
    [string]$TenantId = $env:COWORK_TENANT_ID,
    [string]$ClientId = $(if ($env:AZURE_CLIENT_ID) { $env:AZURE_CLIENT_ID } else { $env:COWORK_CLIENT_ID }),
    [string]$InitialStartUtc = $env:COWORK_INITIAL_START_UTC,
    [int]$EndLagHours = $(if ($env:COWORK_END_LAG_HOURS) { [int]$env:COWORK_END_LAG_HOURS } else { 6 }),
    [int]$OverlapHours = $(if ($env:COWORK_OVERLAP_HOURS) { [int]$env:COWORK_OVERLAP_HOURS } else { 24 }),
    [int]$WindowHours = $(if ($env:COWORK_WINDOW_HOURS) { [int]$env:COWORK_WINDOW_HOURS } else { 24 }),
    [int]$MaxWindowsPerRun = $(if ($env:COWORK_MAX_WINDOWS_PER_RUN) { [int]$env:COWORK_MAX_WINDOWS_PER_RUN } else { 7 }),
    [double]$PaxBlockHours = $(if ($env:COWORK_PAX_BLOCK_HOURS) { [double]$env:COWORK_PAX_BLOCK_HOURS } else { 0.25 }),
    [int]$PaxMaxConcurrency = $(if ($env:COWORK_PAX_MAX_CONCURRENCY) { [int]$env:COWORK_PAX_MAX_CONCURRENCY } else { 6 }),
    [switch]$PreprocessOnly
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function ConvertFrom-UtcTimestamp {
    param([Parameter(Mandatory)][string]$Value)

    return [DateTimeOffset]::Parse(
        $Value,
        [Globalization.CultureInfo]::InvariantCulture,
        [Globalization.DateTimeStyles]::AssumeUniversal
    ).ToUniversalTime()
}

function ConvertTo-UtcTimestamp {
    param([Parameter(Mandatory)][DateTimeOffset]$Value)

    return $Value.UtcDateTime.ToString(
        'yyyy-MM-ddTHH:mm:ssZ',
        [Globalization.CultureInfo]::InvariantCulture
    )
}

function ConvertTo-PaxDate {
    param([Parameter(Mandatory)][DateTimeOffset]$Value)

    return $Value.UtcDateTime.ToString(
        'yyyy-MM-dd',
        [Globalization.CultureInfo]::InvariantCulture
    )
}

function Write-JsonAtomic {
    param(
        [Parameter(Mandatory)][string]$Path,
        [Parameter(Mandatory)][object]$Value
    )

    $parent = Split-Path -Parent $Path
    New-Item -ItemType Directory -Path $parent -Force | Out-Null
    $temporary = Join-Path $parent ('.{0}.tmp-{1}' -f ([IO.Path]::GetFileName($Path)), [guid]::NewGuid().ToString('N'))
    $json = $Value | ConvertTo-Json -Depth 20
    [IO.File]::WriteAllText($temporary, $json + [Environment]::NewLine, [Text.UTF8Encoding]::new($false))
    Move-Item -LiteralPath $temporary -Destination $Path -Force
}

function Invoke-NativeChecked {
    param(
        [Parameter(Mandatory)][string]$FilePath,
        [Parameter(Mandatory)][string[]]$Arguments,
        [Parameter(Mandatory)][string]$Label
    )

    & $FilePath @Arguments
    $exitCode = $LASTEXITCODE
    if ($exitCode -ne 0) {
        throw "$Label failed with exit code $exitCode."
    }
}

function Assert-SeparatePaths {
    param(
        [Parameter(Mandatory)][string]$InputPath,
        [Parameter(Mandatory)][string]$OutputPath
    )

    $inputFull = [IO.Path]::GetFullPath($InputPath).TrimEnd([IO.Path]::DirectorySeparatorChar, [IO.Path]::AltDirectorySeparatorChar)
    $outputFull = [IO.Path]::GetFullPath($OutputPath).TrimEnd([IO.Path]::DirectorySeparatorChar, [IO.Path]::AltDirectorySeparatorChar)
    $comparison = if ($IsWindows) { [StringComparison]::OrdinalIgnoreCase } else { [StringComparison]::Ordinal }
    $separator = [IO.Path]::DirectorySeparatorChar

    if ($inputFull.Equals($outputFull, $comparison) -or
        $inputFull.StartsWith($outputFull + $separator, $comparison) -or
        $outputFull.StartsWith($inputFull + $separator, $comparison)) {
        throw "Input and output paths must be separate and cannot contain each other."
    }
}

function Assert-OwnedOutput {
    param([Parameter(Mandatory)][string]$OutputPath)

    if (-not (Test-Path -LiteralPath $OutputPath -PathType Container)) {
        return
    }

    $children = @(Get-ChildItem -LiteralPath $OutputPath -Force)
    if ($children.Count -eq 0) {
        return
    }

    $manifestPath = Join-Path $OutputPath 'manifest.json'
    if (-not (Test-Path -LiteralPath $manifestPath -PathType Leaf)) {
        throw "Existing output is not owned by the Cowork preprocessor: $OutputPath"
    }

    $manifest = Get-Content -LiteralPath $manifestPath -Raw | ConvertFrom-Json
    if ($manifest.format -ne 'cowork-python-preprocessor-manifest-v1') {
        throw "Existing output has an unsupported manifest format: $OutputPath"
    }
}

function Get-WindowPlan {
    param(
        [Parameter(Mandatory)][DateTimeOffset]$Start,
        [Parameter(Mandatory)][DateTimeOffset]$End,
        [Parameter(Mandatory)][int]$Hours,
        [Parameter(Mandatory)][int]$Maximum
    )

    $result = [Collections.Generic.List[object]]::new()
    $cursor = $Start
    while ($cursor -lt $End -and $result.Count -lt $Maximum) {
        $windowEnd = $cursor.AddHours($Hours)
        if ($windowEnd -gt $End) {
            $windowEnd = $End
        }
        $result.Add([pscustomobject]@{ Start = $cursor; End = $windowEnd })
        $cursor = $windowEnd
    }
    return @($result)
}

function Invoke-PaxWindow {
    param(
        [Parameter(Mandatory)][DateTimeOffset]$Start,
        [Parameter(Mandatory)][DateTimeOffset]$End,
        [Parameter(Mandatory)][string]$StableAuditPath,
        [Parameter(Mandatory)][string]$IncomingRoot,
        [Parameter(Mandatory)][string]$LogsRoot,
        [Parameter(Mandatory)][string]$MetricsRoot,
        [Parameter(Mandatory)][string]$RunId
    )

    $windowLabel = '{0}-{1}' -f $Start.UtcDateTime.ToString('yyyyMMddHHmmss'), $End.UtcDateTime.ToString('yyyyMMddHHmmss')
    $metricsPath = Join-Path $MetricsRoot ("pax-$RunId-$windowLabel.json")
    $arguments = @(
        '-NoLogo', '-NoProfile', '-File', $PaxScriptPath,
        '-StartDate', (ConvertTo-PaxDate $Start),
        '-EndDate', (ConvertTo-PaxDate $End),
        '-ActivityTypes', 'CopilotInteraction',
        '-Auth', 'ManagedIdentity',
        '-TenantId', $TenantId,
        '-ClientId', $ClientId,
        '-BlockHours', ([string]::Format([Globalization.CultureInfo]::InvariantCulture, '{0}', $PaxBlockHours)),
        '-MaxConcurrency', $PaxMaxConcurrency.ToString([Globalization.CultureInfo]::InvariantCulture),
        '-CombineOutput',
        '-AutoCompleteness',
        '-EmitMetricsJson',
        '-MetricsPath', $metricsPath,
        '-OutputPathLog', $LogsRoot,
        '-Force'
    )

    if (Test-Path -LiteralPath $StableAuditPath -PathType Leaf) {
        $arguments += @('-AppendFile', $StableAuditPath)
        Invoke-NativeChecked -FilePath $PowerShellCommand -Arguments $arguments -Label "PAX window $windowLabel"
        return
    }

    $incoming = Join-Path $IncomingRoot $windowLabel
    New-Item -ItemType Directory -Path $incoming -Force | Out-Null
    $arguments += @('-OutputPath', $incoming)
    Invoke-NativeChecked -FilePath $PowerShellCommand -Arguments $arguments -Label "PAX window $windowLabel"

    $candidates = @(
        Get-ChildItem -LiteralPath $incoming -Recurse -File -Filter '*.csv' |
            Where-Object { $_.Name -like 'Purview_Audit*' -and $_.Name -notlike '*PARTIAL*' }
    )
    if ($candidates.Count -ne 1) {
        throw "Expected one PAX audit CSV for initial publication; found $($candidates.Count) in $incoming."
    }

    New-Item -ItemType Directory -Path (Split-Path -Parent $StableAuditPath) -Force | Out-Null
    Move-Item -LiteralPath $candidates[0].FullName -Destination $StableAuditPath
    Remove-Item -LiteralPath $incoming -Recurse -Force
}

function Invoke-CoworkPreprocessing {
    param(
        [Parameter(Mandatory)][string]$InputPath,
        [Parameter(Mandatory)][string]$OutputPath
    )

    Assert-OwnedOutput -OutputPath $OutputPath
    Invoke-NativeChecked -FilePath $PythonCommand -Arguments @(
        $PreprocessorPath, '--input', $InputPath, '--output', $OutputPath, '--quiet'
    ) -Label 'Cowork preprocessing'
    Invoke-NativeChecked -FilePath $PythonCommand -Arguments @(
        $PreprocessorPath, '--validate-output', $OutputPath, '--quiet'
    ) -Label 'Cowork output validation'

    $compatibilityJson = & $PythonCommand $CompatibilityValidatorPath --output $OutputPath
    $exitCode = $LASTEXITCODE
    if ($exitCode -ne 0) {
        throw "Cowork compatibility validation failed with exit code $exitCode."
    }
    return ($compatibilityJson | Out-String | ConvertFrom-Json)
}

if ($EndLagHours -lt 0) { throw 'EndLagHours must be zero or greater.' }
if ($OverlapHours -lt 0 -or $OverlapHours % 24 -ne 0) { throw 'OverlapHours must be zero or a whole number of days.' }
if ($WindowHours -lt 24 -or $WindowHours -gt 168 -or $WindowHours % 24 -ne 0) { throw 'WindowHours must be 24 to 168 and a whole number of days.' }
if ($MaxWindowsPerRun -lt 1 -or $MaxWindowsPerRun -gt 180) { throw 'MaxWindowsPerRun must be between 1 and 180.' }
if ($PaxBlockHours -lt 0.016667 -or $PaxBlockHours -gt 24) { throw 'PaxBlockHours must be between 0.016667 and 24.' }
if ($PaxMaxConcurrency -lt 1 -or $PaxMaxConcurrency -gt 20) { throw 'PaxMaxConcurrency must be between 1 and 20.' }

$runId = [guid]::NewGuid().ToString('N')
$started = [DateTimeOffset]::UtcNow
$root = [IO.Path]::GetFullPath($DataRoot)
$inputPath = Join-Path $root 'active'
$auditPath = Join-Path $inputPath 'purview_audit'
$stableAuditPath = Join-Path $auditPath 'CoworkPurviewAudit.csv'
$outputPath = Join-Path $root 'preprocessed'
$incomingRoot = Join-Path $root 'incoming'
$logsRoot = Join-Path $root 'logs'
$metricsRoot = Join-Path $root 'metrics'
$stateRoot = Join-Path $root 'state'
$statusRoot = Join-Path $root 'status'
$statePath = Join-Path $stateRoot 'watermark.json'
$latestStatusPath = Join-Path $statusRoot 'latest.json'
$historyStatusPath = Join-Path (Join-Path $statusRoot 'history') "$runId.json"
$lockPath = Join-Path $stateRoot 'pipeline.lock'
$lockStream = $null

New-Item -ItemType Directory -Path $inputPath, $auditPath, $incomingRoot, $logsRoot, $metricsRoot, $stateRoot, $statusRoot -Force | Out-Null
Assert-SeparatePaths -InputPath $inputPath -OutputPath $outputPath

try {
    try {
        $lockStream = [IO.File]::Open(
            $lockPath,
            [IO.FileMode]::OpenOrCreate,
            [IO.FileAccess]::ReadWrite,
            [IO.FileShare]::None
        )
    }
    catch {
        throw "Another Cowork pipeline execution already holds the data-root lock."
    }

    $lockStream.SetLength(0)
    $lockBytes = [Text.Encoding]::UTF8.GetBytes(
        (@{ runId = $runId; startedUtc = (ConvertTo-UtcTimestamp $started) } | ConvertTo-Json -Compress)
    )
    $lockStream.Write($lockBytes, 0, $lockBytes.Length)
    $lockStream.Flush()

    if (-not (Test-Path -LiteralPath $PreprocessorPath -PathType Leaf)) {
        throw "Cowork preprocessor not found: $PreprocessorPath"
    }
    if (-not (Test-Path -LiteralPath $CompatibilityValidatorPath -PathType Leaf)) {
        throw "Compatibility validator not found: $CompatibilityValidatorPath"
    }

    $windowPlan = @()
    $processedStart = $null
    $processedEnd = $null
    $targetEnd = $null
    $refreshRequired = $true

    if (-not $PreprocessOnly) {
        if (-not (Test-Path -LiteralPath $PaxScriptPath -PathType Leaf)) {
            throw "PAX script not found: $PaxScriptPath"
        }
        if ([string]::IsNullOrWhiteSpace($TenantId) -or [string]::IsNullOrWhiteSpace($ClientId)) {
            throw 'COWORK_TENANT_ID and AZURE_CLIENT_ID are required for managed-identity collection.'
        }

        $initial = if ([string]::IsNullOrWhiteSpace($InitialStartUtc)) {
            $null
        } else {
            $parsedInitial = ConvertFrom-UtcTimestamp $InitialStartUtc
            [DateTimeOffset]::new(
                $parsedInitial.Year, $parsedInitial.Month, $parsedInitial.Day,
                0, 0, 0, [TimeSpan]::Zero
            )
        }
        $watermark = $null
        if (Test-Path -LiteralPath $statePath -PathType Leaf) {
            $state = Get-Content -LiteralPath $statePath -Raw | ConvertFrom-Json
            $watermark = ConvertFrom-UtcTimestamp $state.lastSuccessfulEndUtc
        }
        elseif ($null -eq $initial) {
            throw 'Set COWORK_INITIAL_START_UTC for the first run.'
        }

        $collectionStart = if ($null -ne $watermark) {
            $watermark.AddHours(-$OverlapHours)
        } else {
            $initial
        }
        if ($null -ne $initial -and $collectionStart -lt $initial) {
            $collectionStart = $initial
        }

        $nowLagged = [DateTimeOffset]::UtcNow.AddHours(-$EndLagHours)
        $targetEnd = [DateTimeOffset]::new(
            $nowLagged.Year, $nowLagged.Month, $nowLagged.Day,
            0, 0, 0, [TimeSpan]::Zero
        )
        if ($collectionStart -gt $targetEnd) {
            throw "Collection start is later than the lagged target end. Check COWORK_INITIAL_START_UTC."
        }

        $windowPlan = Get-WindowPlan -Start $collectionStart -End $targetEnd -Hours $WindowHours -Maximum $MaxWindowsPerRun
        foreach ($window in $windowPlan) {
            Invoke-PaxWindow `
                -Start $window.Start `
                -End $window.End `
                -StableAuditPath $stableAuditPath `
                -IncomingRoot $incomingRoot `
                -LogsRoot $logsRoot `
                -MetricsRoot $metricsRoot `
                -RunId $runId
        }

        if ($windowPlan.Count -gt 0) {
            $processedStart = $windowPlan[0].Start
            $processedEnd = $windowPlan[-1].End
        }
        else {
            $refreshRequired = -not (Test-Path -LiteralPath (Join-Path $outputPath 'manifest.json') -PathType Leaf)
        }
    }

    if (-not (Test-Path -LiteralPath $stableAuditPath -PathType Leaf)) {
        throw "The active audit CSV is missing: $stableAuditPath"
    }

    $compatibility = $null
    if ($refreshRequired -or $PreprocessOnly) {
        $compatibility = Invoke-CoworkPreprocessing -InputPath $inputPath -OutputPath $outputPath
    }
    else {
        Invoke-NativeChecked -FilePath $PythonCommand -Arguments @(
            $PreprocessorPath, '--validate-output', $outputPath, '--quiet'
        ) -Label 'Cowork output validation'
        $compatibilityJson = & $PythonCommand $CompatibilityValidatorPath --output $outputPath
        if ($LASTEXITCODE -ne 0) {
            throw "Cowork compatibility validation failed with exit code $LASTEXITCODE."
        }
        $compatibility = $compatibilityJson | Out-String | ConvertFrom-Json
    }

    $manifestPath = Join-Path $outputPath 'manifest.json'
    $manifest = Get-Content -LiteralPath $manifestPath -Raw | ConvertFrom-Json
    if ($manifest.format -ne 'cowork-python-preprocessor-manifest-v1') {
        throw "Unexpected Cowork manifest format: $($manifest.format)"
    }

    $completed = [DateTimeOffset]::UtcNow
    $success = [ordered]@{
        status = 'succeeded'
        runId = $runId
        startedUtc = ConvertTo-UtcTimestamp $started
        completedUtc = ConvertTo-UtcTimestamp $completed
        durationSeconds = [math]::Round(($completed - $started).TotalSeconds, 3)
        refreshRequired = [bool]($refreshRequired -or $PreprocessOnly)
        preprocessOnly = [bool]$PreprocessOnly
        processedStartUtc = if ($null -ne $processedStart) { ConvertTo-UtcTimestamp $processedStart } else { $null }
        processedEndUtc = if ($null -ne $processedEnd) { ConvertTo-UtcTimestamp $processedEnd } else { $null }
        windowsProcessed = $windowPlan.Count
        caughtUp = if ($PreprocessOnly) { $null } elseif ($null -eq $processedEnd) { $true } else { $processedEnd -ge $targetEnd }
        manifestFormat = $manifest.format
        preprocessorVersion = $manifest.preprocessor_version
        reconciliation = $manifest.reconciliation
        timings = $manifest.timings
        compatibility = $compatibility
    }

    Write-JsonAtomic -Path $historyStatusPath -Value $success
    if (-not $PreprocessOnly -and $null -ne $processedEnd) {
        Write-JsonAtomic -Path $statePath -Value ([ordered]@{
            format = 'cowork-automation-watermark-v1'
            lastSuccessfulEndUtc = ConvertTo-UtcTimestamp $processedEnd
            updatedUtc = ConvertTo-UtcTimestamp $completed
            runId = $runId
        })
    }
    Write-JsonAtomic -Path $latestStatusPath -Value $success
    $success | ConvertTo-Json -Depth 20
}
catch {
    if ($null -eq $lockStream) {
        throw
    }
    $failed = [ordered]@{
        status = 'failed'
        runId = $runId
        startedUtc = ConvertTo-UtcTimestamp $started
        completedUtc = ConvertTo-UtcTimestamp ([DateTimeOffset]::UtcNow)
        error = $_.Exception.Message
    }
    try {
        Write-JsonAtomic -Path $historyStatusPath -Value $failed
        Write-JsonAtomic -Path $latestStatusPath -Value $failed
    }
    catch {
        Write-Warning "Unable to publish failure status: $($_.Exception.Message)"
    }
    throw
}
finally {
    if ($null -ne $lockStream) {
        $lockStream.Dispose()
    }
}
