$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path $PSScriptRoot -Parent
foreach ($item in @(@('JSHESS_manuscript_reading','v5_math_reading'), @('JSHESS_manuscript_submission','v5_math_submission'), @('JSHESS_supplementary_material','v5_math_supplement'), @('JSHESS_equations_explained_CN','v5_math_guide'))) {
    $documentPath = Join-Path $projectRoot ('revision/review_v5/submission_math_review/' + $item[0] + '.docx')
    $pdfPath = Join-Path $projectRoot ('_qa/' + $item[1] + '.pdf')
    & (Join-Path $PSScriptRoot 'render_word.ps1') -DocumentPath $documentPath -PdfPath $pdfPath
}
