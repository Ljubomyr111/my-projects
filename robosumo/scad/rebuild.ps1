# ============================================================================
#  Перегенерувати всі деталі з OpenSCAD і освіжити прев'ю.
#
#  Запуск (з будь-якого місця):
#     pwsh -File scad\rebuild.ps1
#
#  Прав розміри в scad\params.scad, тоді запусти цей скрипт.
# ============================================================================

param(
    [string]$OpenScad = "C:\Program Files\OpenSCAD\openscad.exe",
    [int]$Dpi = 1000
)

# OpenSCAD пише свою статистику в stderr, тому не піднімаємо це в помилку
$ErrorActionPreference = "Continue"

$here = Split-Path -Parent $MyInvocation.MyCommand.Path
$root = Split-Path -Parent $here
$stlDir = Join-Path $root "stl"
$imgDir = Join-Path $root "scad_preview"

if (-not (Test-Path $OpenScad)) {
    Write-Error "OpenSCAD не знайдено: $OpenScad`nВкажи шлях параметром -OpenScad"
}

New-Item -ItemType Directory -Force -Path $stlDir | Out-Null
New-Item -ItemType Directory -Force -Path $imgDir | Out-Null

Write-Host "OpenSCAD: $OpenScad"
Write-Host "STL  -> $stlDir"
Write-Host "PNG  -> $imgDir"
Write-Host ""

# параметричний файл не є деталлю
$parts = Get-ChildItem $here -Filter "*.scad" |
         Where-Object { $_.Name -ne "params.scad" } |
         Sort-Object Name

$fail = 0
foreach ($p in $parts) {
    $stl = Join-Path $stlDir ($p.BaseName + ".stl")
    $png = Join-Path $imgDir ($p.BaseName + ".png")

    if (Test-Path $stl) { Remove-Item $stl -Force }
    if (Test-Path $png) { Remove-Item $png -Force }

    # 09_assembly — це не деталь для друку, лише перевірка збірки:
    # рендеримо тільки картинку, STL не зберігаємо в stl/
    $isAssembly = $p.BaseName -like "09_*"
    if (-not $isAssembly) {
        & $OpenScad -o $stl $p.FullName 2>$null | Out-Null
    }
    & $OpenScad -o $png --imgsize="$Dpi,760" --projection=o --viewall `
                --autocenter --colorscheme=Tomorrow $p.FullName 2>$null | Out-Null

    $okStl = Test-Path $stl
    $okPng = Test-Path $png
    if ($okStl -and $okPng) {
        "{0,-26} OK   STL {1,7:N0} KB   PNG {2,5:N0} KB" -f `
            $p.Name, ((Get-Item $stl).Length / 1KB), ((Get-Item $png).Length / 1KB)
    } else {
        "{0,-26} FAILED  (stl={1} png={2})" -f $p.Name, $okStl, $okPng
        $fail++
    }
}

Write-Host ""
if ($fail -eq 0) {
    Write-Host "Готово: $($parts.Count) файлів, усі згенеровано." -ForegroundColor Green
} else {
    Write-Warning "$fail файлів не згенерувалися."
    exit 1
}
