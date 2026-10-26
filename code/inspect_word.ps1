$wa = [Runtime.InteropServices.Marshal]::GetActiveObject('Word.Application')
$wa.Documents | ForEach-Object { [pscustomobject]@{Path=$_.FullName;Saved=$_.Saved;ReadOnly=$_.ReadOnly} }
