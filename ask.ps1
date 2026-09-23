Set-Location $PSScriptRoot
$env:PYTHONPATH = (Get-Location).Path
& "$PSScriptRoot\.venv\Scripts\python.exe" ask_python.py @args
