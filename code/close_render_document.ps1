$wa = [Runtime.InteropServices.Marshal]::GetActiveObject('Word.Application')
$expected = 'F:\个人论文3\JSHESS_Manuscript\submission\JSHESS_reading.docx'
foreach ($wd in @($wa.Documents)) {
    if ($wd.FullName -eq $expected -and $wd.Saved -and $wd.ReadOnly) { $wd.Close(0) }
}
if ($wa.Documents.Count -eq 0) { $wa.Quit() }
Write-Output 'Closed the saved, read-only manuscript used by the interrupted renderer.'
