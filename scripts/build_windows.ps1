$ErrorActionPreference = "Stop"

$projectDir = (Resolve-Path (Join-Path $PSScriptRoot ".." )).Path
$buildPython = Join-Path $projectDir ".venv-build\Scripts\python.exe"
$outputDir = Join-Path $HOME "Aplicaciones\Clipper\Windows"
$workDir = Join-Path $projectDir "build\windows"

if (-not (Test-Path $buildPython)) {
	py -3 -m venv (Join-Path $projectDir ".venv-build")
}

& $buildPython -m pip install -r (Join-Path $projectDir "requirements.txt") -r (Join-Path $projectDir "requirements-build.txt")
& $buildPython -m PyInstaller --noconfirm --clean `
	--distpath $outputDir `
	--workpath $workDir `
	(Join-Path $projectDir "packaging\clipper.spec")