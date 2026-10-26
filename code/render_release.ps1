$ErrorActionPreference = 'Stop'
$projectPath = Split-Path -Parent $PSScriptRoot
$wordApp = New-Object -ComObject Word.Application
$wordApp.Visible = $false
$wordApp.DisplayAlerts = 0
try {
    foreach ($stem in @('JSHESS_reading', 'JSHESS_submission', 'JSHESS_supplement')) {
        $inputPath = Join-Path $projectPath "submission/$stem.docx"
        $outputPath = Join-Path $projectPath "_qa/${stem}_release.pdf"
        $wordDoc = $wordApp.Documents.Open($inputPath, $false, $true)
        $wordDoc.Repaginate()
        $wordDoc.ExportAsFixedFormat($outputPath, 17)
        $wordDoc.Close(0)
        Write-Output "Rendered $stem"
    }
} finally {
    $wordApp.Quit()
    [void][System.Runtime.InteropServices.Marshal]::ReleaseComObject($wordApp)
}
