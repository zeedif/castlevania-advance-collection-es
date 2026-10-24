# Genera dist\CastlevaniaAdvanceES.exe (sin ventana de consola). Requiere Python 3.10+ con tkinter.
$ErrorActionPreference = 'Stop'
Set-Location $PSScriptRoot
python -m venv .venv-build
& .\.venv-build\Scripts\python.exe -m pip install --quiet pyinstaller
& .\.venv-build\Scripts\python.exe -m PyInstaller --noconfirm --onefile --windowed --name CastlevaniaAdvanceES `
    --distpath dist --workpath .build --specpath .build --paths $PSScriptRoot `
    --add-data "$PSScriptRoot\datos.json;." --add-data "$PSScriptRoot\menus_es.dat;." `
    --hidden-import menus_es instalar.py
Write-Host "Listo: dist\CastlevaniaAdvanceES.exe"
(Get-FileHash dist\CastlevaniaAdvanceES.exe -Algorithm SHA256).Hash
