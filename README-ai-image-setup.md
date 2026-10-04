# Локальний стек редагування зображень (ComfyUI + SD 1.5)

Установлено й перевірено на цьому ПК. Усе працює **офлайн**, без жодного
зовнішнього API та без будь-яких вбудованих фільтрів вмісту.

## Що за залізо і чому саме так

| | |
|---|---|
| GPU | NVIDIA Quadro T1000, **4 ГБ VRAM**, compute capability 7.5 |
| CPU / RAM | i7-9750H / 16 ГБ |
| Стек | ComfyUI 0.38.0 portable, Python 3.13.14, **torch 2.14.0+cu130** |

4 ГБ VRAM — це головне обмеження. Тому базою взяті моделі класу **SD 1.5**
(~1–2 ГБ кожна), а не SDXL/Flux: останні фізично не влізуть. Реальні заміри
на цій машині:

| Операція | Час |
|---|---|
| txt2img 512×512, 24 кроки | ~30 с |
| Видалення об'єкта (LaMa) | **~4 с** |
| Заміна обличчя (ReActor) | **~6 с** |
| Inpaint з SD 1.5, 512×512 | ~45–105 с |
| Апскейл ×4 (512 → 2048) | ~12 с (перший прогін довший) |

## Де що лежить

```
C:\AI\
├─ ComfyUI_windows_portable\      ← сама програма (5,2 ГБ)
│  ├─ ComfyUI\
│  │  ├─ extra_model_paths.yaml   ← вказує на C:\AI\models
│  │  ├─ custom_nodes\
│  │  │  ├─ ComfyUI-ReActor\          (заміна облич)
│  │  │  └─ comfyui-inpaint-nodes\    (LaMa та інші inpaint-моделі)
│  │  └─ models\insightface\      ← junction на C:\AI\models\insightface
│  ├─ python_embeded\             ← Python з torch, усередині
│  └─ run_comfyui.bat             ← ЗАПУСК: подвійний клік
├─ models\                        ← 18,7 ГБ ваг
│  ├─ checkpoints\     sd-v1-5-inpainting, v1-5-pruned-emaonly,
│  │                   Realistic_Vision_V6.0, DreamShaper_8
│  ├─ controlnet\      openpose, depth, inpaint, softedge (v1.1)
│  ├─ inpaint\         big-lama.pt          (видалення об'єктів)
│  ├─ upscale_models\  RealESRGAN_x4plus.pth
│  ├─ facerestore_models\ GFPGANv1.4.pth
│  └─ insightface\     inswapper_128.onnx + models\buffalo_l\ (5 файлів)
└─ workflows\          ← робочі процеси (див. нижче)
```

Стокові дані ComfyUI (input/output/temp/user) виведені в `C:\AI\data-*`,
щоб оновлення програми їх не зачіпало. Зображення з'являються в
`C:\AI\data-output`.

## Запуск

1. Подвійний клік: **`C:\AI\ComfyUI_windows_portable\run_comfyui.bat`**
2. У браузері: **http://127.0.0.1:8188**
3. Зупинити сервер — закрити вікно консолі.

У вікні батника можна прибрати `--lowvram`, якщо хочете швидше й не ловите
помилок пам'яті. `--lowvram` тримає VRAM у межах, але частину роботи жене
через оперативну пам'ять — саме тому inpaint іноді займає півтори хвилини.

## Готові робочі процеси

Лежать у `C:\AI\workflows`. У веб-інтерфейсі: **Workflow → Load** і вибрати
файл. Файли, які процес очікує, треба покласти в `C:\AI\data-input`.

| Файл | Що робить |
|---|---|
| `01_txt2img.json` | генерація з нуля за текстом |
| `02_img2img.json` | переробити наявне зображення (denoise 0.45) |
| `03_inpaint_sd15.json` | inpainting з підказкою текстом (SD 1.5 inpainting) |
| `04_object_removal_lama.json` | **видалити об'єкт** — LaMa, без промпта, ~4 с |
| `05_inpaint_controlnet_openpose.json` | заміна тіла зі збереженням пози |
| `06_faceswap.json` | **заміна обличчя**: `target.png` + `source_face.png` |
| `07_upscale_x4.json` | апскейл ×4 (Real-ESRGAN) |

Маска для inpaint — чорно-біле зображення того ж розміру, що й фото:
**біле = ділянка, яку треба змінити або прибрати**.

### Запуск процесу з командного рядка

```powershell
$py = "C:\AI\ComfyUI_windows_portable\python_embeded\python.exe"

# видалити об'єкт
& $py C:\AI\workflows\run_workflow.py 04_object_removal_lama.json `
     --image C:\pics\photo.jpg --mask C:\pics\mask.png

