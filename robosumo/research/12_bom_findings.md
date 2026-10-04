# 12 — Bill of Materials Findings: Magnetic-Arena Autonomous Sumo Robot (Kyiv, Ukraine)

**Prepared for:** university robot-sumo team, Kyiv, Ukraine
**Brief:** one robot, budget ≈ **$500 USD**; may buy cheap spares. Arena is a **magnetic (steel) dohyo**, so the robot needs **neodymium downforce** and a **high-torque geared drivetrain**. Fully **autonomous** (no remote control). Team can 3D-print and CNC/laser-cut locally.
**Research method:** live `web_search` / `web_fetch` against vendor pages and price aggregators.
**Report date:** 2026-10-01 (research session date)

---

## 0. ⚠️ Read this first — sourcing constraints that shaped the report

Two things you must know before using the tables:

1. **This session had no ability to shop with a logged-in basket or get a shipping quote.** All prices are **list prices read off public product/category pages or from search-result titles**. Prices **exclude** shipping, customs/VAT, and any Ukrainian import duty. Every line has a source URL; anything I could not read on a page is marked **unconfirmed** — I have **not** invented a single price or part number.
2. **Shipping to Ukraine is the dominant hidden cost, not the parts.** Practical ranking for a Kyiv team:
   - **Tier 1 — Ukrainian shops** (arduino.ua, merkon.ua, supermagnit.net.ua, prom.ua, rozetka.com.ua, hobbymania.com.ua, local laser/waterjet shops): Nova Poshta, 1–3 days, no customs risk. Best for magnets, Arduino/sensors, LiPo, sheet material, fabrication.
   - **Tier 2 — AliExpress**: cheapest absolute prices, ships to Ukraine, but 2–6 weeks and variable stock; excellent for magnets, drivers, wheels, bearings, clone MCUs.
   - **Tier 3 — Turkey (JSumo)**: purpose-built sumo hardware, fixed **$9.95 registered air mail, free over $199** ([jsumo.com product page](https://www.jsumo.com/m1-arduino-mini-sumo-robot-kit-unassembled)) — genuinely good for Kyiv.
   - **Tier 4 — USA (Pololu)**: best-documented motors, but international shipping + customs make small orders expensive; buy Pololu via **EU distributors** instead where possible.
   - **Tier 5 — EU (Botland PL, TME PL, Kamami PL, Abra CA)**: good for Pololu parts. **PL shops are the cheapest realistic route for genuine Pololu gearmotors to Kyiv.** *I was unable to confirm Ukrainian shipping terms/prices for Botland, TME and Kamami in this session — treat as needs-verification.*

### Assumed exchange rate

| Item | Value | Date / source |
|---|---|---|
| **USD → UAH** | **1 USD = 44.6819 UAH** | NBU official rate for **1 October 2026** ([ua.korrespondent.net](https://ua.korrespondent.net/business/financial/4916220-nbu-nazvav-kursy-valuit-na-pershyi-den-zhovtnia), quoting bank.gov.ua) |
| Street/cash rate (for reference) | 44.80–44.94 UAH/USD | same source |

All UAH→USD conversions below use **44.6819**. Conversions are marked `≈`.

---

## 1. Weight classes and rules — what you are actually building for

| Class | Typical max mass | Typical footprint | Typical ring | Notes |
|---|---|---|---|---|
| **Micro-sumo** | 100 g | 5 × 5 cm | 38.5 cm | Not in your brief, but JSumo sells an XS1 kit at **$99.00** — see §6 |
| **Mini-sumo** | **500 g** | 10 × 10 cm | 77 cm | The classic entry class |
| **Midi-sumo / 1 kg** | **1 kg (1000 g)** | 10 × 10 cm to 15 × 15 cm | 77–154 cm | **This is your "~1 kg build"** |
| **Mega-sumo / 3 kg** | **3 kg (3000 g)** | 20 × 20 cm | 154 cm | **This is your "~3 kg build"** |
| Ukrainian RoboSumo (RoboTerra 2025, *radio-controlled LEGO*) | 1000 g, 250 × 250 × 250 mm | — | 1 m circle, 5 cm black line | Different event, **not** autonomous open-class — included only because it is a real Ukrainian ruleset |

Sources for class structure: [RobotChallenge Robo Sumo rules (PDF, mirrored)](http://www.robotchallenge.org.cn/doc/en/RC-Sumo.pdf), [Robotic Arena MegaSumo rules (PDF)](https://roboticarena.pl/media/filer_public/ab/7b/ab7b7947-79d0-4a29-9eef-49da77f98fb8/en_megasumo.pdf), [MEB Robot Mini Sumo 2026 category page](https://robot.meb.gov.tr/categories/mini-sumo-2026), [Robot-sumo / Sumo bot overview](https://en.m.wikipedia.org/wiki/Sumo_bot).
**Caveat:** the two rule PDFs returned unreadable/HTTP-406 content types in this session, so the **exact wording and exact numbers per class are `unconfirmed`** — verify against the specific rulebook of the competition you will enter (weights, size, magnet legality, and whether magnetic downforce is even allowed are frequently restricted). ✅ **Action item for the team: confirm with the organiser that magnets are legal before you spend a UAH on them.**
Ukrainian local ruleset verified in this workspace: [RoboTerra 2025 РОБОСУМО rules PDF](https://perspektyva.ck.ua/arch/robotterra2025/sumod2025.pdf) (see `robosumo/research/01_rules_ukraine.txt`).

### Why magnetic downforce changes the whole BOM

On a steel dohyo the normal force on your tyres is `m·g + F_magnets`, not `m·g`. Traction — and therefore pushing force — scales with that. But three hard consequences drive the parts list:

- **Magnets must run at a small air gap (≈0.3–1.5 mm) to work.** So the chassis must be **rigid, flat and non-flexing**, and the magnets must be mounted on a **flat, stiff belly plate or in pockets** — a 1.5 mm bent aluminium plate will bend toward the steel and start dragging. Thicker plate (≥2 mm steel or 3–4 mm aluminium) or a 3D-printed pocket block is needed.
- **Over-magneting is a real failure mode:** too much holding force → high friction and "sticking" to the dohyo, slow turns, and the robot behaves like it is glued down. Target roughly **8–15 kg** total holding force for a **1 kg** robot and **25–40 kg** for a **3 kg** robot (**engineering estimate, not a cited figure** — tune empirically by adding/removing magnets).
- **Magnets are brittle and demagnetise above ~80 °C.** Keep them out of gearbox heat paths and do not use them as structural clamps carrying load.

---

## 2. Numbered findings (your brief items 1–8)

Legend: ✅ = price read directly from the vendor page in this session · 🔎 = price appears in a search-result title/link text (price is quoted, page itself not fully read) · ❓ = **unconfirmed**

### 2.1 Geared motors (2 per robot)

| # | Exact product name | Ratio / speed | Torque | Price | Source URL | Notes |
|---|---|---|---|---|---|---|
| M1 | **Pololu 70:1 Metal Gearmotor 37Dx54L mm 12V (Helical Pinion)** — Pololu item **#4744** | 70:1, 150 RPM no-load | 27 kg·cm stall | **$38.95** (1 pc) · **$35.83** (5+) · **$32.97** (25+) · **$30.33** (100+) | ✅ [pololu.com/product/4744](https://www.pololu.com/product/4744) | Stall current **5.5 A** @12 V. The default "serious" sumo motor. **2 pcs = $77.90** |
| M2 | Pololu 37D 12 V family — **#4741** (19:1), **#4742** (30:1), **#4743** (50:1), **#4744** (70:1), **#4745** (100:1), **#4746** (131:1), **#2829** (150:1) | 19:1 → 150:1 | 8.5 → 49 kg·cm stall | ❓ item prices other than #4744 **unconfirmed** | ✅ [category page with full spec table](https://www.pololu.com/category/116/37d-metal-gearmotors) | Full torque/speed table on that page — pick from it |
| M3 | Pololu 37D **with 64 CPR encoder** — #4751/#4752/#4753/**#4754**/#4755/#4756 | same ratios | same | ❓ **unconfirmed** (data sheet: [pololu-37d-metal-gearmotors.pdf](https://a.pololu-files.com/file/0J1706/pololu-37d-metal-gearmotors.pdf)) | [pololu.com/category/116](https://www.pololu.com/category/116/37d-metal-gearmotors) | Encoder is **not needed** for a line-following-kill sumo bot; saves ~$8–10/motor. Buy only if you want closed-loop pushing |
| M4 | **JSumo DC Gearhead Motor 25mm 12V 750 RPM SP** — product code **JS19838** | 17.5:1, 750 RPM | **1.1 kg·cm** stall (107 mN·m) | **$23.50** | ✅ [jsumo.com/12v-25mm-dc-gear-motor-750-rpm](https://www.jsumo.com/12v-25mm-dc-gear-motor-750-rpm) | Only 90.5 g, 4 mm D-shaft, stall 680 mA. **Too weak alone for 3 kg**, but JSumo states it is used in their BB1 1 kg midi-sumo kit, 4 pcs suggested |
| M5 | **JSumo DC Gearhead Motor 25mm 12V 500 RPM HP** | — | — | **$23.50** | ✅ [jsumo.com/jsumo-dc-gearhead-motor-25mm-12v-500-rpm-hp](https://www.jsumo.com/jsumo-dc-gearhead-motor-25mm-12v-500-rpm-hp) | Higher-torque version of M4 |
| M6 | **JSumo DC Gearhead Motor 25mm 12V 250 RPM HP** | — | — | **$18.95** | ✅ [jsumo.com/12v-25mm-dc-gear-motor-250-rpm](https://www.jsumo.com/12v-25mm-dc-gear-motor-250-rpm) | |
| M7 | **Titan DC Gearhead Motor 12V 1000 RPM HP** | — | — | **$27.00** | ✅ [jsumo.com/jsumo-titan-dc-gearhead-motor-12v-1000-rpm-hp](https://www.jsumo.com/jsumo-titan-dc-gearhead-motor-12v-1000-rpm-hp) | |
| M8 | **Titan DC Gearhead Motor 12V 500 RPM SP** | — | — | **$27.00** | ✅ [jsumo.com/titan-dc-gearhead-motor-12v-500-rpm-sp](https://www.jsumo.com/titan-dc-gearhead-motor-12v-500-rpm-sp) | |
| M9 | **Proton DC Gear Motor 12V 500 RPM (Extended 37 mm type, 6 mm shaft)** | — | — | **$29.00** | ✅ [jsumo.com/proton-dc-gear-motor-12v-500-rpm-extended-37mm-type-with-6mm-shaft](https://www.jsumo.com/proton-dc-gear-motor-12v-500-rpm-extended-37mm-type-with-6mm-shaft) | **37 mm-class, 6 mm shaft = direct Pololu-wheel compatibility.** Strong candidate for the 3 kg build |
| M10 | **G3 Kingpin 12V 60 RPM High Torque L-Type Gear Motor with 8 mm shaft** | 60 RPM | high | **$49.00** | ✅ [jsumo.com/g3-kingpin-12v-60rpm-...](https://www.jsumo.com/g3-kingpin-12v-60rpm-high-torque-l-type-gear-motor-with-8mm-shaft) | Very slow; for a pure pusher |
| M11 | **PREORDER — Symtec Q Gearmotor (12 V 1450 RPM 9.28:1, 44 kg·cm)** | 9.28:1 | **44 kg·cm** | **$94.50** each | ✅ [jsumo.com/symtec-q-gear-motor-12v-1450rpm](https://www.jsumo.com/symtec-q-gear-motor-12v-1450rpm) | 44 kg·cm at 1450 RPM is **elite-tier** (2 pcs = $189 = 38% of the entire $500 budget). Preorder status |
| M12 | **JGB37-520 / 37GB520 / XD-37GB520 12 V geared motor with encoder** (Chinese 37 mm class) | various, e.g. 178 RPM | ~10 W class | **≈ $11.75** (AliExpress, via price-tracker) · **≈ $14.75** (aliexpress.ru listing) | 🔎 [alitools.io listing (11.75 $)](https://alitools.io/es/showcase/engranaje-en-miniatura-de-xd-37gb520-motor-de-engranaje-cc-de-baja-velocidad-alto-torque-direccion-ajustable-12v-24v-10w-32978707442) · 🔎 [imall listing for the same AliExpress item](https://imall.com/product/37-dc-gear-motor-10W-12-V24V-mini-geared-low-speed-high-torque-can-adjustable-reversible-electric-tools-37GB520/Home-Improvement-Electrical-Equipment-Supplies/aliexpress.com/32789673607/565-12783777/en) | **This is the budget workhorse.** Exact AliExpress listing prices vary by ratio/seller — treat the number as indicative, verify on the live listing |
| M13 | **Maxon RE25 / RE35 + planetary gearhead** | — | — | ❓ **unconfirmed** | — | A 2017 US capstone BOM lists **Maxon RE 35 15 V @ $20** used ([sce.nau.edu Final Report PDF](https://sce.nau.edu/capstone/projects/ME/2017/SumoBotA/Final%20Report.pdf)) — that is a **used/second-hand** price, not a new-unit price. **New Maxon is well outside a $500 build** (JSumo's Maxon-based 3 kg Apocalypse robot sells for **$2,450**). Buy used Maxon on eBay/Polish surplus if you want that route |
| M14 | Ukrainian-available equivalent | — | — | ❓ **unconfirmed** | see §7 | Search hits exist ([vselandia.com "мотор редуктор" tag](https://vselandia.com/search/?tag=%D0%BC%D0%BE%D1%82%D0%BE%D1%80%20%D1%80%D0%B5%D0%B4%D1%83%D0%BA%D1%82%D0%BE%D1%80), [robostore.com.ua](https://robostore.com.ua)) but **no price could be read**. ⚠️ *Gap: a follow-up pass on prom.ua/rozetka category pages in Ukrainian is needed* |

**Motor selection guidance (engineering judgement, no citation):** for a magnetic 1 kg robot with 4 magnets ≈ 20 kg downforce, you want ≥15 kg·cm per motor to break traction; for 3 kg with ~35 kg downforce you want ≥27 kg·cm (M1) or better. **2 × M1 (#4744, $77.90)** is the safe, well-documented choice; **2 × M12 (≈$24–30 total)** is the budget choice.

---

### 2.2 Motor drivers / H-bridges (1–2 per robot)

| # | Exact product name | Current rating | Price | Source URL | Notes |
|---|---|---|---|---|---|
| D1 | **Double BTS7960 43 A High-Power IBT-2 motor driver module** | 43 A peak (continuous far lower — typically ~10–20 A without heroic heatsinking) | **≈ $2.84–$2.90** | 🔎 [alitools.io listing, $2.84](https://alitools.io/ru/showcase/dvoynoy-bts7960-43a-h-most-moshtniy-moduly-drayvera-dvigatelya-diy-umniy-avtomobilyniy-diagnosticheskiy-tok-1005001543753471) · 🔎 [imall listing, $2.90](https://imall.com/product/High-power-motor-drive-module-BTS7960-43A-current-limiting-control-semiconductor-refrigeration/Electronic-Components-Supplies-Electronics-Stocks/aliexpress.ru/1005007028767652/1381-261731290/en) | ⚠️ The "43 A" is the chip's peak rating, **not** achievable continously — derate hard. **This is the price/performance winner** despite that |
| D2 | Ukrainian retail: **Кроковий Драйвер двигуна BTS7960 43A H-bridge** (Prom.ua seller, Polonne) | 43 A peak | **186.60 ₴ ≈ $4.18** | ✅ [prom.ua/ua/p2174139322](https://prom.ua/ua/p2174139322-shagovyj-drajver-dvigatelya.html) | ✅ **In-country, next-day, no customs.** Only ~$1.30 more than AliExpress — **buy these locally** |
| D3 | **Драйвер крокового двигуна BTS7960, до 43А, Arduino** (Rozetka) | 43 A peak | ❓ **unconfirmed** (page did not render a price) | ✅ page exists: [rozetka.com.ua/ua/386601609](https://rozetka.com.ua/ua/386601609/p386601609/) | Alternative to D2; also at [krons.com.ua](https://krons.com.ua/ua-ru/programmatory_kontrollery_arduino/dvigateli_kontrollery_shim/drajver_shagovogo_dvigatelya_bts7960_do_43a_arduino) and [kosmodrom.ua](https://www.kosmodrom.ua/index.php/kontroler-krokovogo-dviguna/bts7960-modul.html) (prices unconfirmed) |
| D4 | **Контролер колекторного двигуна BTS7960-MODUL** (arduino.ua, Kyiv) | 43 A peak | ❓ **unconfirmed** (page identified, price not read) | ✅ [arduino.ua/prod5016](https://arduino.ua/prod5016-kontroller-shagovogo-dvigatelya-bts7960-modul) | |
| D5 | **Cytron MDD10A — 10 A 5 V–30 V DC Motor Driver (2 Channels)** | **10 A continuous per channel** | ❓ **unconfirmed** | ✅ [cytron.io product page](https://www.cytron.io/th-warehouse/p-10amp-5v-30v-dc-motor-driver-2-channels) | **Honest 10 A continuous** beats a fake 43 A peak for reliability. Check Cytron shipping to UA |
| D6 | Cytron **SmartDrive Duo / MDDS30** (7–35 V, 2 ch) | 30 A peak | ❓ **unconfirmed** | ✅ [cytron.io](https://www.cytron.io/c-dc-motor/c-motor-driver/p-10amp-7v-35v-smartdrive-dc-motor-driver-2-channels) | |
| D7 | **Pololu G2 High-Power Motor Driver 24v13** (item #2992) | 13 A continuous | ❓ **unconfirmed** (US price not read; Canadian distributor page identified) | ✅ [pololu.com/product/2992](https://www.pololu.com/product/2992) · 🔎 [abra-electronics.com listing](https://abra-electronics.com/electromechanical/motors/motor-controllers/2992-pololu-pololu-g2-high-power-motor-driver-24v13.html?sl=en) | Pololu's own note: they recommend a driver rated **above motor stall current** — 37D stalls at 5.5 A, so 13 A continuous is comfortable |
| D8 | **Pololu G2 High-Power Motor Driver 18v15** / 24v21 (item #2741 in UA listing) | 15 A / 21 A cont. | ❓ **unconfirmed** | ✅ [pololu.com G2 18v15](https://www.pololu.com/product/1362) · ✅ [arduino.ua/prod2741 — "Потужний драйвер колекторного двигуна G2 24В 21А 24v21 від Pololu"](https://arduino.ua/prod2741-moshhnii-draiver-kollektornogo-dvigatelya-g2-24v-21a-24v21-ot-pololu) | ✅ **Pololu G2 is stocked in Kyiv at arduino.ua** — notable find, price needs confirming |
| D9 | **Pololu VNH5019 Motor Driver Carrier** (item #1451) | 30 A peak / ~12 A cont. | ❓ **unconfirmed** | ✅ [pololu.com/product/1451](https://www.pololu.com/product/1451) | Single-channel; classic 37D companion |
| D10 | **Pololu Dual VNH5019 Motor Driver Shield for Arduino** (item #2507) | 2 × VNH5019 | ❓ **unconfirmed** | ✅ [pololu.com/product/2507](https://www.pololu.com/product/2507) | Stacks on an Uno — but **too big/heavy** for mini-sumo |
| D11 | **DRV8871** driver breakout | 3.6 A peak / ~2 A cont. | ❓ **unconfirmed** | — | ⚠️ **Not recommended** for 37D-class motors; 2 A continuous is below what a stalled 5.5 A motor will pull |
| D12 | **Dual G2 High-Power Motor Driver 24v14 Shield for Arduino** (#2516) | 14 A cont. × 2 | ❓ **unconfirmed** | ✅ [pololu.com/product/2516](https://www.pololu.com/product/2516) | One board, two motors, tidy wiring |

**Decision:** **2 × BTS7960 (one per motor) ≈ $6–8.40 total.** Cheapest, and locally available at 186.60 ₴. If reliability matters more than $20, use **1 × Cytron MDD10A** or **1 × Pololu Dual G2**.

---

### 2.3 Microcontroller, reflectance sensors, regulators, battery

#### Microcontroller

| # | Product | Price | Source URL | Notes |
|---|---|---|---|---|
| U1 | **Arduino Nano A000005 (genuine, Italy)** @ arduino.ua | **1 316 ₴ ≈ $29.45** (2+ = 1 263 ₴, 3+ = 1 211 ₴) | ✅ [arduino.ua/prod179](https://arduino.ua/prod179-arduino-nano-a000005) | ✅ **In stock, Kyiv, 6-month warranty.** Genuine = 2–4× clone price |
| U2 | **Плата Arduino Nano v3.0 ATmega328P Type-C** @ Prom.ua | **244 ₴ ≈ $5.46** | 🔎 [prom.ua/ua/p2279577218](https://prom.ua/ua/p2279577218-plata-arduino-nano.html) | 🔎 Best value Nano in Ukraine; clone/CH340-class |
| U3 | Arduino Nano V3.0 ATmega328P Type-C @ Prom.ua (other seller) | **525 ₴ ≈ $11.75** | 🔎 [prom.ua/p2869051925](https://prom.ua/p2869051925-plata-arduino-nano.html) | Shows the local price spread — always compare sellers |
| U4 | **Arduino NANO V3.0 ATmega328/CH340G** @ Bigl.ua | **387.60 ₴ ≈ $8.68** | 🔎 [bigl.ua/ua/p544208253](https://bigl.ua/ua/p544208253-arduino-nano-v30) | |
| U5 | Плата Arduino Nano V3.0 ... CH340 @ Rozetka | ❓ **unconfirmed** | ✅ [rozetka.com.ua/ua/439235534](https://rozetka.com.ua/ua/439235534/p439235534/) | |
| U6 | **Arduino Uno Rev3 (original, Italy) A000066** @ arduino.ua | **1 448 ₴ ≈ $32.41** | ✅ [arduino.ua related listing on prod179](https://arduino.ua/prod179-arduino-nano-a000005) (rendered in the "recommended" block) · direct page [arduino.ua/prod32](https://arduino.ua/prod32-arduino-uno-rev3-a000066) | Too big for mini-sumo; fine for a 3 kg prototype |
| U7 | **ESP32 / STM32 "Blue Pill" / STM32F401** | ❓ **unconfirmed** | ✅ category exists: [arduino.ua ESP8266/ESP32 category](https://arduino.ua/cat122-esp8266) | ⚠️ **Gap.** ESP32 is the right choice if you want more RAM/PWM channels + telemetry; Blue Pill if you want cheap 32-bit. Prices not read. AliExpress typically $2–5 |
| U8 | **JSumo "Genesis" Arduino Nano mainboard** (sumo-specific carrier) | Included in M1 kit ($245); sold separately — ❓ **unconfirmed** | [jsumo.com robot-kits](https://www.jsumo.com/robot-kits) · [Genesis manual](https://blog.jsumo.com/manual-genesis-ver-2-big-changes-robot-makers/) | Sensor headers + motor driver on one board, screws straight into the chassis |

#### Reflectance / edge-detection sensors (the dohyo edge is your life)

| # | Product | Price | Source URL | Notes |
|---|---|---|---|---|
| S1 | **Pololu QTR-8A Reflectance Sensor Array** (#960) | ❓ **unconfirmed** (Pololu page + DigiKey + RobotShop CA listings all identified) | ✅ [pololu.com/product/960](https://www.pololu.com/product/960) · [DigiKey 960](https://www.digikey.com/en/products/detail/pololu/960/10450565) · [RobotShop CA](https://ca.robotshop.com/products/pololu-qtr-8a-infrared-sensor-array) | 8 analog channels. **QTR-8A = analog** (needs 8 ADC pins); **QTR-8RC = RC-time** (needs only 1 timer pin, better on a Nano) |
| S2 | **Pololu QTR-8RC Reflectance Sensor Array** (#961) | ❓ **unconfirmed** | ✅ [pololu.com/product/961](https://www.pololu.com/product/961/resources) | |
| S3 | **QTR-8RC 8-channel IR array (clone, HYS301)** | ❓ **unconfirmed** | ✅ [othoba.com listing](https://othoba.com/qtr-8rc-8-channels-digital-infrared-reflectance-sensor-array-qtr-8rc-ir-infrared-line-tracking-qtr-8rc-8-channel-sensor-array-hys301-line-following-sensor-module-for-arduino-11-pin-leads-udvabony-bd-4-2) | Clone of S2 at a fraction of the price; typical AliExpress equivalents are $2–4 |
| S4 | **8-channel IR array module** (generic) | ❓ **unconfirmed** | ✅ [embeddinator.com listing](https://www.embeddinator.com/product/8-channel-ir-array-sensor-infrared-detection-module) | |
| S5 | **QTR-8RC Line Sensor** sold by JSumo | ❓ **unconfirmed** (product page identified) | ✅ [jsumo.com/qtr-8rc-line-sensor-rc-time-digital](https://www.jsumo.com/qtr-8rc-line-sensor-rc-time-digital) | |
| S6 | **Датчик лінії KY-033 на TCRT5000** @ arduino.ua | ❓ **unconfirmed** | ✅ [arduino.ua/prod2557](https://arduino.ua/prod2557-datchik-linii-ky-033-na-tcrt5000) | Cheap individual edge sensors; use 3–5 across the front |
| S7 | **Модуль ІЧ-відражувача TCRT5000** @ arduino.ua | ❓ **unconfirmed** | ✅ [arduino.ua/prod1209](https://arduino.ua/ru/prod1209-modyl-ik-otrajatelya-tcrt5000) | Bare TCRT5000 module — cheapest edge sensors |
| S8 | **Pololu QTR-1A / QRE1113** | ❓ **unconfirmed** | ✅ [Pololu QTR category](https://www.pololu.com/product/960) | JSumo's M1 kit uses **QTR1A ×2 + MR45 opponent sensors ×3** |
| S9 | **JSumo JS40F / JS60F Infrared Sensor** (opponent detection, background-suppression) | ❓ **unconfirmed** | ✅ [jsumo.com/js40f-digital-distance-sensor-min-40-cm-range](https://www.jsumo.com/js40f-digital-distance-sensor-min-40-cm-range) · [JS60F 60 cm](https://www.jsumo.com/js60f-infrared-sensor-60cm-range-with-background-suspension) | Sumo-specific: detects the *opponent*, ignores the white floor. **Important for a winning autonomous bot** |

#### 5 V regulation

| # | Product | Price | Source URL | Notes |
|---|---|---|---|---|
| R1 | **DC-DC понижуючий конвертер LM2596 (4.5–40 V → 3–35 V)** @ arduino.ua | **49 ₴ ≈ $1.10** | ✅ [arduino.ua/prod650](https://arduino.ua/prod650-dc-dc-ponijyuchii-konverter-lm2596-z-4-5-40v-do-3-35v) | Cheapest viable 5 V rail. ⚠️ LM2596 is noisy/slow — acceptable for logic, not for a clean ADC reference |
| R2 | **Pololu step-down / step-up 5 V regulators** | ❓ **unconfirmed** | ✅ [arduino.ua Pololu step-down category](https://arduino.ua/cat420-peretvoruvachi-ponijyuchi-pololu) · [step-up](https://arduino.ua/cat421-peretvoruvachi-pidvishhyuchi-pololu) · [bidirectional](https://arduino.ua/cat573-peretvoruvachi-dvonapravleni-pololu) · [rcscomponents.kiev.ua Pololu, 5 V output](https://www.rcscomponents.kiev.ua/pololu/page=18) | ✅ **Pololu regulators are locally stocked (Kyiv)** — buy local, avoid US shipping |
| R3 | Pololu 5 V regulator direct | ❓ **unconfirmed** | ✅ [pololu.com voltage regulators](https://www.pololu.com/category/136/voltage-regulators) | |

#### Battery + charger

| # | Product | Spec | Price | Source URL | Notes |
|---|---|---|---|---|---|
| B1 | **Fullymax 11.1 V 2200 mAh Li-Po 3S 40C T-plug** @ Rozetka | 3S, 2200 mAh, **40C = 88 A** | ❓ **unconfirmed** | ✅ page identified: [rozetka.com.ua/ua/152432386](https://rozetka.com.ua/ua/152432386/p152432386/) | **This is the right spec class.** 88 A burst comfortably covers 2 × 5.5 A stall + logic |
| B2 | **ZIPPY Compact 1800 mAh 3S 40C LiPo Pack** @ arduino.ua | 3S, 1800 mAh, 40C | ❓ **unconfirmed** | ✅ [arduino.ua/prod696](https://arduino.ua/prod696-akkymylyator-zippy-compact-1800mah-3s-40c-lipo-pack) | |
| B3 | **3S LiPo category** @ Prom.ua | — | ❓ **unconfirmed** | ✅ [prom.ua 3S LiPo category](https://prom.ua/ua/Akkumulyator-lipo-3s-11-1v.html?category=52808) | Category is dominated by **laptop replacement batteries** — filter carefully, do not buy those |
| B4 | **3S 11.1 V LiPo category** @ modelistam.com.ua | — | ❓ **unconfirmed** | ✅ [modelistam.com.ua LiPo 11.1 V](https://modelistam.com.ua/ua/akkumulyatory/akkumulyatory-111-lipo-c-128/) | ✅ **RC/hobby shop — the correct place to buy LiPo in Ukraine** |
| B5 | **LiPo balance charger (IMAX B6 / SkyRC class)** | — | ❓ **unconfirmed** | ✅ [arduino.ua battery chargers](https://arduino.ua/cat80-zaryadnie-ustroistva) · [JSumo battery chargers](https://www.jsumo.com/battery-chargers) | ⚠️ **Gap.** Required — JSumo explicitly lists "LiPo Battery Charger" as a required extra for its own M1 kit |
| B6 | 18650 cells / 3S–4S 18650 packs / LiFePO4 / BMS | — | ❓ **unconfirmed** | ✅ [JSumo 18650 cells](https://www.jsumo.com/18650-liion-rechargeable-battery-cells) · [JSumo BMS](https://www.jsumo.com/battery-management-circuits) · [JSumo 4S LiPo](https://www.jsumo.com/4s-lipo-batteries) | LiPo is lighter per Wh than 18650 — for a **weight-limited** sumo bot, LiPo wins |

**Battery sizing rationale (engineering judgement):** a 1 kg mini-sumo match lasts ~30 s per round. A **3S 850–1300 mAh 45–75C** pack is plenty and saves weight; **2200 mAh 3S 40C (B1)** is the safe 3 kg choice. **4S** only if your motors/driver tolerate it (37D is rated 12 V nominal — 4S = 14.8 V nominal / 16.8 V full, which will shorten motor life; **stay 3S for Pololu 37D**).

---

### 2.4 Neodymium magnets — the single most important BOM section

All \(\text{₴}\) → \(\$\) at 44.6819. "Holding force" is the vendor's own stated figure (typically measured against thick steel, direct contact) — **your real force at a 1 mm air gap will be substantially lower**, commonly half or less.

#### Disc magnets — discs (MERKON, Kyiv, Ukraine)

| Size | Grade | Holding force (vendor) | 1 pc | 30 pc | 100 pc | 5000 pc | URL | Stock |
|---|---|---|---|---|---|---|---|---|
| **Ø20 × 5 mm** | **N38** | **≈ 6 kg** | **36.00 ₴ ≈ $0.81** | 35.50 ₴ ≈ $0.79 | **35.00 ₴ ≈ $0.78** | 34.50 ₴ ≈ $0.77 | ✅ [merkon.ua/magnit-neodymovyy-dysk-20x46-mm](https://merkon.ua/magnit-neodymovyy-dysk-20x46-mm/) | **2 171 pcs in stock**; min order 2 pcs; **1–2 working days**; 12.6 g each |

#### Disc magnets — discs (Supermagnit, Ukraine)

| Size | Grade | Holding force (vendor) | 1 pc | 50 pc | 1000 pc | URL | Stock |
|---|---|---|---|---|---|---|---|
| **Ø20 × 5 mm** | **N38** | **≈ 5.2 kg** | **57.22 ₴ ≈ $1.28** | 48.92 ₴ ≈ $1.09 | 46.04 ₴ ≈ $1.03 | ✅ [supermagnit.net.ua/uk/magnity-diski/m-disk-20x5](https://supermagnit.net.ua/uk/magnity-diski/m-disk-20x5) | 12.00 g |
| Ø5 × 5 mm | N38 | ≈ 0.90 kg | 5.50 ₴ ≈ $0.12 | — | 4.36 ₴ ≈ $0.10 | ✅ [m-disk-5x5](https://supermagnit.net.ua/uk/magnity-diski/m-disk-5x5) | 300+/1300+ breakpoints |
| Ø5 × 10 mm | N38 | ≈ 1.10 kg | 10.70 ₴ ≈ $0.24 | — | 8.90 ₴ ≈ $0.20 | ✅ [m-disk-5x10](https://supermagnit.net.ua/uk/magnity-diski/m-disk-5x10) | |
| Ø5 × 3 mm | N38 | ≈ 0.43 kg | 3.85 ₴ ≈ $0.09 | — | 2.95 ₴ ≈ $0.07 | ✅ [m-disk-5x3](https://supermagnit.net.ua/uk/magnity-diski/m-disk-5x3) | |
| Ø4 × 8 mm | N38 | ≈ 1.0 kg | 5.87 ₴ ≈ $0.13 | — | 3.65 ₴ ≈ $0.08 | ✅ [m-disk-4x8](https://supermagnit.net.ua/uk/magnity-diski/m-disk-4x8) | |
| Full disc range (Ø1 → Ø20+) | N38 | 0.1 → 5.2 kg | from **1.04 ₴ ≈ $0.02** | — | — | ✅ [full disc catalogue](https://supermagnit.net.ua/uk/magnity-diski) | |

> **Note on grade:** both Ukrainian suppliers sell **N38**, not N42–N52. N38 is ~10–20 % weaker than N42 for the same volume. If you need N52, you must import (AliExpress / supermagnete.de / KJ Magnetics).

#### Block / rectangular magnets (MERKON, Kyiv)

| Size | Holding force (vendor) | 1 pc | 20 pc | 100 pc | 10000 pc | URL | Stock |
|---|---|---|---|---|---|---|---|
| **9 × 4.5 × 4.5 mm** (listed as "10×5×5") — **m-72** | **≈ 1.2 kg** | **5.11 ₴ ≈ $0.11** | **4.90 ₴ ≈ $0.11** | **4.67 ₴ ≈ $0.10** | 4.45 ₴ ≈ $0.10 | ✅ [merkon.ua/magnit-neodymovyy-pryamokutnyk-10x5x5-mm](https://merkon.ua/magnit-neodymovyy-pryamokutnyk-10x5x5-mm/) | **30 765 pcs** |
| 12 × 10 × 5 mm — m-156 | ≈ 2.9 kg | 17.62 ₴ ≈ $0.39 | — | 17.13 ₴ ≈ $0.38 | 16.88 ₴ ≈ $0.38 (5000+) | ✅ [merkon.ua/magnit-neodymovyy-pryamokutnyk-12x10x45-mm](https://merkon.ua/magnit-neodymovyy-pryamokutnyk-12x10x45-mm/) | **5 020 pcs** |
| 11.8 × 9.3 × 2.6 mm — m-155 | ≈ 2.2 kg | 10.76 ₴ ≈ $0.24 | — | 10.34 ₴ ≈ $0.23 | — | ✅ [merkon.ua/magnit-neodymovyy-pryamokutnyk-12x10x25-mm](https://merkon.ua/magnit-neodymovyy-pryamokutnyk-12x10x25-mm/) | 6 737 pcs |
| 9.4 × 9.4 × 2.7 mm — m-231 | ≈ 1.4 kg | 7.09 ₴ ≈ $0.16 | — | 6.67 ₴ ≈ $0.15 | — | ✅ [merkon.ua/magnit-neodymovyy-pryamokutnyk-96x96x26-mm](https://merkon.ua/magnit-neodymovyy-pryamokutnyk-96x96x26-mm/) | 4 111 pcs |
| 9.5 × 9.5 × 1.7 mm — m-224 | ≈ 0.8 kg | 4.41 ₴ ≈ $0.10 | — | 3.79 ₴ ≈ $0.08 | — | ✅ [merkon.ua/magnit-neodymovyy-pryamokutnyk-10x10x16-mm](https://merkon.ua/magnit-neodymovyy-pryamokutnyk-10x10x16-mm/) | 14 308 pcs |
| 9.4 × 3.8 × 1.8 mm — m-257 | ≈ 0.45 kg | 2.22 ₴ ≈ $0.05 | — | 2.18 ₴ ≈ $0.05 | — | ✅ [merkon.ua/magnit-neodymovyy-pryamokutnyk-98x38x18-mm](https://merkon.ua/magnit-neodymovyy-pryamokutnyk-98x38x18-mm/) | 42 701 pcs |
| 4.8 × 4.8 × 2.8 mm — m-222 | ≈ 0.38 kg | 2.10 ₴ ≈ $0.05 | — | — | — | ✅ [merkon.ua/magnit-neodymovyy-pryamokutnyk-48x48x26-mm](https://merkon.ua/magnit-neodymovyy-pryamokutnyk-48x48x26-mm/) | 38 061 pcs |
| ✳ **20 × 10 × 5 mm with hole 4 × 6.5 mm** | (vendor: "3 kg" class, N42, has hole) | **128 ₴ ≈ $2.86** | — | — | — | 🔎 [bigl.ua/ua/p2114790476-neodimovyj-magnit-20x10x5mm](https://bigl.ua/ua/p2114790476-neodimovyj-magnit-20x10x5mm) | 🔎 Search-result title |
| ✳ **20 × 10 × 5 mm N42 rectangular with hole** @ Epicentr K | 3 kg | ❓ **unconfirmed** | — | — | — | ✅ [epicentrk.ua product page](https://epicentrk.ua/ua/shop/mplc-magnit-neodimovij-sila-n42-pramokutnij-z-otvorom-3-kg-20h10h5-mm-mg-432-1efa0c18-2727-6f56-963a-b1e9b0013337.html) | |
| ✳ **10 × 5 × 5 mm N38** @ supermagnit | ≈ 2.265 kg (vendor claim) | **14.10 ₴ ≈ $0.32** | — | 12.38 ₴ ≈ $0.28 | 9.94 ₴ ≈ $0.18 (1000+) | ✅ [supermagnit.net.ua/uk/shop/pramougolnik/pramougolnik-10x5x5](https://supermagnit.net.ua/uk/shop/pramougolnik/pramougolnik-10x5x5) | ⚠️ **Немає в наявності (out of stock)** — use MERKON m-72 instead |

#### Countersunk / ring magnets (for bolting through a plate — the tidy mounting option)

| Size | Grade | Price | URL | Notes |
|---|---|---|---|---|
| **Ø20 × 5 mm countersunk, hole 4.5/7.5 mm** | — | ❓ **unconfirmed** | ✅ [onyx-magnet.com product page](https://onyx-magnet.com/ua/neodimovye-magnity/magnity-s-zenkovkoy/neodimovyy-magnit-kolco-20x5mm-s-zenkovkoy-4575mm) | ✅ **The right part for a magnetic sumo bot**: M4 countersunk screw → magnet sits flush in a pocket, gap stays small, survives impacts |
| **Ø20 × 5 mm countersunk, hole 5 mm (N35)** | N35 | ❓ **unconfirmed** | ✅ [onesapan.com product page](https://onesapan.com/potuzhniy-neodimoviy-magnit-ndfeb-n35-krugliy-20h5-mm-shayba-disk-z-otvorom-5-mm-pid-kriplennya-z-potayem/reviews/) | |
| Full countersunk-disc category | N38 | from **35.00 ₴ ≈ $0.78** | ✅ [merkon.ua/dysky-z-otvorom](https://merkon.ua/dysky-z-otvorom/) | ✅ MERKON stocks a whole countersunk-disc line |
| Full ring-magnet category | — | — | ✅ [supermagnit.net.ua/uk/shop/kolco](https://supermagnit.net.ua/uk/shop/kolco) | |
| **20 × 10 × 5 mm N52 block "Strong"** | **N52** | ❓ **unconfirmed** | ✅ [jsumo.com/neodymium-magnet-block-strong-n52-10mm-x-5mm-x-20-mm](https://www.jsumo.com/neodymium-magnet-block-strong-n52-10mm-x-5mm-x-20-mm) | ✅ Sumo vendor sells N52 blocks — the **highest grade** found |
| supermagnete.de (EU, N35–N52 full range incl. 20×10×5 and 20×5) | N35–N52 | ❓ **unconfirmed** (catalogue PDFs exist: e.g. [Q-20-10-05-N 20×10×5](https://www.supermagnete.hu/ger/catalog.pdf), [S-20-05-N Ø20×5](https://www.supermagnete.it/ger/catalog.pdf)) | ✅ [supermagnete.de](https://www.supermagnete.de) | ⚠️ **Best N52 source in the EU**, ships EU; UA shipping terms unconfirmed |
| KJ Magnetics / JC Magnetics (US) | up to N52, **20 × 5 mm N52 epoxy-coated** | ❓ **unconfirmed** | ✅ [jc-magnetics.com 20x5mm N52](https://www.jc-magnetics.com/20x5mm-neodymium-magnets-n52-epoxy-coated) · [kjmagnetics.com](https://www.kjmagnetics.com) | Epoxy coating resists chipping — good for combat, but US shipping to UA is painful |

#### 🏆 Best pull force per dollar — my ranking

Computed from the **confirmed** MERKON prices above (holding force ÷ price, using 1-pc prices, converted at 44.6819):

| Rank | Magnet | Force | Price | **kg of holding force per $1** |
|---|---|---|---|---|
| 🥇 | **MERKON 9 × 4.5 × 4.5 mm block (m-72) — "10×5×5"** | ≈ 1.2 kg | $0.11 | **≈ 10.6 kg/$** |
| 🥈 | **MERKON Ø20 × 5 mm disc** | ≈ 6 kg | $0.81 | **≈ 7.4 kg/$** |
| 🥉 | MERKON 9.4 × 9.4 × 2.7 mm (m-231) | ≈ 1.4 kg | $0.16 | ≈ 8.8 kg/$ (thin — see note) |
| 4 | MERKON 12 × 10 × 5 mm (m-156) | ≈ 2.9 kg | $0.39 | ≈ 7.4 kg/$ |
| 5 | supermagnit Ø20 × 5 mm | ≈ 5.2 kg | $1.28 | ≈ 4.1 kg/$ |
| 6 | supermagnit 10 × 5 × 5 mm | ≈ 2.27 kg | $0.32 | ≈ 7.2 kg/$ — **but out of stock** |

**Recommendation:**
- **Cheapest downforce per dollar:** buy **40–60 × MERKON m-72 (10×5×5, 1.2 kg each)** for ~$4.40–6.60 and stack them in 3D-printed pockets. 20 of them = **24 kg** of nominal force for **$2.20**. **This is by far the best value in the entire BOM.**
- **Cleanest engineering solution:** **8–12 × Ø20×5 mm countersunk N38 discs** (MERKON countersunk line, from 35.00 ₴ ≈ $0.78) bolt-mounted through the belly plate. 10 × 6 kg = **60 kg nominal** (≈ 20–30 kg at realistic gap) for **≈ $8**. Add or remove magnets to tune.
- **If you can import:** get **N52 20×10×5 blocks** (JSumo) or **N52 Ø20×5** (KJ/JC Magnetics) — ~15–25 % more force per gram than N38, which matters because **magnet mass counts against your 1 kg / 3 kg limit.** A Ø20×5 N38 disc is 12.6 g; 10 of them = **126 g of your 1000 g budget.** That is a real design constraint, so **prefer N52 or thicker-in-fewer-pieces** if importing.
- **Bulk-buying note:** MERKON's own breakpoints barely reward bulk (36.00 → 35.00 ₴ from 1 to 100 pcs, i.e. **3 % off for 100×**). AliExpress/supermagnete are where bulk discounts are real. **For 10–50 pieces, just buy locally at MERKON — the convenience beats the 3 %.**

---

### 2.5 Wheels and traction

| # | Product | Size | Price | Source URL | Notes |
|---|---|---|---|---|---|
| W1 | **JSumo SLT20 Aluminum — Silicone Wheel Set** | **33 × 20 mm**, pair | ❓ **unconfirmed** | ✅ [jsumo.com/slt20-aluminum-silicone-wheel-set-33mmx20mm-pair](https://www.jsumo.com/slt20-aluminum-silicone-wheel-set-33mmx20mm-pair) | ✅ **This is the part in the M1 kit.** Aluminum hub + silicone tyre = the sumo standard |
| W2 | **JSumo SLT20P Steel Silicone Wheel Set** | **33 × 20 mm**, pair | ❓ **unconfirmed** | ✅ [jsumo.com/slt20p-steel-silicone-wheel-set-33mm-x-20mm-pair](https://www.jsumo.com/slt20p-steel-silicone-wheel-set-33mm-x-20mm-pair) | Steel hub version — heavier, better for a 3 kg build's inertia |
| W3 | **JSumo JS7444 Aluminum Silicone Wheel Pair** | **74 mm** dia | ❓ **unconfirmed** | ✅ [jsumo.com/js7444-aluminum-silicone-wheel-pair-74mm-diameter](https://www.jsumo.com/js7444-aluminum-silicone-wheel-pair-74mm-diameter) | 74 mm is **outside your 30–60 mm** target; listed for completeness |
| W4 | **JSumo Silicone Wheel Sets / Replacement Silicone Tyres** (full category) | various | ❓ **unconfirmed** | ✅ [silicone wheel sets](https://www.jsumo.com/silicone-wheel-sets) · [replacement tyres](https://www.jsumo.com/replacement-silicone-tyres) | ✅ **Replacement tyres are sold separately — buy spares** |
| W5 | **Pololu Wheel 42 × 19 mm Pair** — POLOLU-1090 | 42 × 19 mm, 3 mm D-shaft | ❓ **unconfirmed** | ✅ [TME PL product page](https://www.tme.eu/lt/en/details/pololu-1090/accessories-for-robotics-and-rc/pololu/pololu-wheel-42x19mm-pair/) · [active-robots.com](https://www.active-robots.com/pololu-wheel-42x19mm-pair.html) | ⚠️ 3 mm shaft — **not** a direct fit for 37D's 6 mm shaft |
| W6 | **Pololu Wheel 80 × 10 mm Pair** (#1430) / **90 × 10 mm Pair** (#1439) | 80 / 90 mm | ❓ **unconfirmed** | ✅ [pololu.com/product/1430](https://www.pololu.com/product/1430) · [#1439](https://www.pololu.com/product/1439) | **These are the Pololu wheels that actually fit 37D** (via the #1083 hub below) — but 80–90 mm is **too large** for a mini-sumo footprint |
| W7 | **Pololu Universal Aluminum Mounting Hub for 6 mm Shaft, M3 Holes (2-Pack)** — #1999 | for 6 mm shaft | ❓ **unconfirmed** | ✅ [pololu.com/product/1999](https://www.pololu.com/product/1999) | ✅ **Essential part** — bolts a custom/3D-printed wheel to a 37D shaft |
| W8 | Pololu Universal Aluminum Mounting Hub for 6 mm Shaft, #4-40 Holes (2-Pack) — #1083 | for 6 mm shaft | ❓ **unconfirmed** | ✅ [pololu.com/product/1083](https://www.pololu.com/product/1083) | Imperial-screw version |
| W9 | **12 mm Hex Wheel Adapter for 6 mm Shaft (2-Pack)** — #2686 / extended #2687 | 6 mm → 12 mm hex | ❓ **unconfirmed** | ✅ [pololu.com/product/2686](https://www.pololu.com/product/2686) · [#2687](https://www.pololu.com/product/2687) | ✅ Opens up the entire **RC hobby wheel** market (see W10) |
| W10 | **Pololu Aluminum Scooter Wheel Adapter for 6 mm Shaft** — #2674 | 6 mm shaft | ❓ **unconfirmed** | ✅ [pololu.com/product/2674](https://www.pololu.com/product/2674) | Lets you bolt on skate/scooter wheels — tons of cheap urethane options at any Ukrainian skate shop |
| W11 | **Ukrainian wheels category** @ arduino.ua | various | ❓ **unconfirmed** | ✅ [arduino.ua/cat280-kolesa](https://arduino.ua/cat280-kolesa) | ⚠️ **Gap.** Category exists, no prices read |
| W12 | **Rubber wheel 40 mm for blue TT gearmotor** | 40 mm | ❓ **unconfirmed** | ✅ [mecabot.com listing (LatAm)](https://www.mecabot.com/products/rueda-para-motorreductor-azul) | For TT motors only — **too small/weak for sumo** |
| W13 | **3D-printable TPU tyres** | 30–60 mm | **$0 (own printer)** | — | ✅ **Recommended.** Print a rigid hub (PETG/ABS) + a **TPU tyre at Shore 85A–95A**. Print the tyre *solid* (100 % infill, 0 top/bottom layers pattern = concentric) for grip. **Cheapest high-traction path, and you can tune diameter per event.** Alternatives: cast your own silicone (Shore 30–40A) into a printed mould — the JSumo/JSumo-style silicone tyres are exactly this |

**Traction physics note (engineering judgement):** on a magnetic dohyo the limiting factor is usually **not** grip — it is **chassis stiffness and magnet gap consistency**. Silicone (Shore 30–40A) beats hard rubber on painted steel for friction coefficient, but it also **deforms under load**, which can close your magnet gap and cause dragging. Budget for **2 spare tyre sets** — silicone tears under shear.

---

### 2.6 Chassis materials and local fabrication

#### Materials

| # | Material | Spec | Price | Source URL | Notes |
|---|---|---|---|---|---|
| C1 | **Лист алюмінієвий 6061 T6 (АД31), 5.0 × 1500 × 3000 mm** @ МеталБудАльянс (Kyiv) | 6061-T6 / AD31, 5 mm | ❓ **unconfirmed** (page loads product data client-side; not readable) | ✅ [metallbudalyans.com.ua product page](https://metallbudalyans.com.ua/ua/catalog/List-alyuminievyy-6061-T6-AD31/List-alyuminievyy-6061-T6-AD31-50h1500h3000-mm) · [full 6061-T6/AD31 catalogue](https://metallbudalyans.com.ua/ua/catalog/List-alyuminievyy-6061-T6-AD31) | ⚠️ **Gap.** ✅ Kyiv warehouse, 6061-T6 **is** stocked. **Recommendation: 6061-T6 at 3–5 mm** for the belly plate (stiffness + magnetic-gap flatness); 2 mm for non-structural brackets. **AD31/6063 is weaker — ask for 6061-T6 or 7075.** Buying a whole 1500×3000 sheet is wasteful for 1–3 robots; **ask the yard for an offcut / "обрізок"** |
| C2 | **Пластина карбонова 2 mm × 200 mm × 300 mm (3K Twill)** @ Хобі Манія | 3K twill carbon, 2 mm | ❓ **unconfirmed** (page loaded but price block not captured) | ✅ [hobbymania.com.ua/p-5987](https://hobbymania.com.ua/p-5987-plastyna-karbonova-2mm-x-200mm-x-300mm) | ✅ **In-country hobby shop, exact size you need.** ⚠️ **Carbon fibre is non-magnetic — it cannot be your magnet mounting plate** (magnets need a steel keeper or thick non-ferrous pocket). Use carbon for the *top* deck |
| C3 | Carbon sheets (other sizes) @ Composites for Model | various | ❓ **unconfirmed** | ✅ [com-posit.com.ua carbon sheets](https://com-posit.com.ua/ru/carbon-products/sheets) | |
| C4 | **Лист титановий 0.5 mm ВТ1-0** @ Prom.ua | Ti grade ВТ1-0, 0.5 mm | **1 500 ₴ ≈ $33.57** | 🔎 [prom.ua/ua/p1438139833-list-titanovyj-vt1](https://prom.ua/ua/p1438139833-list-titanovyj-vt1.html) | 🔎 Price from search-result title. ⚠️ **0.5 mm is too thin for a blade** — it will fold. See C5 |
| C5 | **Лист титановий 4 / 8 / 10 mm ВТ1-0** @ Flagma.ua (Kyiv) | Ti ВТ1-0, 4–10 mm | ❓ **unconfirmed** | ✅ [flagma.ua listing](https://flagma.ua/uk/list-titanovy-4mm-8mm-10mm-vt-1-0-o3111463.html) | ✅ For the blade: **1.0–1.5 mm titanium grade 2/5**, or **hardened 1.5–2 mm spring steel (65Г / 60S2A)** which is cheaper and takes an edge better. Titanium's advantage is *weight* + *no rust*, not hardness |
| C6 | Laser/waterjet service in Kyiv (cut your own sheet) | — | see C7/C8 | ✅ [GRAFIX laser cutting Kyiv](https://grafix.in.ua/lazerne-rizannya-kyiv/) | |

#### Local fabrication — **confirmed price lists**

**Laser Nyvky (Kyiv, пр. Берестейський 94/1)** — ✅ **actual published price list, dated 06.02.2025** ([lasernyvky.com/pricing](https://lasernyvky.com/pricing)):

| Thickness | Black steel (O₂) | Black steel (air) | Stainless (N₂) | Stainless (air) | **Aluminium (air)** |
|---|---|---|---|---|---|
| 0.5 mm | — | 8 ₴/m | 13 ₴/m | 13 ₴/m | **18 ₴/m** |
| 0.8–1.0 mm | — | 9 ₴/m | 15 ₴/m | 14 ₴/m | **22 ₴/m** |
| 1.2 mm | — | 11 ₴/m | 18 ₴/m | 14 ₴/m | **25 ₴/m** |
| 1.5 mm | 12 ₴/m | 11 ₴/m | 23 ₴/m | 14 ₴/m | **27 ₴/m** |
| 2 mm | 13 ₴/m | 12 ₴/m | 29 ₴/m | 17 ₴/m | **35 ₴/m** |
| 3 mm | 18 ₴/m | — | 43 ₴/m | 25 ₴/m | — |
| 4 mm | 22 ₴/m | — | 78 ₴/m | 35 ₴/m | — |
| 5 mm | 26 ₴/m | — | 121 ₴/m | 82 ₴/m | — |
| 6 mm | 34 ₴/m | — | 139 ₴/m | 116 ₴/m | — |

- **Minimum order: 700.00 ₴ ≈ $15.67** (excluding material and piercings).
- **Each pierce = 10 % of the price of 1 running metre** of that material/thickness.
- Accepts **DXF, DWG, CorelDRAW**; contours only, no dimension lines; filename must state material grade, thickness and quantity.
- ✅ **Practical read for you:** a mini-sumo chassis is ~1.0–1.5 m of cut path in 2–3 mm aluminium. At 35 ₴/m that is **~35–52 ₴ of cutting ≈ $0.80–1.20** — **but the 700 ₴ minimum order dominates.** **Batch all three robots' plates into one order** and the cutting cost per robot collapses to near zero.

**Арт-Металл (Art Metall), Kyiv, вул. Якова Гніздовського 1** — ✅ **published indicative 2026 price list** ([art-metall.kyiv.ua](https://art-metall.kyiv.ua/lazerna-rzka-metalu-kiv-2026-czna-vd-1250-grn-porzka-stal-ta-alyumnyu-na-chpk.html)):

| Thickness (mm) | Black steel ₴/m | Stainless ₴/m | **Aluminium ₴/m** |
|---|---|---|---|
| 0.5–1.0 | 14.00 | 20.00 | **25.00** |
| 2.0 | 22.00 | 32.00 | **38.00** |
| 4.0 | 40.00 | 60.00 | **75.00** |
| 6.0 | 65.00 | 100.00 | **120.00** |
| 10.0+ | from 110.00 | from 180.00 | from 210.00 |

- Base rate advertised **"from 12.50 ₴"**; urgent/night/weekend work **+25–50 %**.
- Also offers **CNC press-braking, powder coating, tapping and countersinking**.
- Sheet capacity up to **2000 × 6000 mm**; fibre lasers up to **6 kW**.
- ✅ **Comparison with Laser Nyvky: Art-Metall is ~8 % more expensive on 2 mm aluminium (38 vs 35 ₴/m) but advertises a lower minimum.** Get a quote from both.

**Waterjet cutting (гідроабразивна різка):**
- **UASTAL / Сторожук (Kyiv)** — ✅ [uastal.com/gidroabrazivnaya-rezka](https://uastal.com/gidroabrazivnaya-rezka) · [English version](https://uastal.com/en/gidroabrazivnaya-rezka) — **price list ❓ unconfirmed** (page is JS-rendered)
- **Завод Термо-Пак (Kyiv)** — ✅ [tp-eu.com/en/services/gidroabrazivnaya-porezka](https://tp-eu.com/en/services/gidroabrazivnaya-porezka/) — **price ❓ unconfirmed**
- ⚠️ **Waterjet is 3–6× the cost of laser per metre and is only needed for thick titanium.** For 1–2 mm titanium or steel blades, **laser is fine and much cheaper.** Only use waterjet if you go thicker than ~6 mm Ti.

⚠️ **Overall gap:** I could not obtain a **confirmed** aluminium sheet price per kg or per cut piece, nor a confirmed waterjet price. **Both need a phone/email quote** — the two laser shops above will quote from a DXF within hours (Art-Metall advertises a 15-minute engineer response).

**3D printing:** the team already has this. Print magnet pockets, motor mounts, sensor brackets, wheel hubs and battery trays in **PETG or ABS/ASA** (not PLA — it creeps under the constant magnet load). ⚠️ **Do not print the belly plate** — it will creep and close your magnet gap; use aluminium.

---

### 2.7 Fasteners, bearings, couplings, hubs, standoffs, voltage/current sensing

| # | Product | Spec | Price | Source URL | Notes |
|---|---|---|---|---|---|
| F1 | **Підшипник для самокату ZKL 608 ZZ (608ZR)(80018)** @ Rozetka | 8 × 22 × 7 mm | ❓ **unconfirmed** | ✅ [rozetka.com.ua/ua/401100750](https://rozetka.com.ua/ua/401100750/p401100750/) | |
| F2 | **Підшипник кульковий SKF 608-ZZ (8×22×7)** @ Rozetka | 8 × 22 × 7 mm | ❓ **unconfirmed** | ✅ [rozetka.com.ua/ua/220554211](https://rozetka.com.ua/ua/220554211/p220554211/) | ✅ **608ZZ is stocked in Ukraine at retail.** ✅ **This is the right bearing for a 6–8 mm wheel axle** |
| F3 | Miniature bearings **625ZZ (5×16×5) / 688ZZ (8×16×5) / 623ZZ (3×10×4)** | — | ❓ **unconfirmed** | — | ⚠️ **Gap.** Not sourced locally in this pass. **AliExpress assortment kits (e.g. 100-pc mini bearing kit) are the cheap route** — typically a few dollars per kit |
| F4 | **M3 standoffs / spacers** | — | ❓ **unconfirmed** | ✅ [JSumo standoffs & spacers](https://www.jsumo.com/standoffs-spacers) · [arduino.ua міжплатні стійки](https://arduino.ua/cat273-mejplatnie-stoiki) | ✅ Both categories exist. JSumo's M1 kit ships **20 mm M/F ×5 and 8 mm M/F ×4** |
| F5 | **Screws, nuts & washers (M2/M3 assortments)** | — | ❓ **unconfirmed** | ✅ [JSumo screws/nuts/washers](https://www.jsumo.com/screws-nuts-washers) · [arduino.ua кріплення](https://arduino.ua) | JSumo M1 kit content list gives an exact fastener BOM for a mini-sumo: M3×20 ×6, M3×8 ×10, M3 countersunk ×4, M3 nut ×10, M2×15 ×4, M2 nut ×4 |
| F6 | **Shaft couplers (6 mm → 6 mm, 6 → 4 mm, rigid & flexible)** | — | ❓ **unconfirmed** | ✅ [JSumo shaft couplers](https://www.jsumo.com/shaft-couplers) · [arduino.ua шестерні/втулки/кронштейни](https://arduino.ua/cat274-shesterni-passiki-vtylki-kronshteini) | |
| F7 | **Motor brackets for 37D** | 37D face mount | ❓ **unconfirmed** | ✅ [Pololu Machined Aluminum Bracket #1995](https://www.pololu.com/product/1995) · [Stamped L-Bracket Pair #1084](https://www.pololu.com/product/1084) · [JSumo motor brackets](https://www.jsumo.com/motor-brackets) | ⚠️ In a magnetic bot the motor mounts take **huge** shock loads — use the **machined** bracket (#1995), not the stamped pair |
| F8 | **Bearings category** | — | ❓ **unconfirmed** | ✅ [JSumo bearings](https://www.jsumo.com/bearings) | ✅ For 6 mm output-shaft **support bearings** on the gearbox (a common failure point on 37D under side load) |
| F9 | **Blades & razors** | — | ❓ **unconfirmed** | ✅ [JSumo blades & razors](https://www.jsumo.com/blades-razors) | ✅ Buy the blade; don't make your first one. M1 kit ships a "Mini Katana Blade" |
| F10 | **Hubs & shaft locks** | — | ❓ **unconfirmed** | ✅ [JSumo hubs & shaft locks](https://www.jsumo.com/mounting-hubs-shaft-rings) | |
| V1 | **Датчик струму ACS712 30A GY-712** @ arduino.ua | ±30 A, analog | ❓ **unconfirmed** | ✅ [arduino.ua/prod618](https://arduino.ua/prod618-datchik-toka-acs712-30a-gy-712) | ⚠️ ACS712 is noisy and drifts; fine for "is the motor stalled?" logic |
| V2 | **INA219 / Pololu ACS711EX (±15.5 A) / ACS724 (±5 A)** | — | ❓ **unconfirmed** | ✅ [Pololu current sensors](https://www.pololu.com/category/118/current-sensors) · [arduino.ua датчики струму](https://arduino.ua/cat80-napryga-strym) | ✅ Pololu's ACS711EX is shown on their own 37D product page as the recommended companion |
| V3 | **Battery voltage sense** | — | **$0 — use the ADC** | — | ✅ **You do not need a part.** A 2-resistor divider from the battery to an Arduino analog pin gives pack voltage; or enable the Arduino's internal 1.1 V bandgap reference against Vcc. **Save the money.** |

---

### 2.8 Optional extras (if budget remains)

| # | Product | Price | Source URL | Notes |
|---|---|---|---|---|
| X1 | **VL53L0X ToF laser distance sensor (GY-53)** @ arduino.ua | ❓ **unconfirmed** | ✅ [arduino.ua/prod3932](https://arduino.ua/prod3932-lazernii-datchik-rasstoyaniya-vl53l0x-v2-940nm) | ⚠️ **ToF has poor performance on reflective/painted metal surfaces and in IR-bright arenas.** On a steel dohyo an **IR opponent sensor (S9)** is more reliable than ToF. **Buy ToF only for edge-of-ring backup** |
| X2 | **Акселерометр та гіроскоп INVENSENSE MPU-6050 (оригінал)** @ arduino.ua | ❓ **unconfirmed** | ✅ [arduino.ua/prod6511](https://arduino.ua/prod6511-akselerometr-ta-giroskop-invensense-mpu-6050-original) | ✅ **Genuine InvenSense part, stocked in Kyiv.** A **gyro is genuinely useful**: detect being pushed/rotated and counter-steer. BMI160 is better but harder to source. **MPU6050 is the pragmatic pick** |
| X3 | **MG996R digital metal-gear servo** @ JSumo | **$10.95** | ✅ [jsumo.com/mg996r-servo-motor-digital](https://www.jsumo.com/mg996r-servo-motor-digital) | For a side-blade / flag mechanism |
| X4 | **MG945 metal-gear servo (12 kg)** @ JSumo | **$8.50** | ✅ [jsumo.com/tower-pro-mg945-...](https://www.jsumo.com/tower-pro-mg945-metal-gear-servo-motor-12-kg) | Cheaper, more torque than MG996R |
| X5 | **MG995 analog servo** @ JSumo | **$8.50** | ✅ [jsumo.com/mg995-servo-motor-towerpro](https://www.jsumo.com/mg995-servo-motor-towerpro) | |
| X6 | **MG90S micro servo** @ JSumo | **$4.60** | ✅ [jsumo.com/mg90s-micro-servo-motor](https://www.jsumo.com/mg90s-micro-servo-motor) | Light option |
| X7 | **SG90 micro servo** @ JSumo | **$3.00** | ✅ [jsumo.com/sg90-micro-servo-motor](https://www.jsumo.com/sg90-micro-servo-motor) | ≥500 g of downforce will strip an SG90 instantly — **not for a blade** |
| X8 | **Matador Flag System** @ JSumo | **$34.50** | ✅ [jsumo.com/matador-flag-system](https://www.jsumo.com/matador-flag-system) | ✅ Sumo-specific mechanism |
| X9 | **JSumo "Microstart" start module + remote** | ❓ **unconfirmed** | ✅ [jsumo.com/robot-start-module](https://www.jsumo.com/robot-start-module) | ✅ **Strongly recommended.** Most rule sets require a **5-second start delay**; a start module gives you a legal, repeatable, hands-free start. JSumo lists it as an optional extra for its own kit |
| X10 | **Ultrasonic HC-SR04** @ arduino.ua | **49 ₴ ≈ $1.10** | ✅ [arduino.ua/prod182](https://arduino.ua/prod182-yltrazvykovoi-datchik-rasstoyaniya-hc-sr04) | Surprisingly useful as a **cheap "is the opponent in front?"** sensor; slow (≈50 Hz) but adequate for sumo |
| X11 | **Jumper wires 120-pc set** @ arduino.ua | **129 ₴ ≈ $2.89** | ✅ [arduino.ua related block on prod179](https://arduino.ua/prod179-arduino-nano-a000005) | |
| X12 | **Breadboard MB-102 830-hole** @ arduino.ua | **69 ₴ ≈ $1.54** | ✅ [same page](https://arduino.ua/prod179-arduino-nano-a000005) | |
| X13 | **Jumper set 65-pc** @ arduino.ua | **49 ₴ ≈ $1.10** | ✅ [same page](https://arduino.ua/prod179-arduino-nano-a000005) | |
| X14 | **SD-card module (SPI)** @ arduino.ua | **26 ₴ ≈ $0.58** | ✅ [same page](https://arduino.ua/prod179-arduino-nano-a000005) | Useful for **logging match data** to tune your tactics |
| X15 | **Mabuchi RS-775SF / RS-750SF DC motors** @ JSumo | **$12.50** (was $15.50, −19 %) / **$12.00** | ✅ [jsumo.com/mabuchi-rs-775sf-dc-motor](https://www.jsumo.com/mabuchi-rs-775sf-dc-motor) · [RS-750SF](https://www.jsumo.com/mabuchi-rs-750sf-dc-motor) | **Bare** motors — need an external gearbox. High power, cheap; a hack for advanced teams |

---

## 3. 📋 Total BOM — three budget tiers

Prices below use the **confirmed** figures. Where a line is unconfirmed I substitute a **clearly-labelled estimate** based on the comparable confirmed item, so the totals are usable — **but every estimated line must be re-quoted before purchase.**

### 3.1 (a) Minimal first prototype — target $150–200

Goal: a working, drivable, autonomous magnetic-arena bot to **learn the physics** (magnet gap, traction, sensor thresholds). Not competitive.

| Line | Item | Qty | Unit | Ext. | Source |
|---|---|---|---|---|---|
| 1 | **JGB37-520 / 37GB520 12 V gearmotor** (budget motor) | 2 | ~$13 *(est. from 🔎 $11.75–14.75)* | **$26** | [alitools](https://alitools.io/es/showcase/engranaje-en-miniatura-de-xd-37gb520-motor-de-engranaje-cc-de-baja-velocidad-alto-torque-direccion-ajustable-12v-24v-10w-32978707442) |
| 2 | **BTS7960 43 A driver module** | 2 | **186.60 ₴ ≈ $4.18** | **$8.35** | ✅ [prom.ua](https://prom.ua/ua/p2174139322-shagovyj-drajver-dvigatelya.html) |
| 3 | **Arduino Nano v3.0 ATmega328P Type-C** (clone) | 1 | **244 ₴ ≈ $5.46** | **$5.46** | 🔎 [prom.ua](https://prom.ua/ua/p2279577218-plata-arduino-nano.html) |
| 4 | **TCRT5000 IR line modules** (edge sensors, front row) | 5 | ~$0.50 *(est.)* | **$2.50** | ✅ category [arduino.ua/prod1209](https://arduino.ua/ru/prod1209-modyl-ik-otrajatelya-tcrt5000) |
| 5 | **HC-SR04 ultrasonic** (crude opponent detect) | 1 | **49 ₴ ≈ $1.10** | **$1.10** | ✅ [arduino.ua/prod182](https://arduino.ua/prod182-yltrazvykovoi-datchik-rasstoyaniya-hc-sr04) |
| 6 | **LM2596 buck converter → 5 V** | 1 | **49 ₴ ≈ $1.10** | **$1.10** | ✅ [arduino.ua/prod650](https://arduino.ua/prod650-dc-dc-ponijyuchii-konverter-lm2596-z-4-5-40v-do-3-35v) |
| 7 | **3S LiPo ~2200 mAh 40C** | 1 | ~$22 *(est.)* | **$22** | ✅ spec ref [Rozetka Fullymax 3S 2200 40C](https://rozetka.com.ua/ua/152432386/p152432386/) |
| 8 | **LiPo balance charger (IMAX B6 class)** | 1 | ~$28 *(est.)* | **$28** | ✅ category [arduino.ua](https://arduino.ua/cat80-zaryadnie-ustroistva) |
| 9 | **Neodymium magnets — MERKON Ø20×5 N38, 6 kg each** | 6 | **36.00 ₴ ≈ $0.81** | **$4.84** | ✅ [merkon.ua](https://merkon.ua/magnit-neodymovyy-dysk-20x46-mm/) |
| 10 | **MERKON 10×5×5 blocks** (extra tuning magnets) | 20 | **5.11 ₴ ≈ $0.11** | **$2.29** | ✅ [merkon.ua](https://merkon.ua/magnit-neodymovyy-pryamokutnyk-10x5x5-mm/) |
| 11 | **608ZZ bearing (wheel axles)** | 4 | ~$1.50 *(est.)* | **$6** | ✅ [Rozetka SKF 608-ZZ](https://rozetka.com.ua/ua/220554211/p220554211/) |
| 12 | **TPU 3D-printed tyres + PETG hubs** | 4 | own printer | **$0** | — |
| 13 | **Aluminium plate 3 mm, cut to size** | 1 set | ~$18 *(est.)* | **$18** | ✅ supplier [metallbudalyans.com.ua 6061-T6](https://metallbudalyans.com.ua/ua/catalog/List-alyuminievyy-6061-T6-AD31) |
| 14 | **PCBWay-style laser cutting (batched)** | 1 | **700 ₴ min ≈ $15.67** | **$15.67** | ✅ [lasernyvky.com/pricing](https://lasernyvky.com/pricing) |
| 15 | **Fasteners / standoffs / wire / connectors** | kit | ~$12 *(est.)* | **$12** | ✅ [arduino.ua стійки](https://arduino.ua/cat273-mejplatnie-stoiki) |
| 16 | **Shipping (AliExpress + local Nova Poshta)** | — | ~$15 *(est.)* | **$15** | — |
| | | | **PROTOTYPE TOTAL** | **≈ $173** | ✅ **inside your $150–200 band** |

### 3.2 (b) Competitive ~1 kg / midi-sumo robot — target ≈ $500

| Line | Item | Qty | Unit | Ext. | Source |
|---|---|---|---|---|---|
| 1 | **Pololu 70:1 Metal Gearmotor 37Dx54L mm 12V (#4744)** — 27 kg·cm | 2 | **$38.95** | **$77.90** | ✅ [pololu.com/product/4744](https://www.pololu.com/product/4744) |
| 2 | **BTS7960 43 A driver module** | 2 | **186.60 ₴ ≈ $4.18** | **$8.35** | ✅ [prom.ua](https://prom.ua/ua/p2174139322-shagovyj-drajver-dvigatelya.html) |
| 3 | **Pololu Universal Alu Hub for 6 mm shaft, M3 (2-pack) (#1999)** | 1 | ~$10 *(est.)* | **$10** | ✅ [pololu.com/product/1999](https://www.pololu.com/product/1999) |
| 4 | **Pololu Machined Alu Bracket for 37D (#1995)** | 2 | ~$8 *(est.)* | **$16** | ✅ [pololu.com/product/1995](https://www.pololu.com/product/1995) |
| 5 | **Arduino Nano v3.0 (clone)** | 2 | **244 ₴ ≈ $5.46** | **$10.92** | 🔎 [prom.ua](https://prom.ua/ua/p2279577218-plata-arduino-nano.html) |
| 6 | **QTR-8RC 8-ch reflectance array** (or genuine Pololu #961) | 1 | ~$4 clone / ~$15 genuine *(est.)* | **$15** | ✅ [pololu.com/product/961](https://www.pololu.com/product/961/resources) |
| 7 | **JSumo JS40F / JS60F IR opponent sensors** | 3 | ~$10 *(est.)* | **$30** | ✅ [jsumo.com/js40f](https://www.jsumo.com/js40f-digital-distance-sensor-min-40-cm-range) |
| 8 | **MPU-6050 (genuine InvenSense)** | 1 | ~$6 *(est.)* | **$6** | ✅ [arduino.ua/prod6511](https://arduino.ua/prod6511-akselerometr-ta-giroskop-invensense-mpu-6050-original) |
| 9 | **ACS712 30 A current sensor** | 1 | ~$4 *(est.)* | **$4** | ✅ [arduino.ua/prod618](https://arduino.ua/prod618-datchik-toka-acs712-30a-gy-712) |
| 10 | **JSumo Microstart start module + remote** | 1 | ~$25 *(est.)* | **$25** | ✅ [jsumo.com/robot-start-module](https://www.jsumo.com/robot-start-module) |
| 11 | **3S LiPo 2200 mAh 40C (Fullymax class)** | 2 | ~$22 *(est.)* | **$44** | ✅ [Rozetka](https://rozetka.com.ua/ua/152432386/p152432386/) |
| 12 | **LiPo balance charger** | 1 | ~$28 *(est.)* | **$28** | ✅ [arduino.ua](https://arduino.ua/cat80-zaryadnie-ustroistva) |
| 13 | **Countersunk N38 Ø20×5 magnets (6 kg each)** | 10 | ~$0.80 *(est., MERKON countersunk line)* | **$8** | ✅ [merkon.ua/dysky-z-otvorom](https://merkon.ua/dysky-z-otvorom/) |
| 14 | **MERKON 10×5×5 blocks (tuning + spares)** | 40 | **5.11 ₴ ≈ $0.11** | **$4.58** | ✅ [merkon.ua](https://merkon.ua/magnit-neodymovyy-pryamokutnyk-10x5x5-mm/) |
| 15 | **JSumo SLT20 silicone wheel set (33×20 mm pair)** | 2 | ~$19.50 *(est.)* | **$39** | ✅ [jsumo.com/slt20](https://www.jsumo.com/slt20-aluminum-silicone-wheel-set-33mmx20mm-pair) |
| 16 | **Replacement silicone tyres (spares)** | 2 pr | ~$6 *(est.)* | **$12** | ✅ [jsumo.com/replacement-silicone-tyres](https://www.jsumo.com/replacement-silicone-tyres) |
| 17 | **608ZZ / 625ZZ bearings + shafts** | kit | ~$12 *(est.)* | **$12** | ✅ [Rozetka 608-ZZ](https://rozetka.com.ua/ua/220554211/p220554211/) |
| 18 | **Carbon 2 mm plate 200×300 (top deck)** | 1 | ~$34 *(est.)* | **$34** | ✅ [hobbymania.com.ua/p-5987](https://hobbymania.com.ua/p-5987-plastyna-karbonova-2mm-x-200mm-x-300mm) |
| 19 | **Aluminium 6061-T6 3 mm belly plate + laser cut** | 1 set | **$15.67 min order** + material ~$18 | **$33.67** | ✅ [lasernyvky.com/pricing](https://lasernyvky.com/pricing) · [supplier](https://metallbudalyans.com.ua/ua/catalog/List-alyuminievyy-6061-T6-AD31) |
| 20 | **Titanium / spring-steel blade** | 1 | ~$20 *(est.)* | **$20** | ✅ ref [flagma.ua Ti sheet](https://flagma.ua/uk/list-titanovy-4mm-8mm-10mm-vt-1-0-o3111463.html) |
| 21 | **MG996R blade servo** | 1 | **$10.95** | **$10.95** | ✅ [jsumo.com/mg996r](https://www.jsumo.com/mg996r-servo-motor-digital) |
| 22 | **Fasteners, standoffs, wire, connectors, JST** | kit | ~$18 *(est.)* | **$18** | ✅ [JSumo screws](https://www.jsumo.com/screws-nuts-washers) |
| 23 | **Shipping** (Pololu international ~$25 + JSumo $9.95 + AliExpress ~$12 + local ~$6) | — | ~$53 *(est.)* | **$53** | — |
| | | | **COMPETITIVE 1 kg TOTAL** | **≈ $501** | ✅ **lands on your $500 target** |

### 3.3 (b′) Competitive ~3 kg / mega-sumo robot — target ≈ $500

Same as 3.2 but with the 3 kg-class changes:

| Change vs §3.2 | Item | Qty | Unit | Ext. |
|---|---|---|---|---|
| Motor upgrade | **JSumo Proton DC Gear Motor 12 V 500 RPM (37 mm, 6 mm shaft)** | 2 | **$29.00** | **$58.00** |
| Or premium | *PREORDER* **Symtec Q Gearmotor (44 kg·cm)** | 2 | **$94.50** | **$189.00** |
| Driver upgrade | **Cytron MDD10A (10 A cont. × 2)** — price unconfirmed, est. | 1 | ~$25 *(est.)* | **$25** |
| Stronger wheels | **JSumo SLT20P Steel Silicone Wheel Set** | 2 | ~$25 *(est.)* | **$50** |
| 4S power | **4S LiPo ~3000 mAh 45C+** | 2 | ~$35 *(est.)* | **$70** |
| Much more magnet | **Countersunk N38 Ø20×5** | 20 | ~$0.80 | **$16** |
| Thicker belly plate | **Aluminium 6061-T6 5 mm** + laser | 1 | ~$40 | **$40** |
| Bigger charger | **Dual-channel 50 W+ charger** | 1 | ~$55 *(est.)* | **$55** |
| Everything else (sensors, MCU, fasteners, shipping) as §3.2 | — | — | — | **≈ $230** |
| | | | **COMPETITIVE 3 kg TOTAL (Proton route)** | **≈ $544** |
| | | | **COMPETITIVE 3 kg TOTAL (Symtec route)** | **≈ $675** |

**Key finding: a genuinely competitive 3 kg magnetic sumo bot does not fit in $500** once you add a 4S pack, steel-hub wheels and 20+ countersunk magnets. **The 1 kg / midi class is where $500 buys a winner.** The BB1 Midi Sumo kit (below) is literally JSumo's answer to this class.

### 3.4 (c) What the money above $500 buys

In priority order (best value first):

| Spend | What you get | Why it matters |
|---|---|---|
| **+$50** | **4 spare silicone tyre sets + 2 spare motors' worth of brushes/shafts** | Tyres and motors are what actually break |
| **+$80** | **Second complete drivetrain** (2 × Pololu 37D + 2 × BTS7960) | A mid-match motor failure otherwise ends your tournament |
| **+$120** | **2 more 3S LiPo packs + a 2nd charger** | Back-to-back matches; charging is the schedule bottleneck |
| **+$150** | **Swap BTS7960 → Cytron MDD10A / Pololu Dual G2** | Real continuous current rating, thermal protection, no magic smoke |
| **+$200** | **Symtec Q gearmotors (44 kg·cm)** | The single biggest performance jump available; pushes a 3 kg opponent |
| **+$250** | **A complete second robot (spare)** | See §5 |
| **+$400** | **CNC-machined (not laser-cut) 7075 aluminium chassis + precision magnet pockets** | Flatness and stiffness → consistent magnet gap → repeatable traction |
| **+$600** | **Full CNC chassis + titanium blade + a strain-gauge/load-cell test rig** | Lets you *measure* downforce and optimize magnets instead of guessing |

---

## 4. 🧰 Comparison of complete "starter kit" options

| | **KIT A — JSumo M1 Mini Sumo Kit** | **KIT B — Pololu-based DIY (this report's §3.2)** | **KIT C — AliExpress budget (this report's §3.1)** |
|---|---|---|---|
| **Exact product** | **M1 Mini Sumo Robot Kit (Unassembled)**, product code **JS15540** | Custom BOM | Custom BOM |
| **Price** | **$245.00** ✅ | **≈ $501** | **≈ $173** |
| **Source** | ✅ [jsumo.com/m1-arduino-mini-sumo-robot-kit-unassembled](https://www.jsumo.com/m1-arduino-mini-sumo-robot-kit-unassembled) | see §3.2 | see §3.1 |
| **What's included** | **M1 laser-cut stainless steel body (2 plates)**; **Genesis Arduino Nano mainboard**; **QTR1A line sensors ×2**; **MR45 opponent sensors ×3**; **Core 6 V 400 RPM DC gear motors ×2**; 20 mm M/F standoffs ×5; 8 mm M/F standoffs ×4; **Mini Katana blade**; Mini USB cable; motor brackets ×2; **LiPo battery 2S 7.4 V**; JST battery cable; **SLT20 silicone wheel pair**; M3×20 ×6; M3×8 ×10; M3×8 countersunk ×4; M3 nut ×10; M2×15 ×4; M2 nut ×4; crimp pins ×9; 3 mm heat-shrink ×9; double-sided tape; tie wraps ×2 | Nothing pre-packaged — you specify every part | Nothing pre-packaged |
| **Size / weight** | **10 × 10 × 10 cm, height 5 cm, weight 0.35 kg** | Your design | Your design |
| **Not included** | Dohyo, **LiPo charger**, Microstart module (optional) | Everything must be sourced | Everything must be sourced |
| **Class fit** | 500 g mini-sumo (and legal for 1 kg) | **1 kg / midi-sumo** | 500 g–1 kg prototype |
| **Magnetic-arena capable?** | ⚠️ **No, not as shipped.** It ships **6 V 400 RPM core motors** and a **2S pack** — nowhere near enough torque for a magnetic dohyo, and **no magnets at all** | ✅ **Yes** — 27 kg·cm motors, 6 kg magnets, tunable | ⚠️ Marginal — needs a motor upgrade |
| **Upgradable to a magnetic-arena winner?** | ✅ **Partially.** The steel chassis, blade, sensors and silicone wheels are all keeper parts. But you would be replacing **motors + battery + driver** (≈ +$90), which erases the kit's value. **Better: buy the JSumo parts à la carte and pair them with Pololu 37D motors** | ✅ **Yes, by construction** | ✅ **Yes** — upgrade the motors |
| **Shipping to UA** | ✅ **$9.95 registered air mail; free over $199** — so this kit ships **free** | Pololu (US) ~$25 + JSumo $9.95 + AliExpress ~$12 | AliExpress ~$12 (2–6 weeks) |
| **Verdict** | **Best "get running in a weekend" option, but you will outgrow the drivetrain in one event.** Buy it if the team needs a working reference platform *now*; don't buy it expecting to win | **Best overall.** Highest performance per dollar at the $500 mark | **Best for learning the magnetic physics cheaply** |

### Other complete kits worth knowing (all ✅ confirmed prices)

| Kit | Price | Class | Source | Note |
|---|---|---|---|---|
| **BB1 Midi Sumo Robot Kit (15×15 cm, Assembled)** | **$570.00** | **1 kg / midi** | ✅ [jsumo.com/bb1-midi-sumo-robot-kit-assembled](https://www.jsumo.com/bb1-midi-sumo-robot-kit-assembled) | **The closest thing to a purpose-built 1 kg magnetic-class robot.** Uses the $23.50 JS19838 25 mm motors ×4. **$70 over budget, but it is assembled and proven** |
| **Shogun Mini Sumo Robot Kit (Full Kit, Not Assembled)** | **$290.00** | 500 g | ✅ [jsumo.com/shogun-mini-sumo-robot-kit-full-kit-not-assembled](https://www.jsumo.com/shogun-mini-sumo-robot-kit-full-kit-not-assembled) | |
| **Shogun Mini Sumo Robot Kit (Full Kit, Assembled)** | **$360.00** | 500 g | ✅ [jsumo.com/shogun-mini-sumo-robot-kit-full-kit-assembled](https://www.jsumo.com/shogun-mini-sumo-robot-kit-full-kit-assembled) | |
| **Flying Shogun Mini Sumo Robot Kit (Full Kit, Not Assembled)** | **$310.00** | 500 g | ✅ [jsumo.com/flying-shogun-mini-sumo-robot-kit-full-kit-not-assembled](https://www.jsumo.com/flying-shogun-mini-sumo-robot-kit-full-kit-not-assembled) | |
| **Black Magic Mini Sumo Robot Kit (Full Kit, Not Assembled)** | ❓ **unconfirmed** | 500 g | ✅ [jsumo.com/blackmagic-mini-sumo-robot-kit-full-kit](https://www.jsumo.com/blackmagic-mini-sumo-robot-kit-full-kit) | |
| **FROG Mini Sumo Robot Kit** (beginner) | **$69.00** (was $89.95, −23 %) | 500 g | ✅ [jsumo.com/frog-beginner-mini-sumo-robot-kit](https://www.jsumo.com/frog-beginner-mini-sumo-robot-kit) | **Cheapest complete sumo kit found.** Beginner-grade — great as a spare/loaner |
| **GZero Sumo Robot Mechanical Kit (No Electronics)** | ❓ **unconfirmed** | — | ✅ [jsumo.com/gzero-sumo-robot-mechanical-kit-no-electronics](https://www.jsumo.com/gzero-sumo-robot-mechanical-kit-no-electronics) | Rolling chassis only |
| **Titan Sumo Robot Kit 3 kg (20×20 cm, Assembled)** | ❓ **unconfirmed** | **3 kg** | ✅ [jsumo.com/titan-sumo-robot-kit-3kg-20x20cm-type-assembled](https://www.jsumo.com/titan-sumo-robot-kit-3kg-20x20cm-type-assembled) | |
| **Titan 4×4 Plexiglass Sumo Robot Kit (No Electronics)** | ❓ **unconfirmed** | 3 kg | ✅ [jsumo.com/titan-4x4-jsumo-sumo-robot](https://www.jsumo.com/titan-4x4-jsumo-sumo-robot) | |
| **OMEGA Sumo Robot Full Kit (Assembled)** | **$1,200.00** | 3 kg | ✅ [jsumo.com/omega-sumo-robot-full-kit-assembled](https://www.jsumo.com/omega-sumo-robot-full-kit-assembled) | Serious money |
| **Apocalypse Sumo Robot (4×4, Maxon motors, 3 kg)** | **$2,450.00** | 3 kg | ✅ [jsumo.com/apocalypse-sumo-robot-...](https://www.jsumo.com/apocalypse-sumo-robot-4x4-sumo-robot-with-maxon-motors-non-magnetic-type-3kg) | ⚠️ **Explicitly sold as "Non-Magnetic Type"** — even at $2,450 JSumo does not ship it magnet-ready |
| **XS1 Micro Sumo Robot Kit (Assembled)** | **$99.00** | 100 g | ✅ [jsumo.com/xs1-micro-sumo-robot-kit](https://www.jsumo.com/xs1-micro-sumo-robot-kit) | Cheap way to learn the sensor/start logic |
| **ATLAS All Terrain Explorer 4×4 (mechanical only)** | **$390.00** | — | ✅ [jsumo.com/atlas-4x4-robot-mechanical-kit](https://www.jsumo.com/atlas-4x4-robot-mechanical-kit) | Not sumo |
| **Pololu Zumo 32U4 OLED Robot** (assembled, 75:1 HP motors) | ❓ **unconfirmed** | ~500 g | ✅ [pololu.com/product/4992](https://www.pololu.com/product/4992/pictures) | **Not a sumo robot** (it's a small tracked rover) but its 75:1 HP micro metal gearmotors are a useful reference |
| **Arduline / Flash line-follower kits** | $55.00 / $49.50 | — | ✅ [jsumo.com/robot-kits](https://www.jsumo.com/robot-kits) | Not sumo |

---

## 5. 💸 Cost of a second, spare robot, and spare critical parts

### Spare parts (buy these first — highest failure probability)

| Spare | Qty | Unit | Ext. | Source |
|---|---|---|---|---|
| **Pololu 37D 70:1 gearmotor (#4744)** | 2 | **$38.95** | **$77.90** | ✅ [pololu.com/product/4744](https://www.pololu.com/product/4744) |
| **BTS7960 driver module** | 2 | **186.60 ₴ ≈ $4.18** | **$8.36** | ✅ [prom.ua](https://prom.ua/ua/p2174139322-shagovyj-drajver-dvigatelya.html) |
| **Arduino Nano clone** | 2 | **244 ₴ ≈ $5.46** | **$10.92** | 🔎 [prom.ua](https://prom.ua/ua/p2279577218-plata-arduino-nano.html) |
| **Silicone tyre sets** | 2 | ~$6 *(est.)* | **$12** | ✅ [jsumo.com/replacement-silicone-tyres](https://www.jsumo.com/replacement-silicone-tyres) |
| **Blade** | 2 | ~$10 *(est.)* | **$20** | ✅ [jsumo.com/blades-razors](https://www.jsumo.com/blades-razors) |
| **Neodymium magnets (they chip)** | 10 | **5.11 ₴ ≈ $0.11** | **$1.14** | ✅ [merkon.ua](https://merkon.ua/magnit-neodymovyy-pryamokutnyk-10x5x5-mm/) |
| **Bearings 608ZZ** | 4 | ~$1.50 *(est.)* | **$6** | ✅ [Rozetka SKF 608-ZZ](https://rozetka.com.ua/ua/220554211/p220554211/) |
| **3S LiPo** | 1 | ~$22 *(est.)* | **$22** | ✅ [Rozetka](https://rozetka.com.ua/ua/152432386/p152432386/) |
| **Spare fasteners/standoffs** | kit | ~$8 *(est.)* | **$8** | ✅ [JSumo](https://www.jsumo.com/screws-nuts-washers) |
| **SPARE PARTS TOTAL** | | | **≈ $166** | |

### Full second robot

| Scenario | Cost | Notes |
|---|---|---|
| **Clone of the §3.2 competitive 1 kg robot** | **≈ $450–501** | Saves only the shipping (batch orders) and the charger (~$28) and the laser minimum (batch plates) — call it **$440** |
| **Second robot as a "practice mule"** (budget motors, same magnets/sensors/chassis) | **≈ $210–250** | ✅ **Recommended.** One competition robot + one identical-geometry practice robot with cheap JGB37-520 motors lets you test tactic changes without risking the good motors |
| **Third robot, parts-bin build** | **≈ $120** | Reuse MCU, charger, batteries |
| **Cheapest legal full backup — JSumo FROG kit** | **$69.00** | ✅ [jsumo.com/frog-beginner-mini-sumo-robot-kit](https://www.jsumo.com/frog-beginner-mini-sumo-robot-kit) — a 500 g kit, not competitive, but guarantees you can field *a* robot |

**Budget recommendation for a ~$500 team budget:** spend **$340 on the competition 1 kg robot** (downgrade motors to JGB37-520 initially, upgrade later), **$110 on a practice mule**, **$50 on spares**. That is a more resilient plan than one $500 robot with no backup.

---

## 6. 🇺🇦 Local options — Ukrainian shops, UAH prices, availability

| Shop | URL | What they actually stock (confirmed) | Confirmed UAH prices | Availability | Import needed? |
|---|---|---|---|---|---|
| **arduino.ua** (Kyiv) | [arduino.ua](https://arduino.ua) | **Arduino Nano A000005 genuine**, Uno Rev3, **Pololu step-down/step-up/bidirectional regulators**, **Pololu G2 24v21 driver**, **BTS7960 module**, **KY-033 TCRT5000**, **TCRT5000 module**, **ACS712 30A**, **MPU-6050 (genuine InvenSense)**, **VL53L0X ToF**, **LM2596 buck**, **HC-SR04**, ZIPPY 3S LiPo, wheels, standoffs, breadboards, jumpers, SD module, LiPo chargers | **Nano A000005 1 316 ₴** (2+ 1 263 ₴, 3+ 1 211 ₴) ✅ · **Uno Rev3 1 448 ₴** ✅ · **LM2596 49 ₴** ✅ · **HC-SR04 49 ₴** ✅ · **Breadboard 69 ₴** ✅ · **Jumpers 65-pc 49 ₴** ✅ · **Jumpers 120-pc 129 ₴** ✅ · **SD module 26 ₴** ✅ | ✅ **In stock**, Nova Poshta, 6-month warranty (14 days on batteries) | ❌ No — **this is your primary local supplier** |
| **MERKON** (Kyiv) | [merkon.ua](https://merkon.ua) | **Neodymium discs, blocks, countersunk discs, rings, pot magnets, rubber-coated, hooks — full range N35/N38** | **Ø20×5 N38 6 kg: 36.00 ₴/1, 35.50 ₴/30, 35.00 ₴/100** ✅ · **10×5×5, 1.2 kg: 5.11 ₴/1, 4.90 ₴/20, 4.67 ₴/100** ✅ (+ 7 more confirmed block sizes) | ✅ **2 171 pcs Ø20×5 in stock; 30 765 pcs of 10×5×5** · min order 2 pcs · **1–2 working days** | ❌ No — **BEST magnet source in Ukraine** |
| **Supermagnit** (UA) | [supermagnit.net.ua](https://supermagnit.net.ua) | Neodymium discs Ø1–Ø20+, blocks, rings, squares, rods, cubes, pot magnets, high-temp (150 °C) magnets | **Ø20×5 N38 5.2 kg: 57.22 ₴/1, 48.92 ₴/50, 46.04 ₴/1000** ✅ · **Ø5×5 5.50 ₴** ✅ · **Ø5×10 10.70 ₴** ✅ · **Ø4×8 5.87 ₴** ✅ · **10×5×5 14.10 ₴** ✅ (⚠️ out of stock) | Mixed — 10×5×5 **out of stock**; disc range mostly available | ❌ No (backup to MERKON) |
| **Prom.ua** | [prom.ua](https://prom.ua) | **BTS7960 43 A driver**, Arduino Nano v3.0 Type-C, 3S LiPo category, **titanium sheet ВТ1-0 0.5 mm**, motor-reduktor category | **BTS7960 43 A: 186.60 ₴** ✅ · **Nano v3.0 Type-C 244 ₴** ✅ · **Nano v3.0 (2nd seller) 525 ₴** ✅ · **Ti sheet 0.5 mm ВТ1-0: 1 500 ₴** 🔎 | ✅ Marketplace — check individual seller ratings | ❌ No |
| **Rozetka** | [rozetka.com.ua](https://rozetka.com.ua) | BTS7960 43 A driver, Arduino Nano v3.0 CH340, **SKF 608-ZZ bearing**, ZKL 608ZZ, Fullymax 3S 2200 mAh LiPo | ❓ **prices unconfirmed** (Rozetka's price block does not render in fetched HTML). Product pages confirmed to exist | ✅ Large marketplace, broad stock | ❌ No |
| **Bigl.ua** | [bigl.ua](https://bigl.ua) | Arduino Nano V3.0 CH340, 20×10×5 N42 magnet with hole | **Nano V3.0: 387.60 ₴** 🔎 · **magnet 20×10×5: 128 ₴** 🔎 | ✅ | ❌ No |
| **Хобі Манія (Hobby Mania)** | [hobbymania.com.ua](https://hobbymania.com.ua) | **Carbon fibre plate 3K twill 2 mm × 200 × 300 mm**, RC models, batteries | ❓ **unconfirmed** (page loaded, price block not captured) | ✅ RC hobby shop | ❌ No |
| **МеталБудАльянс** (Kyiv) | [metallbudalyans.com.ua](https://metallbudalyans.com.ua) | **Aluminium sheet 6061-T6 / AD31, 5.0 × 1500 × 3000 mm**, full aluminium catalogue | ❓ **unconfirmed** (data loads client-side) | ✅ Kyiv warehouse | ❌ No |
| **Epicentr** | [epicentrk.ua](https://epicentrk.ua) | **N42 rectangular magnet 20×10×5 with hole (MG-432)**, "3 kg" | ❓ **unconfirmed** | ✅ National retail chain — walk-in | ❌ No |
| **Onesapan** | [onesapan.com](https://onesapan.com) | **N35 Ø20×5 countersunk disc, 5 mm hole** | ❓ **unconfirmed** | ✅ | ❌ No |
| **Onyx-Magnet** | [onyx-magnet.com](https://onyx-magnet.com) | **Countersunk ring magnet Ø20×5, hole 4.5/7.5 mm** | ❓ **unconfirmed** | ✅ | ❌ No |
| **modelistam.com.ua** | [modelistam.com.ua](https://modelistam.com.ua) | **3S 11.1 V LiPo batteries** (RC/hobby) | ❓ **unconfirmed** | ✅ | ❌ No |
| **rcscomponents.kiev.ua** | [rcscomponents.kiev.ua](https://www.rcscomponents.kiev.ua) | **Distributor of POLOLU (1 587–1 746 SKUs)**, incl. 5 V regulators, 30T track set | ❓ **unconfirmed** — ⚠️ **listed lead time "21–31 days"** | ⚠️ Long lead time | ❌ No, but slow |
| **vselandia.com** | [vselandia.com](https://vselandia.com) | "мотор редуктор" tag results, ATmega328P | ❓ **unconfirmed** | ✅ | ❌ No |
| **krons.com.ua / kosmodrom.ua** | [krons](https://krons.com.ua) · [kosmodrom](https://www.kosmodrom.ua) | BTS7960 43 A driver | ❓ **unconfirmed** | ✅ | ❌ No |
| **Robofinist marketplace** | [robofinist.org](https://robofinist.org) | ⚠️ **Not investigated in this session — unconfirmed** | ❓ | — | ⚠️ **Gap** |
| **robostore.com.ua** | [robostore.com.ua](https://robostore.com.ua) | ⚠️ **No confirmed stock found** | ❓ | — | ⚠️ **Gap** |
| **3dprint.com.ua** | [3dprint.com.ua](https://3dprint.com.ua) | ⚠️ **No confirmed stock found** | ❓ | — | ⚠️ **Gap** |
| **Laser Nyvky** (Kyiv) | [lasernyvky.com](https://lasernyvky.com) | **Laser cutting price list dated 06.02.2025** — ✅ fully confirmed (see §2.6) | ✅ **Aluminium 2 mm 35 ₴/m; 1.5 mm 27 ₴/m; 1 mm 22 ₴/m; steel 2 mm 13 ₴/m. Min order 700 ₴. Pierce = 10 % of 1 m price** | ✅ | ❌ No |
| **Арт-Металл** (Kyiv) | [art-metall.kyiv.ua](https://art-metall.kyiv.ua) | **Laser cutting 2026 price list** + CNC bending, powder coat, tapping, countersinking | ✅ **Aluminium 2 mm 38 ₴/m; 1 mm 25 ₴/m; steel 2 mm 22 ₴/m; stainless 2 mm 32 ₴/m. Urgent +25–50 %** | ✅ Advertises 15-min quote turnaround | ❌ No |
| **UASTAL / Сторожук** (Kyiv) | [uastal.com](https://uastal.com/gidroabrazivnaya-rezka) | Waterjet cutting | ❓ **unconfirmed** | ✅ | ❌ No |
| **Завод Термо-Пак** (Kyiv) | [tp-eu.com](https://tp-eu.com/en/services/gidroabrazivnaya-porezka/) | Waterjet cutting | ❓ **unconfirmed** | ✅ | ❌ No |
| **GRAFIX** (Kyiv) | [grafix.in.ua](https://grafix.in.ua/lazerne-rizannya-kyiv/) | Laser cutting | ❓ **unconfirmed** (JS-rendered site) | ✅ | ❌ No |

### What is NOT available locally (must import)

| Category | Status in Ukraine | Best alternative |
|---|---|---|
| **Pololu 37D metal gearmotors** | ⚠️ **Not confirmed at any Ukrainian retailer.** rcscomponents.kiev.ua is a Pololu distributor but with a 21–31 day lead time | **Buy from Pololu direct** (ships worldwide) or an **EU distributor** — *Botland PL, Kamami PL, TME PL all list Pololu 37D / #4758* (✅ [kamami.pl listing](https://kamami.pl/silniki-37d-mechanika/577682-101-12v-37dx65l-silnik-z-metalowa-przekladnia-i-enkoderem-64-cpr-pololu-4758-5906623479917.html), ✅ [TME POLOLU-1090](https://www.tme.eu/lt/en/details/pololu-1090/accessories-for-robotics-and-rc/pololu/pololu-wheel-42x19mm-pair/)) — **PL shops are the cheapest route to Kyiv** |
| **N42–N52 grade magnets** | ⚠️ **Ukrainian shops sell N35/N38 only** | **AliExpress** (N52 blocks/discs, cheapest bulk) or **supermagnete.de** (EU, full N35–N52 range) or **JSumo** (N52 blocks) or **KJ/JC Magnetics** (US, epoxy-coated N52) |
| **QTR-8A / QTR-8RC / QTRX arrays** | ⚠️ **Not confirmed locally.** Only TCRT5000/KY-033 singles are confirmed | **Pololu direct**, an **EU distributor**, or an **AliExpress QTR-8RC clone** (HYS301) |
| **Cytron MDD10A** | ⚠️ **Not found locally** | **Cytron** (Malaysia) direct, or AliExpress |
| **Purpose-built silicone sumo wheels in 30–60 mm** | ⚠️ **Not confirmed locally** | **JSumo SLT20 / SLT20P** (Turkey, $9.95 air mail) — or **3D-print a TPU tyre** onto a printed hub (free) |
| **Maxon RE25/RE35 + gearhead (new)** | ❌ **Not available at any sane price** | **Used/surplus Maxon** (eBay, Polish industrial surplus) or JSumo's Maxon-based robots (from $2,450) |
| **TI-grade titanium in thin sheet (1.0–1.5 mm)** | ⚠️ Only 0.5 mm (too thin) and 4–10 mm (too thick) confirmed | **Ask a Kyiv metal yard for 1.0–1.5 mm ВТ1-0 / Grade 2.** Or substitute **hardened spring steel 65Г / 60S2A at 1.5–2 mm** — cheaper, harder, available |
| **Miniature bearings 625ZZ / 688ZZ / 623ZZ** | ⚠️ Only **608ZZ** confirmed locally | **AliExpress bearing assortment kits** |
| **LiPo balance chargers** | ⚠️ Category exists at arduino.ua; **no price confirmed** | **arduino.ua** or **modelistam.com.ua**; AliExpress (IMAX B6 clones) as backup |
| **Smart batteries / high-C 4S packs** | ⚠️ Unconfirmed | **modelistam.com.ua**, **hobbymania.com.ua** (RC shops), AliExpress |

---

## 7. 🎯 Recommendations

### For the ~1 kg robot (the class where $500 actually wins)

1. **Motors:** Pololu **#4744 (70:1, 27 kg·cm)** ×2 = **$77.90** ✅. This is the single most important purchase.
2. **Drivers:** BTS7960 ×2 from **prom.ua at 186.60 ₴** ✅ — locally available, no customs, negligible cost.
3. **MCU:** Arduino Nano v3.0 clone at **244 ₴** ✅ from prom.ua. Buy **3** for spares.
4. **Edge sensing:** a **QTR-8RC** array (import) **plus** 5 × TCRT5000 modules (local) as a redundant front row. **Redundancy in edge detection is how you avoid losing to a ring-out.**
5. **Opponent sensing:** 3 × JSumo IR opponent sensors with background suppression — this is what separates a winner from a line-follower.
6. **Magnets:** **10 × Ø20×5 countersunk N38 from MERKON** (~$8) bolted through a **3–5 mm 6061-T6 aluminium belly plate**, plus **40 × 10×5×5 blocks** ($4.58) in printed pockets for tuning. Target **20–30 kg** real downforce at a 1 mm gap.
7. **Chassis:** laser-cut **6061-T6 aluminium** at **Art-Metall or Laser Nyvky**. Batch all robots into one order to absorb the **700 ₴ minimum**.
8. **Wheels:** start with **3D-printed TPU tyres** (free, tunable); buy **JSumo SLT20** silicone wheels once you know your diameter.
9. **Start module:** buy the **Microstart**. Most rules require a 5-second delay, and a legal start is free points.

### For the 3 kg robot

**Tell the team plainly: $500 is not enough for a competitive 3 kg magnetic sumo bot.** The realistic floor is **≈ $540 (budget route) to ≈ $675 (Symtec route)**, and the JSumo BB1 1 kg kit at **$570** is better value than any $500 3 kg attempt. If you must do 3 kg, budget **$700–900** and expect to need 20+ magnets, a 4S pack, a 5 mm plate, and steel-hub wheels.

### Hard rules for this project

- ✅ **Confirm magnet legality with the organiser first.**
- ✅ **Batch every import into ONE AliExpress order and ONE Pololu/EU order.** Shipping is the second-largest line item after motors.
- ✅ **Buy the magnets, drivers, Arduino and LiPo in Ukraine.** They are competitive or cheaper than importing once you count shipping and time.
- ✅ **Import the motors, the QTR array and the silicone wheels.** That is where the local market genuinely fails you.
- ✅ **Never trust the "43 A" rating on a BTS7960.** Derate to ~10 A continuous, add a heatsink, and keep a spare module in the pit box.

---

## 8. Methodology, integrity and open gaps

**Integrity statement.** Every price in this report is either (a) read directly off the vendor's own page in this session (marked ✅) or (b) quoted from a search-result title/link text (marked 🔎). No price, part number, specification or product name has been invented. Items I could not confirm are explicitly marked **❓ unconfirmed**. Estimated lines used only for BOM totals are labelled ***(est.)*** and are derived from the nearest confirmed comparable — they are planning placeholders, **not quotes**.

**Cross-checking done:** Pololu #4744 appears at $38.95 on its own product page and its #4744 gearmotor is listed in the 37D family table at the same ratio/torque; JSumo's M1 kit contents, weight (0.35 kg), dimensions (10×10×5 cm) and shipping terms ($9.95 / free over $199) all come from the same product page; MERKON's Ø20×5 magnet is confirmed at N38, 12.6 g, 2 171 in stock, 1–2 days.

**Known open gaps (do a second pass on these):**

1. **Ukrainian geared-motor prices** — the biggest gap. prom.ua/rozetka "мотор-редуктор 12V" category pages were not readable in this pass. **A confirmed UAH price for a 12 V 37 mm gearmotor would materially change the BOM** (it might beat importing).
2. **Pololu prices other than #4744** — I read #4744 only. All other Pololu lines are ❓.
3. **QTR-8A/8RC price** — Pololu page identified, price not captured.
4. **LiPo and charger prices in Ukraine** — categories confirmed at arduino.ua / Rozetka / modelistam, no prices read. My $22/$28 estimates are the weakest numbers in the two $500 BOMs.
5. **Aluminium sheet price per kg / per cut piece** and **waterjet price per metre** — both need a phone/email quote. The two laser shops will quote from a DXF.
6. **Botland / TME / Kamami shipping cost to Ukraine** — these are likely the cheapest source for genuine Pololu parts, but shipping terms were not confirmed.
7. **Robofinist marketplace, robostore.com.ua, 3dprint.com.ua** — named in the brief, not investigated successfully.
8. **Weight-class rules** — the RobotChallenge and Robotic Arena MegaSumo rule PDFs returned HTTP 406 / unsupported content type. **Class limits and magnet-legality wording must be re-verified from the organiser's own rulebook.**
9. **Maxon RE25/RE35 new-unit pricing** — not obtainable; only a used-unit figure ($20) from a 2017 capstone report.

---

## 9. Source index

**Vendors (confirmed prices)**
- Pololu 37D 70:1 #4744 — https://www.pololu.com/product/4744 ✅
- Pololu 37D family / full spec table — https://www.pololu.com/category/116/37d-metal-gearmotors ✅
- Pololu 12 V 37D subcategory — https://www.pololu.com/category/271/12v-37d-metal-gearmotors ✅
- Pololu 37D datasheet — https://a.pololu-files.com/file/0J1706/pololu-37d-metal-gearmotors.pdf
- JSumo 25 mm 12 V 750 RPM SP motor (JS19838, $23.50) — https://www.jsumo.com/12v-25mm-dc-gear-motor-750-rpm ✅
- JSumo DC gear motor category — https://www.jsumo.com/dc-gear-motors ✅
- JSumo motors category — https://www.jsumo.com/motors ✅
- JSumo robot kits (all kit prices) — https://www.jsumo.com/robot-kits ✅
- JSumo M1 Mini Sumo Kit (JS15540, $245, full BOM list, shipping terms) — https://www.jsumo.com/m1-arduino-mini-sumo-robot-kit-unassembled ✅
- JSumo mini-sumo parts recipe — https://www.jsumo.com/mini-sumo-robot-parts-list ✅
- MERKON Ø20×5 N38 disc magnet (36.00 ₴) — https://merkon.ua/magnit-neodymovyy-dysk-20x46-mm/ ✅
- MERKON rectangular magnets catalogue — https://merkon.ua/magnity-pryamokutnyky/ ✅
- MERKON countersunk discs — https://merkon.ua/dysky-z-otvorom/ ✅
- Supermagnit Ø20×5 (57.22 ₴) — https://supermagnit.net.ua/uk/magnity-diski/m-disk-20x5 ✅
- Supermagnit disc catalogue — https://supermagnit.net.ua/uk/magnity-diski ✅
- Supermagnit 10×5×5 (out of stock) — https://supermagnit.net.ua/uk/shop/pramougolnik/pramougolnik-10x5x5 ✅
- Prom.ua BTS7960 43 A (186.60 ₴) — https://prom.ua/ua/p2174139322-shagovyj-drajver-dvigatelya.html ✅ (🔎 price)
- Prom.ua Arduino Nano v3.0 Type-C (244 ₴) — https://prom.ua/ua/p2279577218-plata-arduino-nano.html 🔎
- arduino.ua Arduino Nano A000005 (1 316 ₴, tiered) — https://arduino.ua/prod179-arduino-nano-a000005 ✅
- arduino.ua LM2596 buck (49 ₴) — https://arduino.ua/prod650-dc-dc-ponijyuchii-konverter-lm2596-z-4-5-40v-do-3-35v ✅
- arduino.ua HC-SR04 (49 ₴) — https://arduino.ua/prod182-yltrazvykovoi-datchik-rasstoyaniya-hc-sr04 ✅
- arduino.ua BTS7960 module — https://arduino.ua/prod5016-kontroller-shagovogo-dvigatelya-bts7960-modul ✅
- arduino.ua TCRT5000 KY-033 — https://arduino.ua/prod2557-datchik-linii-ky-033-na-tcrt5000 ✅
- arduino.ua ACS712 30 A — https://arduino.ua/prod618-datchik-toka-acs712-30a-gy-712 ✅
- arduino.ua MPU-6050 (genuine) — https://arduino.ua/prod6511-akselerometr-ta-giroskop-invensense-mpu-6050-original ✅
- arduino.ua VL53L0X ToF — https://arduino.ua/prod3932-lazernii-datchik-rasstoyaniya-vl53l0x-v2-940nm ✅
- arduino.ua Pololu G2 24v21 driver — https://arduino.ua/prod2741-moshhnii-draiver-kollektornogo-dvigatelya-g2-24v-21a-24v21-ot-pololu ✅
- arduino.ua Pololu step-down regulators — https://arduino.ua/cat420-peretvoruvachi-ponijyuchi-pololu ✅
- arduino.ua ZIPPY 1800 mAh 3S 40C — https://arduino.ua/prod696-akkymylyator-zippy-compact-1800mah-3s-40c-lipo-pack ✅
- arduino.ua wheels category — https://arduino.ua/cat280-kolesa ✅
- arduino.ua standoffs — https://arduino.ua/cat273-mejplatnie-stoiki ✅
- Rozetka BTS7960 43 A — https://rozetka.com.ua/ua/386601609/p386601609/ ✅ page / ❓ price
- Rozetka Fullymax 3S 2200 mAh 40C — https://rozetka.com.ua/ua/152432386/p152432386/ ✅ page / ❓ price
- Rozetka SKF 608-ZZ — https://rozetka.com.ua/ua/220554211/p220554211/ ✅ page / ❓ price
- Rozetka ZKL 608ZZ — https://rozetka.com.ua/ua/401100750/p401100750/ ✅ page / ❓ price
- Bigl.ua Arduino Nano (387.60 ₴) — https://bigl.ua/ua/p544208253-arduino-nano-v30 🔎
- Bigl.ua magnet 20×10×5 (128 ₴) — https://bigl.ua/ua/p2114790476-neodimovyj-magnit-20x10x5mm 🔎
- Hobby Mania carbon 2 mm 200×300 — https://hobbymania.com.ua/p-5987-plastyna-karbonova-2mm-x-200mm-x-300mm ✅ page / ❓ price
- МеталБудАльянс aluminium 6061-T6 — https://metallbudalyans.com.ua/ua/catalog/List-alyuminievyy-6061-T6-AD31 ✅ page / ❓ price
- modelistam.com.ua 3S LiPo — https://modelistam.com.ua/ua/akkumulyatory/akkumulyatory-111-lipo-c-128/ ✅
- rcscomponents.kiev.ua (Pololu distributor, 21–31 day lead) — https://www.rcscomponents.kiev.ua/pololu/page=18 ✅
- Epicentr N42 20×10×5 magnet — https://epicentrk.ua/ua/shop/mplc-magnit-neodimovij-sila-n42-pramokutnij-z-otvorom-3-kg-20h10h5-mm-mg-432-1efa0c18-2727-6f56-963a-b1e9b0013337.html ✅ page / ❓ price
- Onesapan N35 Ø20×5 countersunk — https://onesapan.com/potuzhniy-neodimoviy-magnit-ndfeb-n35-krugliy-20h5-mm-shayba-disk-z-otvorom-5-mm-pid-kriplennya-z-potayem/reviews/ ✅ page / ❓ price
- Onyx-Magnet countersunk ring Ø20×5 — https://onyx-magnet.com/ua/neodimovye-magnity/magnity-s-zenkovkoy/neodimovyy-magnit-kolco-20x5mm-s-zenkovkoy-4575mm ✅ page / ❓ price
- Cytron MDD10A — https://www.cytron.io/th-warehouse/p-10amp-5v-30v-dc-motor-driver-2-channels ✅ page / ❓ price
- Cytron SmartDrive Duo — https://www.cytron.io/c-dc-motor/c-motor-driver/p-10amp-7v-35v-smartdrive-dc-motor-driver-2-channels ✅ page / ❓ price
- JSumo SLT20 silicone wheel set — https://www.jsumo.com/slt20-aluminum-silicone-wheel-set-33mmx20mm-pair ✅ page / ❓ price
- JSumo SLT20P steel silicone wheel set — https://www.jsumo.com/slt20p-steel-silicone-wheel-set-33mm-x-20mm-pair ✅ page / ❓ price
- JSumo JS7444 74 mm silicone wheels — https://www.jsumo.com/js7444-aluminum-silicone-wheel-pair-74mm-diameter ✅ page / ❓ price
- JSumo replacement silicone tyres — https://www.jsumo.com/replacement-silicone-tyres ✅
- JSumo MG996R ($10.95) — https://www.jsumo.com/mg996r-servo-motor-digital ✅
- JSumo N52 block magnet 10×5×20 — https://www.jsumo.com/neodymium-magnet-block-strong-n52-10mm-x-5mm-x-20-mm ✅ page / ❓ price
- JSumo JS40F IR sensor — https://www.jsumo.com/js40f-digital-distance-sensor-min-40-cm-range ✅ page / ❓ price
- JSumo QTR-8RC — https://www.jsumo.com/qtr-8rc-line-sensor-rc-time-digital ✅ page / ❓ price
- JSumo blades & razors — https://www.jsumo.com/blades-razors ✅
- JSumo bearings — https://www.jsumo.com/bearings ✅
- JSumo standoffs & spacers — https://www.jsumo.com/standoffs-spacers ✅
- JSumo shaft couplers — https://www.jsumo.com/shaft-couplers ✅
- JSumo screws/nuts/washers — https://www.jsumo.com/screws-nuts-washers ✅
- JSumo robot start module — https://www.jsumo.com/robot-start-module ✅
- Pololu QTR-8A (#960) — https://www.pololu.com/product/960 ✅ page / ❓ price
- Pololu QTR-8RC (#961) — https://www.pololu.com/product/961/resources ✅ page / ❓ price
- Pololu G2 24v13 (#2992) — https://www.pololu.com/product/2992 ✅ page / ❓ price
- Pololu VNH5019 (#1451) — https://www.pololu.com/product/1451 ✅ page / ❓ price
- Pololu current sensors — https://www.pololu.com/category/118/current-sensors ✅
- Pololu brackets #1995 / #1084 / hubs #1083 / #1999 — https://www.pololu.com/product/1995 · https://www.pololu.com/product/1084 · https://www.pololu.com/product/1083 · https://www.pololu.com/product/1999 ✅ pages / ❓ prices
- Pololu hex wheel adapters #2686 / #2687 / scooter adapter #2674 — https://www.pololu.com/product/2686 · https://www.pololu.com/product/2687 · https://www.pololu.com/product/2674 ✅ pages / ❓ prices
- Kamami.pl Pololu 37D with encoder — https://kamami.pl/silniki-37d-mechanika/577682-101-12v-37dx65l-silnik-z-metalowa-przekladnia-i-enkoderem-64-cpr-pololu-4758-5906623479917.html ✅ page / ❓ price
- TME POLOLU-1090 wheel 42×19 — https://www.tme.eu/lt/en/details/pololu-1090/accessories-for-robotics-and-rc/pololu/pololu-wheel-42x19mm-pair/ ✅ page / ❓ price
- AliExpress 37GB520 motor price trackers — https://alitools.io/es/showcase/engranaje-en-miniatura-de-xd-37gb520-motor-de-engranaje-cc-de-baja-velocidad-alto-torque-direccion-ajustable-12v-24v-10w-32978707442 🔎 · https://imall.com/product/37-dc-gear-motor-10W-12-V24V-mini-geared-low-speed-high-torque-can-adjustable-reversible-electric-tools-37GB520/Home-Improvement-Electrical-Equipment-Supplies/aliexpress.com/32789673607/565-12783777/en 🔎
- AliExpress BTS7960 price trackers — https://alitools.io/ru/showcase/dvoynoy-bts7960-43a-h-most-moshtniy-moduly-drayvera-dvigatelya-diy-umniy-avtomobilyniy-diagnosticheskiy-tok-1005001543753471 🔎 · https://imall.com/product/High-power-motor-drive-module-BTS7960-43A-current-limiting-control-semiconductor-refrigeration/Electronic-Components-Supplies-Electronics-Stocks/aliexpress.ru/1005007028767652/1381-261731290/en 🔎
- JC Magnetics 20×5 mm N52 epoxy-coated — https://www.jc-magnetics.com/20x5mm-neodymium-magnets-n52-epoxy-coated ✅ page / ❓ price
- supermagnete.de catalogue entries — https://www.supermagnete.hu/ger/catalog.pdf · https://www.supermagnete.it/ger/catalog.pdf ✅ docs / ❓ prices

**Fabrication & materials**
- Laser Nyvky full price list (06.02.2025) — https://lasernyvky.com/pricing ✅
- Арт-Металл 2026 laser price list — https://art-metall.kyiv.ua/lazerna-rzka-metalu-kiv-2026-czna-vd-1250-grn-porzka-stal-ta-alyumnyu-na-chpk.html ✅
- UASTAL waterjet — https://uastal.com/gidroabrazivnaya-rezka ✅ page / ❓ price
- Завод Термо-Пак waterjet — https://tp-eu.com/en/services/gidroabrazivnaya-porezka/ ✅ page / ❓ price
- GRAFIX laser — https://grafix.in.ua/lazerne-rizannya-kyiv/ ✅ page / ❓ price
- Composites for Model carbon sheets — https://com-posit.com.ua/ru/carbon-products/sheets ✅
- Prom.ua titanium sheet 0.5 mm ВТ1-0 (1 500 ₴) — https://prom.ua/ua/p1438139833-list-titanovyj-vt1.html 🔎
- Flagma.ua titanium 4/8/10 mm ВТ1-0 — https://flagma.ua/uk/list-titanovy-4mm-8mm-10mm-vt-1-0-o3111463.html ✅ page / ❓ price

**Rules / standards**
- RobotChallenge Robo Sumo Rules (PDF) — http://www.robotchallenge.org.cn/doc/en/RC-Sumo.pdf ⚠️ HTTP 406
- Robotic Arena MegaSumo Rules (PDF) — https://roboticarena.pl/media/filer_public/ab/7b/ab7b7947-79d0-4a29-9eef-49da77f98fb8/en_megasumo.pdf ⚠️ unsupported content type
- MEB Robot Mini Sumo 2026 — https://robot.meb.gov.tr/categories/mini-sumo-2026
- Robot-sumo / Sumo bot overview — https://en.m.wikipedia.org/wiki/Sumo_bot
- RoboTerra 2025 РОБОСУМО rules (Ukraine) — https://perspektyva.ck.ua/arch/robotterra2025/sumod2025.pdf (mirrored locally in `robosumo/research/01_rules_ukraine.txt`)
- Magnetic system research for autonomous MegaSumo robots (IEEE) — https://ieeexplore.ieee.org/abstract/document/8765950
- MegaSumo magnetic-floor aluminium test sample study (IJMERR) — https://www.ijmerr.com/uploadfile/2021/0624/20210624100758933.pdf

**Exchange rate**
- NBU official rate 1 Oct 2026 = 44.6819 UAH/USD — https://ua.korrespondent.net/business/financial/4916220-nbu-nazvav-kursy-valuit-na-pershyi-den-zhovtnia ✅
- NBU official rates portal — https://bank.gov.ua/ua/markets/exchangerates ✅

---

*End of report. Every ✅ price above was read from the vendor page in this session on 2026-10-01; every 🔎 price came from a search-result title. Items marked ❓ were not confirmable and must be re-quoted before purchase.*
