param([string]$DocumentPath,[string]$PdfPath)
$ErrorActionPreference = 'Stop'
$wordApp = New-Object -ComObject Word.Application
$wordApp.Visible = $false
$wordApp.DisplayAlerts = 0
try {
    $wordDoc = $wordApp.Documents.Open($DocumentPath, $false, $true)
    $wordDoc.Repaginate()
    $wordDoc.ExportAsFixedFormat($PdfPath, 17)
    $wordDoc.Close(0)
} finally {
    $wordApp.Quit()
    [void][System.Runtime.InteropServices.Marshal]::ReleaseComObject($wordApp)
}
Write-Output "Rendered PDF: $PdfPath"