# замінити обличчя
& $py C:\AI\workflows\run_workflow.py 06_faceswap.json `
     --target C:\pics\body.jpg --source C:\pics\face.jpg

# txt2img зі своїм промптом
& $py C:\AI\workflows\run_workflow.py 01_txt2img.json `
     --set-prompt "a red sports car on a mountain road" --seed 777 --steps 24
```

## Чекпойнти: що для чого

- **Realistic_Vision_V6.0** — основний для фотореалізму (обличчя, тіла).
- **DreamShaper_8** — художній/універсальний, краще тримає композицію.
- **sd-v1-5-inpainting** — спеціально навчений на inpainting: найкращий
  результат при заміні частин зображення.
- **v1-5-pruned-emaonly** — чистий оригінальний SD 1.5, база для всього.

Усі вони — відкриті ваги, які не мають вбудованих фільтрів: нічого не
блокується й нікуди не надсилається. У чекпойнтах SD 1.5 є так званий
`safety_checker` у метаданих, але ComfyUI його **не завантажує і не
викликає** — перевірено тестовими прогонами.

## Замінене обличчя (ReActor): що я в ньому змінив

ReActor має власний NSFW-детектор, який **тихо викидав кадр із черги**, якщо
класифікатор упевнений у «nsfw» більш ніж на 0,979. Це зведено нанівець:
у файлі
`custom_nodes\ComfyUI-ReActor\scripts\reactor_sfw.py`
константу `SCORE` змінено з `0.979` на `1.01` — умова не спрацьовує ніколи.
У файлі є коментар; щоб повернути як було — поставте назад `0.979`.

## Якщо треба щось доустановити

ComfyUI-Manager окремо не ставив. Нові вузли можна додати так:

```powershell
$py = "C:\AI\ComfyUI_windows_portable\python_embeded\python.exe"
cd C:\AI\ComfyUI_windows_portable\ComfyUI\custom_nodes
git clone https://github.com/АВТОР/НАЗВА
& $py -m pip install -r НАЗВА\requirements.txt
```

Потім перезапустити `run_comfyui.bat`.

### Якщо запускаєте через DSH (важливо)

DSH запускає дочірні процеси в пісочниці, яка **дозволяє запис лише всередині
робочої теки** `C:\Users\Lenovo\Documents\deepseek-harness\default-workspace`.
Тому при запуску ComfyUI з DSH треба вказати теки даних усередині воркспейсу:

```powershell
$ws = "C:\Users\Lenovo\Documents\deepseek-harness\default-workspace"
$py = "C:\AI\ComfyUI_windows_portable\python_embeded\python.exe"
& $py -s C:\AI\ComfyUI_windows_portable\ComfyUI\main.py --lowvram --port 8188 `
  --input-directory  "$ws\comfy-data\input"  `
  --output-directory "$ws\comfy-data\output" `
  --temp-directory   "$ws\comfy-data\temp"   `
  --user-directory   "$ws\comfy-data\user"
```

Те саме стосується `pip`: перед встановленням пакетів виставте
`$env:TEMP` і `$env:PIP_CACHE_DIR` у середину воркспейсу, інакше pip упаде з
`Access is denied`. Скрипти в `comfy-data\` (перевірка, збірка процесів,
запуск) уже написані під цей режим.

## Обмеження, про які варто знати

- **4 ГБ VRAM** — стеля для SD 1.5. SDXL запускається лише з важкими
  оптимізаціями й на межі; Flux/Qwen-Image-Edit не підуть взагалі.
- **Роздільність**: 512×512 — робоча; 768×768 можливо, але повільно. Вище —
  через апскейл, а не генерацією.
- **Batch size > 1** на 4 ГБ майже гарантовано дасть out-of-memory.
- Обличчя після свопу виглядає переконливо, але **колір волосся й одяг
  залишаються від вихідного фото** — це нормальна поведінка inswapper.
  Для повної зміни зачіски треба inpainting по волоссю окремо.
- Моделі завантажені з HuggingFace/GitHub; у мережі були обриви, тому
  качалка працювала з докачкою (`aria2c`, 8 з'єднань) — усі файли
  перевірені за розміром байт-у-байт.

## Як усе перевірялося

Кожен етап прогонявся по-справжньому, не «на віру»:

1. `comfy-data\integration_test.py` — txt2img → img2img → inpaint (LaMa і
   SD 1.5) → face swap → апскейл, усе через живий API ComfyUI.
2. `comfy-data\swap_ab_test.py` — один суб'єкт і три різні донори, щоб
   довести, що своп справді змінює обличчя, а не просто «щось робить».
3. `comfy-data\run_workflow.py` — по одному прогону кожного з 7 процесів.

Результати лежать у `comfy-data\output` (у т.ч. `ab_swap_*` — докази свопу).
