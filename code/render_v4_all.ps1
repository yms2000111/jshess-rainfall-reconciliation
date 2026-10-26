$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path $PSScriptRoot -Parent
foreach ($item in @(@('JSHESS_manuscript_reading','v4_reading'), @('JSHESS_manuscript_submission','v4_submission'), @('JSHESS_supplementary_material','v4_supplement'))) {
    $documentPath = Join-Path $projectRoot ('revision/review_v4/submission/' + $item[0] + '.docx')
    $pdfPath = Join-Path $projectRoot ('_qa/' + $item[1] + '.pdf')
    & (Join-Path $PSScriptRoot 'render_word.ps1') -DocumentPath $documentPath -PdfPath $pdfPath
}
