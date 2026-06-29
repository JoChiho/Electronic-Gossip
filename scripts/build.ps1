# bagua 打包脚本（Windows）— 生成 CLI + GUI 双版本 exe
param(
    [switch]$Clean,
    [switch]$SkipTest
)

$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot\..

$Version = (python -c "from bagua import __version__; print(__version__)").Trim()
Write-Host "bagua v$Version 打包开始" -ForegroundColor Cyan

if ($Clean) {
    Remove-Item -Recurse -Force build, dist -ErrorAction SilentlyContinue
    Write-Host "已清理 build/ dist/" -ForegroundColor Yellow
}

if (-not $SkipTest) {
    Write-Host "校验版本与 CHANGELOG..." -ForegroundColor Cyan
    python scripts/check_release.py
    if ($LASTEXITCODE -ne 0) { throw "发版校验未通过，中止打包" }

    Write-Host "运行 lint / typecheck / 测试..." -ForegroundColor Cyan
    python -m ruff check bagua tests scripts
    if ($LASTEXITCODE -ne 0) { throw "ruff 未通过，中止打包" }
    python -m mypy bagua
    if ($LASTEXITCODE -ne 0) { throw "mypy 未通过，中止打包" }
    python -m pytest tests/ -q
    if ($LASTEXITCODE -ne 0) { throw "测试未通过，中止打包" }
}

pip install -q -r requirements-build.txt
pip install -q -e .

Write-Host "构建 bagua.exe (CLI)..." -ForegroundColor Cyan
pyinstaller packaging/bagua.spec --noconfirm --clean
if ($LASTEXITCODE -ne 0) { throw "CLI 打包失败" }

Write-Host "构建 bagua-gui.exe (GUI)..." -ForegroundColor Cyan
pyinstaller packaging/bagua-gui.spec --noconfirm --clean
if ($LASTEXITCODE -ne 0) { throw "GUI 打包失败" }

$dist = Resolve-Path "dist"
Write-Host ""
Write-Host "打包完成 v$Version" -ForegroundColor Green
Write-Host "  $($dist.Path)\bagua.exe"
Write-Host "  $($dist.Path)\bagua-gui.exe"
Write-Host ""
Write-Host "发布建议：将 dist 内 exe 压缩为 bagua-v$Version-win64.zip 上传 GitHub Release" -ForegroundColor DarkGray