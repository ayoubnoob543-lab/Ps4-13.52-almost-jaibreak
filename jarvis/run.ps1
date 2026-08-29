$ErrorActionPreference = 'Stop'
Set-Location $PSScriptRoot
if (-not (Test-Path .\.venv\Scripts\python.exe)) { throw 'No existe el entorno virtual. Ejecuta .\install.ps1 primero.' }
& .\.venv\Scripts\python.exe .\main.py
