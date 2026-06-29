# 将 dist 内 exe 打包为 GitHub Release 用 zip
param(
    [string]$Version = ""
)

$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot\..

if (-not $Version) {
    python scripts/check_release.py
    if ($LASTEXITCODE -ne 0) { throw "发版校验未通过" }
    $Version = (python -c "from bagua import __version__; print(__version__)").Trim()
}

$cli = "dist\bagua.exe"
$gui = "dist\bagua-gui.exe"
if (-not (Test-Path $cli)) { throw "未找到 $cli，请先运行 .\scripts\build.ps1" }
if (-not (Test-Path $gui)) { throw "未找到 $gui，请先运行 .\scripts\build.ps1" }

$zipName = "bagua-v$Version-win64.zip"
if (Test-Path $zipName) { Remove-Item $zipName -Force }

Compress-Archive -Path $cli, $gui -DestinationPath $zipName
Write-Host "已生成 $zipName" -ForegroundColor Green
Write-Host "上传至 GitHub Releases → Assets" -ForegroundColor DarkGray