[CmdletBinding()]
param(
    [Parameter(Mandatory)]
    [ValidateScript({ Test-Path -LiteralPath $_ -PathType Leaf })]
    [string] $InputTemplate,

    [Parameter(Mandatory)]
    [string] $OutputTemplate,

    [switch] $Force
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

Add-Type -AssemblyName System.IO.Compression
Add-Type -AssemblyName System.IO.Compression.FileSystem

function Get-ModelExpression {
    param(
        [Parameter(Mandatory)] $Schema,
        [Parameter(Mandatory)] [string] $Name
    )

    $matches = @($Schema.model.expressions | Where-Object name -eq $Name)
    if ($matches.Count -ne 1) {
        throw "Expected one model expression named '$Name'; found $($matches.Count)."
    }

    return $matches[0]
}

function Get-ModelTable {
    param(
        [Parameter(Mandatory)] $Schema,
        [Parameter(Mandatory)] [string] $Name
    )

    $matches = @($Schema.model.tables | Where-Object name -eq $Name)
    if ($matches.Count -ne 1) {
        throw "Expected one model table named '$Name'; found $($matches.Count)."
    }

    return $matches[0]
}

function Update-MExpression {
    param(
        [Parameter(Mandatory)] $Node,
        [Parameter(Mandatory)] [scriptblock] $Transform
    )

    $lines = @($Node.expression)
    $updated = @(& $Transform $lines)
    $Node.expression = if ($updated.Count -eq 1) { $updated[0] } else { $updated }
}

function Replace-RequiredText {
    param(
        [Parameter(Mandatory)] [AllowEmptyString()] [string[]] $Lines,
        [Parameter(Mandatory)] [string] $Pattern,
        [Parameter(Mandatory)] [string] $Replacement,
        [Parameter(Mandatory)] [string] $Description
    )

    $before = $Lines -join "`n"
    $after = $before -replace $Pattern, $Replacement
    if ($after -ceq $before) {
        throw "Could not update $Description; the expected source text was not found."
    }

    return $after -split "`n"
}

$inputPath = (Resolve-Path -LiteralPath $InputTemplate).Path
$outputPath = [IO.Path]::GetFullPath($OutputTemplate)
if ([string]::Equals($inputPath, $outputPath, [StringComparison]::OrdinalIgnoreCase)) {
    throw 'InputTemplate and OutputTemplate must be different files.'
}

if ((Test-Path -LiteralPath $outputPath) -and -not $Force) {
    throw "Output template already exists: $outputPath. Use -Force to replace it."
}

$outputDirectory = Split-Path -Parent $outputPath
if ($outputDirectory) {
    [IO.Directory]::CreateDirectory($outputDirectory) | Out-Null
}

$inputZip = [IO.Compression.ZipFile]::OpenRead($inputPath)
try {
    $schemaEntry = $inputZip.GetEntry('DataModelSchema')
    if ($null -eq $schemaEntry) {
        throw 'The input template does not contain a DataModelSchema stream.'
    }

    $schemaTimestamp = $schemaEntry.LastWriteTime
    $reader = [IO.StreamReader]::new(
        $schemaEntry.Open(),
        [Text.UnicodeEncoding]::new($false, $false),
        $true
    )
    try {
        $schema = $reader.ReadToEnd() | ConvertFrom-Json -Depth 100
    }
    finally {
        $reader.Dispose()
    }
}
finally {
    $inputZip.Dispose()
}

$siteParameter = Get-ModelExpression -Schema $schema -Name 'DataFolderPath'
$siteParameter.name = 'SharePointSiteUrl'
$siteParameter.description = @(
    'Required SharePoint site URL, for example',
    'https://contoso.sharepoint.com/sites/CoworkAdoption.'
)

$folderParameter = [PSCustomObject][ordered]@{
    name        = 'SharePointFolderUrl'
    description = @(
        'Required full SharePoint folder URL containing the supported CSV exports.',
        'Files in this folder and its subfolders are discovered automatically.'
    )
    kind        = 'm'
    expression  = 'null meta [IsParameterQuery=true, Type="Text", IsParameterQueryRequired=true]'
    lineageTag  = '06396733-5b9f-4dc9-a6e2-537abfd4d879'
    annotations = @(
        [PSCustomObject][ordered]@{
            name  = 'PBI_ResultType'
            value = 'Text'
        }
    )
}

$sharePointFiles = [PSCustomObject][ordered]@{
    name        = 'SharePointFiles'
    description = @(
        'Single static SharePoint connector scoped recursively to SharePointFolderUrl.',
        'All CSV discovery queries reuse this table and its binary Content column.'
    )
    kind        = 'm'
    expression  = @(
        'let',
        '    Site = Text.TrimEnd(Text.Trim(SharePointSiteUrl), "/"),',
        '    Folder = Text.TrimEnd(Text.Trim(SharePointFolderUrl), "/") & "/",',
        '    Source = SharePoint.Files(Site, [ApiVersion = 15]),',
        '    Scoped = Table.SelectRows(Source, each Text.StartsWith([Folder Path], Folder, Comparer.OrdinalIgnoreCase))',
        'in',
        '    Scoped'
    )
    lineageTag  = 'c9939964-dd42-4db4-8485-87ccebf30aba'
    annotations = @(
        [PSCustomObject][ordered]@{
            name  = 'PBI_ResultType'
            value = 'Table'
        }
    )
}

$remainingExpressions = @($schema.model.expressions | Select-Object -Skip 1)
$schema.model.expressions = @($siteParameter, $folderParameter, $sharePointFiles) + $remainingExpressions

$findCsv = Get-ModelExpression -Schema $schema -Name 'fnFindCsvPath'
Update-MExpression -Node $findCsv -Transform {
    param($lines)
    $lines = Replace-RequiredText $lines 'as nullable text =>' 'as nullable binary =>' 'fnFindCsvPath return type'
    $lines = Replace-RequiredText $lines 'Files = try Folder\.Files\(DataFolderPath\) otherwise #table\(type table \[Content = binary, Name = text, Extension = text, #"Folder Path" = text\], \{\}\),' 'Files = SharePointFiles,' 'fnFindCsvPath file source'
    Replace-RequiredText $lines 'if Match = null then null else Match\[#"Folder Path"\] & Match\[Name\]' 'if Match = null then null else Match[Content]' 'fnFindCsvPath result'
}

$loadCsv = Get-ModelExpression -Schema $schema -Name 'fnLoadCsv'
Update-MExpression -Node $loadCsv -Transform {
    param($lines)
    $lines = Replace-RequiredText $lines '\(path as text\) as table =>' '(content as binary) as table =>' 'fnLoadCsv input type'
    Replace-RequiredText $lines 'Csv\.Document\(File\.Contents\(path\),' 'Csv.Document(content,' 'fnLoadCsv binary source'
}

(Get-ModelExpression -Schema $schema -Name 'CopilotAuditFolderPath').expression = 'SharePointFiles'
(Get-ModelExpression -Schema $schema -Name 'IdentityEnrichmentFolderPath').expression = 'SharePointFiles'

$auditWithLists = Get-ModelExpression -Schema $schema -Name 'Fact_CopilotAuditRaw_WithLists'
Update-MExpression -Node $auditWithLists -Transform {
    param($lines)
    Replace-RequiredText $lines 'Folder\.Files\(CopilotAuditFolderPath\)' 'CopilotAuditFolderPath' 'audit file enumeration'
}

$dimUser = Get-ModelTable -Schema $schema -Name 'Dim_User'
Update-MExpression -Node $dimUser.partitions[0].source -Transform {
    param($lines)
    $lines = Replace-RequiredText $lines 'Folder\.Files\(CopilotAuditFolderPath\)' 'CopilotAuditFolderPath' 'Dim_User audit file enumeration'
    Replace-RequiredText $lines 'Folder\.Files\(IdentityEnrichmentFolderPath\)' 'IdentityEnrichmentFolderPath' 'Dim_User identity file enumeration'
}

$factUsage = Get-ModelTable -Schema $schema -Name 'Fact_CoworkUsage'
Update-MExpression -Node $factUsage.partitions[0].source -Transform {
    param($lines)
    Replace-RequiredText $lines 'File\.Contents\(CoworkUsageCsvPath\)' 'CoworkUsageCsvPath' 'Fact_CoworkUsage binary source'
}

$dimUserOrg = Get-ModelTable -Schema $schema -Name 'Dim_UserOrg'
Update-MExpression -Node $dimUserOrg.partitions[0].source -Transform {
    param($lines)
    Replace-RequiredText $lines 'File\.Contents\(OrgCsvPath\)' 'OrgCsvPath' 'Dim_UserOrg binary source'
}

foreach ($expression in $schema.model.expressions) {
    if ($null -ne $expression.PSObject.Properties['description']) {
        $expression.description = @($expression.description | ForEach-Object {
            $_ -replace 'DataFolderPath', 'SharePointFolderUrl'
        })
    }
}

$queryOrderAnnotation = @($schema.model.annotations | Where-Object name -eq 'PBI_QueryOrder')
if ($queryOrderAnnotation.Count -ne 1) {
    throw "Expected one PBI_QueryOrder annotation; found $($queryOrderAnnotation.Count)."
}

$queryOrder = @($queryOrderAnnotation[0].value | ConvertFrom-Json)
$dataFolderIndex = [Array]::IndexOf($queryOrder, 'DataFolderPath')
if ($dataFolderIndex -lt 0) {
    throw 'PBI_QueryOrder does not contain DataFolderPath.'
}

$queryOrderBefore = if ($dataFolderIndex -gt 0) {
    @($queryOrder[0..($dataFolderIndex - 1)])
}
else {
    @()
}
$queryOrderAfter = if ($dataFolderIndex -lt ($queryOrder.Count - 1)) {
    @($queryOrder[($dataFolderIndex + 1)..($queryOrder.Count - 1)])
}
else {
    @()
}
$queryOrder = @(
    $queryOrderBefore
    'SharePointSiteUrl'
    'SharePointFolderUrl'
    'SharePointFiles'
    $queryOrderAfter
)
$queryOrderAnnotation[0].value = $queryOrder | ConvertTo-Json -Compress

$schemaJson = $schema | ConvertTo-Json -Depth 100
$parameterCount = ([regex]::Matches($schemaJson, 'IsParameterQuery=true')).Count
$sharePointConnectorCount = ([regex]::Matches($schemaJson, 'SharePoint\.Files\(')).Count
if ($parameterCount -ne 2) {
    throw "Expected two required parameters after conversion; found $parameterCount."
}
if ($sharePointConnectorCount -ne 1) {
    throw "Expected one SharePoint.Files connector after conversion; found $sharePointConnectorCount."
}
if ($schemaJson -match 'Folder\.Files\(|File\.Contents\(|DataFolderPath') {
    throw 'The converted model still contains a local-folder source reference.'
}

if (Test-Path -LiteralPath $outputPath) {
    Remove-Item -LiteralPath $outputPath -Force
}
Copy-Item -LiteralPath $inputPath -Destination $outputPath

try {
    $outputZip = [IO.Compression.ZipFile]::Open($outputPath, [IO.Compression.ZipArchiveMode]::Update)
    try {
        $oldSchemaEntry = $outputZip.GetEntry('DataModelSchema')
        if ($null -eq $oldSchemaEntry) {
            throw 'The copied template does not contain a DataModelSchema stream.'
        }
        $oldSchemaEntry.Delete()

        $newSchemaEntry = $outputZip.CreateEntry(
            'DataModelSchema',
            [IO.Compression.CompressionLevel]::Optimal
        )
        $newSchemaEntry.LastWriteTime = $schemaTimestamp
        $writer = [IO.StreamWriter]::new(
            $newSchemaEntry.Open(),
            [Text.UnicodeEncoding]::new($false, $false)
        )
        try {
            $writer.Write($schemaJson)
        }
        finally {
            $writer.Dispose()
        }
    }
    finally {
        $outputZip.Dispose()
    }

    $verifyZip = [IO.Compression.ZipFile]::OpenRead($outputPath)
    try {
        if ($verifyZip.GetEntry('SecurityBindings')) {
            throw 'The output unexpectedly contains a machine-bound SecurityBindings stream.'
        }

        $verifySchemaEntry = $verifyZip.GetEntry('DataModelSchema')
        $verifyReader = [IO.StreamReader]::new(
            $verifySchemaEntry.Open(),
            [Text.UnicodeEncoding]::new($false, $false),
            $true
        )
        try {
            $verifyJson = $verifyReader.ReadToEnd()
            $null = $verifyJson | ConvertFrom-Json -Depth 100
        }
        finally {
            $verifyReader.Dispose()
        }
    }
    finally {
        $verifyZip.Dispose()
    }
}
catch {
    Remove-Item -LiteralPath $outputPath -Force -ErrorAction SilentlyContinue
    throw
}

$outputFile = Get-Item -LiteralPath $outputPath
$hash = (Get-FileHash -LiteralPath $outputPath -Algorithm SHA256).Hash.ToLowerInvariant()
[PSCustomObject]@{
    Path       = $outputFile.FullName
    Bytes      = $outputFile.Length
    SHA256     = $hash
    Parameters = @('SharePointSiteUrl', 'SharePointFolderUrl')
    Connector  = 'SharePoint.Files'
}
