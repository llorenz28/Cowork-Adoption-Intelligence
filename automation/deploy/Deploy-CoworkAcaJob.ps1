[CmdletBinding()]
param(
    [Parameter(Mandatory)][string]$SubscriptionId,
    [Parameter(Mandatory)][string]$ResourceGroup,
    [Parameter(Mandatory)][string]$EnvironmentName,
    [Parameter(Mandatory)][string]$AcrName,
    [Parameter(Mandatory)][string]$ManagedIdentityResourceId,
    [Parameter(Mandatory)][string]$ManagedIdentityClientId,
    [Parameter(Mandatory)][string]$TenantId,
    [Parameter(Mandatory)][string]$StorageAccountName,
    [Parameter(Mandatory)][string]$InitialStartUtc,
    [string]$StorageAccountResourceGroup = $ResourceGroup,
    [string]$FileShareName = 'cowork-adoption-data',
    [string]$JobName = 'cowork-adoption-refresh',
    [string]$ImageTag = '0.1.0',
    [int]$EndLagHours = 6,
    [int]$OverlapHours = 24,
    [int]$WindowHours = 24,
    [int]$MaxWindowsPerRun = 7,
    [double]$PaxBlockHours = 0.25,
    [int]$PaxMaxConcurrency = 6,
    [double]$CpuCores = 4.0,
    [double]$MemoryGi = 8.0,
    [int]$ReplicaTimeoutSeconds = 43200,
    [switch]$SkipBuild
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function Invoke-Az {
    param([Parameter(Mandatory)][string[]]$Arguments)

    & az @Arguments
    if ($LASTEXITCODE -ne 0) {
        $summary = ($Arguments | Select-Object -First 3) -join ' '
        throw "Azure CLI failed with exit code $LASTEXITCODE while running: az $summary ..."
    }
}

if (-not (Get-Command az -ErrorAction SilentlyContinue)) {
    throw "Azure CLI ('az') is required."
}
if ($OverlapHours -lt 0 -or $OverlapHours % 24 -ne 0) {
    throw 'OverlapHours must be zero or a whole number of days.'
}
if ($WindowHours -lt 24 -or $WindowHours % 24 -ne 0) {
    throw 'WindowHours must be a whole number of days.'
}
if ($MaxWindowsPerRun -lt 1) {
    throw 'MaxWindowsPerRun must be at least 1.'
}

$parsedInitial = [DateTimeOffset]::Parse(
    $InitialStartUtc,
    [Globalization.CultureInfo]::InvariantCulture,
    [Globalization.DateTimeStyles]::AssumeUniversal
).ToUniversalTime()
$normalizedInitial = [DateTimeOffset]::new(
    $parsedInitial.Year, $parsedInitial.Month, $parsedInitial.Day,
    0, 0, 0, [TimeSpan]::Zero
).UtcDateTime.ToString('yyyy-MM-ddTHH:mm:ssZ')

$packageRoot = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..'))
$containerRoot = Join-Path $packageRoot 'container'
$image = "$AcrName.azurecr.io/cowork-adoption-automation:$ImageTag"
$environmentStorageName = 'cowork-data'
$mountPath = '/data'

Invoke-Az @('account', 'set', '--subscription', $SubscriptionId)
Invoke-Az @('extension', 'add', '--name', 'containerapp', '--upgrade', '--only-show-errors')

if (-not $SkipBuild) {
    Invoke-Az @(
        'acr', 'build',
        '--registry', $AcrName,
        '--image', "cowork-adoption-automation:$ImageTag",
        '--file', (Join-Path $containerRoot 'Dockerfile'),
        $containerRoot,
        '--only-show-errors'
    )
}

$storageKey = & az storage account keys list `
    --account-name $StorageAccountName `
    --resource-group $StorageAccountResourceGroup `
    --query '[0].value' `
    --output tsv `
    --only-show-errors
if ($LASTEXITCODE -ne 0 -or [string]::IsNullOrWhiteSpace($storageKey)) {
    throw "Unable to retrieve a key for storage account '$StorageAccountName'."
}

& az storage share-rm create `
    --resource-group $StorageAccountResourceGroup `
    --storage-account $StorageAccountName `
    --name $FileShareName `
    --quota 1024 `
    --only-show-errors 2>$null | Out-Null
$share = & az storage share-rm show `
    --resource-group $StorageAccountResourceGroup `
    --storage-account $StorageAccountName `
    --name $FileShareName `
    --only-show-errors 2>$null
if ($LASTEXITCODE -ne 0 -or [string]::IsNullOrWhiteSpace($share)) {
    throw "Azure Files share '$FileShareName' does not exist after the create attempt."
}

Invoke-Az @(
    'containerapp', 'env', 'storage', 'set',
    '--name', $EnvironmentName,
    '--resource-group', $ResourceGroup,
    '--storage-name', $environmentStorageName,
    '--azure-file-account-name', $StorageAccountName,
    '--azure-file-account-key', $storageKey,
    '--azure-file-share-name', $FileShareName,
    '--access-mode', 'ReadWrite',
    '--only-show-errors'
)

$environmentVariables = @(
    "AZURE_CLIENT_ID=$ManagedIdentityClientId",
    "COWORK_TENANT_ID=$TenantId",
    'COWORK_DATA_ROOT=/data',
    "COWORK_INITIAL_START_UTC=$normalizedInitial",
    "COWORK_END_LAG_HOURS=$EndLagHours",
    "COWORK_OVERLAP_HOURS=$OverlapHours",
    "COWORK_WINDOW_HOURS=$WindowHours",
    "COWORK_MAX_WINDOWS_PER_RUN=$MaxWindowsPerRun",
    "COWORK_PAX_BLOCK_HOURS=$PaxBlockHours",
    "COWORK_PAX_MAX_CONCURRENCY=$PaxMaxConcurrency",
    'PAX_NONINTERACTIVE=1',
    'PAX_BOOTSTRAP_LOG_DIR=/data/logs/bootstrap'
)

$existing = & az containerapp job show `
    --name $JobName `
    --resource-group $ResourceGroup `
    --only-show-errors 2>$null

if ([string]::IsNullOrWhiteSpace($existing)) {
    $arguments = @(
        'containerapp', 'job', 'create',
        '--name', $JobName,
        '--resource-group', $ResourceGroup,
        '--environment', $EnvironmentName,
        '--trigger-type', 'Manual',
        '--replica-timeout', $ReplicaTimeoutSeconds.ToString(),
        '--replica-retry-limit', '0',
        '--parallelism', '1',
        '--replica-completion-count', '1',
        '--image', $image,
        '--cpu', ([string]::Format([Globalization.CultureInfo]::InvariantCulture, '{0}', $CpuCores)),
        '--memory', ([string]::Format([Globalization.CultureInfo]::InvariantCulture, '{0}Gi', $MemoryGi)),
        '--mi-user-assigned', $ManagedIdentityResourceId,
        '--registry-server', "$AcrName.azurecr.io",
        '--registry-identity', $ManagedIdentityResourceId,
        '--env-vars'
    ) + $environmentVariables + @('--only-show-errors')
    Invoke-Az $arguments
}
else {
    try {
        $existingJob = $existing | ConvertFrom-Json -ErrorAction Stop
    }
    catch {
        throw "Unable to parse the existing ACA Job definition for '$JobName'."
    }
    if ($existingJob.properties.configuration.triggerType -ne 'Manual') {
        throw "Existing ACA Job '$JobName' must use the Manual trigger type."
    }

    $arguments = @(
        'containerapp', 'job', 'update',
        '--name', $JobName,
        '--resource-group', $ResourceGroup,
        '--image', $image,
        '--cpu', ([string]::Format([Globalization.CultureInfo]::InvariantCulture, '{0}', $CpuCores)),
        '--memory', ([string]::Format([Globalization.CultureInfo]::InvariantCulture, '{0}Gi', $MemoryGi)),
        '--replica-timeout', $ReplicaTimeoutSeconds.ToString(),
        '--replica-retry-limit', '0',
        '--parallelism', '1',
        '--replica-completion-count', '1',
        '--set-env-vars'
    ) + $environmentVariables + @('--only-show-errors')
    Invoke-Az $arguments
    Invoke-Az @(
        'containerapp', 'job', 'identity', 'assign',
        '--name', $JobName,
        '--resource-group', $ResourceGroup,
        '--user-assigned', $ManagedIdentityResourceId,
        '--only-show-errors'
    )
    Invoke-Az @(
        'containerapp', 'job', 'registry', 'set',
        '--name', $JobName,
        '--resource-group', $ResourceGroup,
        '--server', "$AcrName.azurecr.io",
        '--identity', $ManagedIdentityResourceId,
        '--only-show-errors'
    )
}

$jobId = & az containerapp job show `
    --name $JobName `
    --resource-group $ResourceGroup `
    --query id `
    --output tsv `
    --only-show-errors
if ($LASTEXITCODE -ne 0 -or [string]::IsNullOrWhiteSpace($jobId)) {
    throw "Unable to resolve the resource ID for job '$JobName'."
}

$volumesJson = ConvertTo-Json -InputObject @(
    [ordered]@{
        name = $environmentStorageName
        storageType = 'AzureFile'
        storageName = $environmentStorageName
    }
) -Compress -Depth 5
$mountsJson = ConvertTo-Json -InputObject @(
    [ordered]@{
        volumeName = $environmentStorageName
        mountPath = $mountPath
    }
) -Compress -Depth 5

Invoke-Az @(
    'resource', 'update',
    '--ids', $jobId,
    '--set', "properties.template.volumes=$volumesJson",
    '--only-show-errors'
)
Invoke-Az @(
    'resource', 'update',
    '--ids', $jobId,
    '--set', "properties.template.containers[0].volumeMounts=$mountsJson",
    '--only-show-errors'
)

$gatewayPath = "\\$StorageAccountName.file.core.windows.net\$FileShareName\preprocessed"
Write-Output "Deployed ACA Job: $JobName"
Write-Output "Image: $image"
Write-Output "Power BI PreprocessedOutputPath: $gatewayPath"
Write-Output "Manual start: az containerapp job start --name $JobName --resource-group $ResourceGroup"
