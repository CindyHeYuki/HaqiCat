$ErrorActionPreference = "Stop"

$projectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$pythonPath = Join-Path $projectRoot ".venv\Scripts\python.exe"
$sourcePath = Join-Path $projectRoot "src"

if (-not (Test-Path -LiteralPath $pythonPath)) {
    throw "项目虚拟环境不存在，请先按 README 安装依赖。"
}

$env:PYTHONPATH = $sourcePath
& $pythonPath -m haqicat.app @args
exit $LASTEXITCODE

