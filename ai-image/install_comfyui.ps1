# ============================================================
#  install_comfyui.ps1
#  Чекає завершення завантажень, перевіряє архів, розпаковує
#  ComfyUI portable і розкладає моделі по C:\AI\models
# ============================================================
$ErrorActionPreference = 'Stop'
[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12

$Base     = 'C:\Users\Lenovo\Documents\deepseek-harness\default-workspace\ai-image'
$Dl       = Join-Path $Base '_downloads'
$Models   = 'C:\AI\models'
$Dest     = 'C:\AI\ComfyUI'
$SevenZr  = Join-Path $Dl '7zr.exe'

function Say($m) { Write-Host ("[{0:HH:mm:ss}] {1}" -f (Get-Date), $m) }

# ---------- 1. дочекатися кінця завантажень ----------
Say "Waiting for aria2 downloads to finish..."
$deadline = (Get-Date).AddHours(3)
while ((Get-Process aria2c -ErrorAction SilentlyContinue) -and (Get-Date) -lt $deadline) {
    Start-Sleep -Seconds 30
}
if (Get-Process aria2c -ErrorAction SilentlyContinue) { throw "aria2 still running after 3h - aborting" }
Say "aria2 finished."

# ---------- 2. звіт про файли ----------
$expected = @{
    'ComfyUI_portable_nvidia.7z'             = 1994326521
    'sd-v1-5-inpainting.ckpt'                = 4265437280
    'v1-5-pruned-emaonly.safetensors'        = 4265146304
    'DreamShaper_8_pruned.safetensors'       = 2132625894
    'Realistic_Vision_V6.0_NV_B1_fp16.safetensors' = 2132625894
    'control_v11p_sd15_openpose.pth'         = 1445235707
    'control_v11f1p_sd15_depth.pth'          = 1445235707
    'control_v11p_sd15_inpaint.pth'          = 1445235707
    'control_v11p_sd15_softedge.pth'         = 1445235707
    'RealESRGAN_x4plus.pth'                  = 67040989
    'inswapper_128.onnx'                     = 554253681
    'GFPGANv1.4.pth'                         = 348632874
    'lama_fp32.onnx'                         = 208044816
}
Say "Download report (size check):"
$missing = @()
foreach ($k in $expected.Keys | Sort-Object) {
    $p = Join-Path $Dl $k
    if (-not (Test-Path $p)) { Say ("  MISSING  {0}" -f $k); $missing += $k; continue }
    $len = (Get-Item $p).Length
    $ok = if ($len -ge ($expected[$k] * 0.99)) { 'ok  ' } else { 'PART' }
    Say ("  {0}  {1,12:N0} bytes  {2}" -f $ok, $len, $k)
    if ($ok -eq 'PART') { $missing += $k }
}

# ---------- 3. перевірка цілісності архіву ----------
$arch = Join-Path $Dl 'ComfyUI_portable_nvidia.7z'
Say "Testing archive integrity (7z t) ..."
$t = & $SevenZr t $arch 2>&1 | Out-String
if ($LASTEXITCODE -ne 0) {
    Say "ARCHIVE IS CORRUPT - re-download needed:"
    $t -split "`n" | Select-Object -Last 8 | ForEach-Object { Say "    $_" }
    throw "corrupt archive"
}
Say "Archive OK."

# ---------- 4. розпакування ----------
if (Test-Path (Join-Path $Dest 'ComfyUI\main.py')) {
    Say "ComfyUI already extracted - skipping extraction."
} else {
    Say "Extracting to $Dest ..."
    & $SevenZr x $arch "-o$Dest" -y | Out-Null
    if ($LASTEXITCODE -ne 0) { throw "extraction failed ($LASTEXITCODE)" }
    Say "Extracted."
}

# ---------- 5. розкладання моделей ----------
function Place($file, $subdir) {
    $src = Join-Path $Dl $file
    if (-not (Test-Path $src)) { Say "  skip (missing): $file"; return }
    if ((Get-Item $src).Length -lt 1024) { Say "  skip (empty):  $file"; return }
    $dir = Join-Path $Models $subdir
    New-Item -ItemType Directory -Force -Path $dir | Out-Null
    $dst = Join-Path $dir $file
    if (Test-Path $dst) {
        if ((Get-Item $dst).Length -eq (Get-Item $src).Length) { Say "  already: $file"; return }
    }
    Copy-Item $src $dst -Force
    Say ("  placed: {0} -> models\{1}" -f $file, $subdir)
}

Say "Placing models..."
Place 'sd-v1-5-inpainting.ckpt'                       'checkpoints'
Place 'v1-5-pruned-emaonly.safetensors'               'checkpoints'
Place 'DreamShaper_8_pruned.safetensors'              'checkpoints'
Place 'Realistic_Vision_V6.0_NV_B1_fp16.safetensors'  'checkpoints'
Place 'control_v11p_sd15_openpose.pth'                'controlnet'
Place 'control_v11f1p_sd15_depth.pth'                 'controlnet'
Place 'control_v11p_sd15_inpaint.pth'                 'controlnet'
Place 'control_v11p_sd15_softedge.pth'                'controlnet'
Place 'RealESRGAN_x4plus.pth'                         'upscale_models'
Place 'GFPGANv1.4.pth'                                'facerestore_models'
Place 'inswapper_128.onnx'                            'insightface'
Place 'lama_fp32.onnx'                                'upscale_models'

Say "=== DONE ==="
Say ("Models tree: {0:N2} GB" -f ((Get-ChildItem $Models -Recurse -File -ErrorAction SilentlyContinue | Measure-Object Length -Sum).Sum/1GB))
if ($missing.Count -gt 0) { Say ("INCOMPLETE FILES: " + ($missing -join ', ')) }
