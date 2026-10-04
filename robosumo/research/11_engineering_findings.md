# Magnetic-Arena Robot Sumo — Engineering Findings

**Prepared for:** student team, ~6-month runway, ~$500 USD budget, 3 kg (MegaSumo) and/or 1 kg class, **steel/coated-steel dohyo** (magnets legal).
**Goal:** win. This document is deliberately numeric. Every derived number is labelled **estimate** with the formula or reasoning shown. Every substantial claim carries a source URL.

> **Reading note on evidence quality.** Two independent peer-reviewed papers (Białystok University of Technology, Poland) report **measured** pull-off forces for neodymium magnet arrays on a steel plate using an MTS 858 materials-testing machine. Those are the strongest numbers available and are used as the calibration anchor throughout. Vendor "pull force" figures (JSumo, K&J) are single-magnet, zero-gap, idealised values and are **not** achievable in a real robot. Do not design to vendor numbers.

---

## 0. Executive summary — the ten decisions that actually matter

| # | Decision | Recommendation | Why (short) |
|---|---|---|---|
| 1 | **Magnet grade** | **N42 or N52**, rectangular blocks, magnetised through the *thin* axis | N52 gives ~11% more `Br` than N42; the gap, not the grade, dominates ([NovaSolver](https://novasolver.jp/en/tools/magnet-strength-neodymium-air-gap.html)) |
| 2 | **Air gap** | **0.3–0.5 mm** at the wedges/wheels, ≤1.0 mm elsewhere. Never >1.5 mm | Force falls ~3.5%/0.1 mm at 0.5 mm gap; **16% loss going 0.5→1.0 mm**, 28% going 0.5→2.0 mm (**estimate**, §1.4) |
| 3 | **Total magnet mass** | 3 kg class: **80–150 g of N52** ⇒ **~30–50 kgf** extra downforce. 1 kg class: **25–50 g** | Measured arrays give 5–15 N per gram of N52 (§1.3) |
| 4 | **Magnet placement** | Concentrate around **the two drive wheels and the front plough**; alternating polarity is *not* enough — use a **Halbach** layout | Measured: Halbach = **1.65× (0.1 mm) to 2.8× (1.0 mm)** the force of alternating polarity for the same magnets ([IJMERR 2020](https://ijmerr.com/uploadfile/2020/0417/20200417064856590.pdf)) |
| 5 | **Motors** | Budget: **Pololu 37D 24 V 50:1 or 100:1**. Money-no-object: Maxon DCX35L + custom 4–10:1. Middle: JSumo Symtec Q | At 50 kgf downforce you need **130–200 kg·cm total** at the wheels — far beyond any 37D; see §2.4 |
| 6 | **Wheels** | **50–60 mm dia, 15–20 mm wide, hard rubber or cast urethane (Shore A 60–80)**, aluminium hubs | Large dia reduces the torque needed (T = F·r) and gives speed at a low gear ratio (§3) |
| 7 | **Blade** | **Tool steel / high-carbon steel, 20–30° sharpened angle, 1.8–3 mm thick**, floating on a stiffener, edge 0.5–1 mm off the dohyo | Commercial sumo blades are exactly this: 200×26.5×1.9 mm @ 23° (§4.1) |
| 8 | **Sensing** | **5 digital IR opponent sensors (±10° each, 0.9 ms response) + 5 downward edge sensors + motor-current sensing for contact** | 5-sensor frontal array is the standard the vendor itself cites (§5.1) |
| 9 | **Start** | Robot must be **moving within 60–100 ms** of the start, at full duty; use the first 300 ms to reach the opponent's shikiri line | Accelerating to 1 m/s takes only 6–24 ms of traction-limited time, so electronics latency is the whole battle (§5.4) |
| 10 | **Legal red line** | Magnets are **only allowed in the 3 kg class**; sharp edges must have r > 0.005" | [RoboGames Unified Sumo Rules Art. 6.7, 6.8](https://robogames.net/rules/all-sumo.php) |

---

## 1. Magnet downforce engineering

### 1.1 The two governing equations

Both are quoted verbatim (in different notation) in the peer-reviewed literature on magnetic sumo robots.

**Air-gap flux density** (lumped magnetic circuit — [NovaSolver](https://novasolver.jp/en/tools/magnet-strength-neodymium-air-gap.html)):

```
B_gap = Br · (t/g) / ((t/g) + 1) · k_arr
```

* `Br` — residual flux density: **1.30 T for N42, 1.43–1.45 T for N52, 1.47 T (as specified) for the N52 cubes used in the Polish tests**
* `t` — magnet thickness **along the magnetising axis**
* `g` — total air gap between magnet face and steel
* `k_arr` — arrangement factor: 1.0 single pole, ~1.4 Halbach, ~1.5 two-pole attract

**Pull force** (Maxwell stress; this is equation (1) of [Łapińska et al., IJMERR 9(5) 2020](https://ijmerr.com/uploadfile/2020/0417/20200417064856590.pdf)):

```
F = B_gap² · A / (2·μ0)          μ0 = 4π×10⁻⁷ H/m
```

Reality corrections, in order of importance:

1. **Fringing/leakage.** 20–50% of flux escapes sideways; leakage dominates once `g > t` ([NovaSolver](https://novasolver.jp/en/tools/magnet-strength-neodymium-air-gap.html)).
2. **Saturation of the target steel.** The dohyo plate is SS400 / ASTM A32-class steel; saturation is ≈1.6 T (SS400) to ≈2.1 T (pure iron). `B_gap` cannot usefully exceed this, capping force at ≈1.0 N/mm² (at 1.6 T, F/A = 1.6²/(2·4π×10⁻⁷) = **1.02 N/mm²**; at 2.1 T, **1.75 N/mm²**). This is the single most important hard ceiling.
3. **Alternating-polarity cancellation** in naïve arrays (adjacent opposite poles fight each other).

### 1.2 Measured / simulated data from the literature

**[A] Łapińska et al., IJMERR 9(5) 2020** — N52 **5×5×5 mm** cubes (0.94 g each, `Br` 1.47 T, vendor "holding force" 1.6 kg/item). COMSOL simulation **and** MTS 858 pull-off experiment. Values below are the paper's Tables II/III divided by the magnet count to give **N per magnet**, so you can scale to your own array.

| Gap (mm) | **Halbach** F/magnet (N) | Halbach kgf/magnet | **Alternating polarity** F/magnet (N) | Halbach ÷ AltPol | N per gram |
|---|---|---|---|---|---|
| 0.1 | 13.12 | 1.34 | 7.94 | **1.65** | 13.96 |
| 0.2 | 11.60 | 1.18 | 6.54 | 1.77 | 12.34 |
| 0.3 | 10.36 | 1.06 | 5.47 | 1.89 | 11.02 |
| 0.4 | 9.32 | 0.95 | 4.62 | 2.02 | 9.91 |
| 0.5 | 8.42 | 0.86 | 3.94 | 2.14 | 8.96 |
| 0.6 | 7.64 | 0.78 | 3.37 | 2.27 | 8.13 |
| 0.7 | 6.95 | 0.71 | 2.90 | 2.40 | 7.39 |
| 0.8 | 6.33 | 0.65 | 2.50 | 2.54 | 6.74 |
| 0.9 | 5.78 | 0.59 | 2.16 | 2.68 | 6.15 |
| 1.0 | 5.29 | 0.54 | 1.87 | **2.83** | 5.63 |

Experimental peak pull-off forces from the same paper: **2617.4 N for 200 magnets in Halbach**, **1592.8 N for 200 in alternating polarity** (a **1024.6 N** difference); **1274.8 N for 100 magnets in Halbach** vs **822.7 N for 100 alternating**. *Note: the paper's Table III for 100 magnets repeats the alternating-polarity column of Table II verbatim — an apparent copy error. Treat the 100-magnet alternating-polarity simulation column as unreliable; the experimental peak values are quoted separately and are consistent.*

**[B] Dziubek, Falkowski, Łapińska & Grądzki, IJMERR 10(6) 2021** — "Research of Hybrid Magnetic System Used in Autonomous MegaSumo Robots". **This is the best real-robot measurement available.**

* **60 neodymium magnets in a Halbach array + 2 electromagnets** on a 6 mm aluminium plate imitating the robot floor.
* Pulled away from a **10 mm thick steel plate** by an MTS 858 Table Top System; data at 25 Hz, lift increment ≈0.001 mm.
* **Permanent magnets only: measured peak ≈ 846 N = 86.3 kgf** for a **3 kg robot** (max allowed mass) — i.e. **28.8× the robot's own weight**.
* Per magnet: **846 / 60 = 14.1 N/magnet = 1.44 kgf/magnet** from 0.94 g magnets ⇒ **15.0 N per gram of N52**.
* **Electromagnets on: 1333.86 N = 136.0 kgf.** Delta **487.9 N**, i.e. **24.9 kgf per electromagnet**, a **+37%** increase.
* "the attraction … can be changed from 846 N to 1334 N **within a fraction of a second**"
* Authors propose the hybrid approach mainly for robots doing **5–7 m/s**.
* Design target stated in the 2020 companion paper: *"it is assumed that it should have about 2000 N of attraction force on the ring, and one neodymium magnet has about 10 N capacity. So, theoretically, 200 pieces of magnets are needed."*

**[C] Vendor figures (JSumo)** — single magnet, **zero gap, 3 mm thick steel, largest face**:

| Part | Dimensions | Mass | Claimed pull | Price |
|---|---|---|---|---|
| [JS19739](https://www.jsumo.com/neodymium-magnet-block-strong-n52-10mm-x-5mm-x-15-mm) | 10 × 5 × 15 mm N52, Ni-Cu-Ni | 10 g | **4 kgf (39.2 N)** | $2.50 |
| [JS15667](https://www.jsumo.com/neodymium-magnet-square-block-strong-n52-20mm-x-20mm-x-5-mm) | 20 × 20 × 5 mm N52 | 18 g | **8 kgf (78.5 N)** | $4.50 |

**Idealised Maxwell check (estimate).** From `F = B²A/(2μ0)`, the claimed 78.5 N over a 400 mm² pole face implies a mean `B = √(2·μ0·78.5/(400×10⁻⁶)) = **0.702 T***. That is *far* below `Br` = 1.43 T, which is physically consistent — it is exactly the leakage-and-reluctance penalty you should expect. The **absolute** Maxwell ceiling for that face at `B = Br` would be **325.5 N (33.2 kgf)**, and it is unreachable. **Do not size your design to 8 kgf for this magnet.** Use §1.3.

### 1.3 The working number: force per gram of N52

This is the most useful single design constant. Assembled from the measurements above:

| Source / configuration | Total force | Magnet mass | **N per gram** |
|---|---|---|---|
| IJMERR 2021, 60-magnet Halbach, ~0 gap, **measured** | 846 N | 56.4 g | **15.0** |
| IJMERR 2020, 200-magnet Halbach @ 0.1 mm (sim) | 2624.7 N | 188 g | 13.96 |
| IJMERR 2020, 200-magnet Halbach @ 0.5 mm (sim) | 1684.5 N | 188 g | 8.96 |
| IJMERR 2020, 200-magnet Halbach @ 1.0 mm (sim) | 1057.6 N | 188 g | 5.63 |
| IJMERR 2020, 200-magnet AltPol @ 1.0 mm (sim) | 373.4 N | 188 g | 1.99 |
| JSumo 10×5×15 block, vendor claim | 39.2 N | 10 g | 3.9 |
| JSumo 20×20×5 block, vendor claim | 78.5 N | 18 g | 4.4 |

**Design rule (estimate).** For a *good* Halbach array on a clean steel dohyo:

```
N52 mass needed [g]  ≈  target downforce [N] / k,   k = 5 … 15 N/g
   k ≈ 12–15  →  gap 0.1–0.2 mm, perfect layout (unrealistic in a real chassis)
   k ≈  8–10  →  gap 0.4–0.5 mm, Halbach, magnets bedded in pockets  ← DESIGN HERE
   k ≈  5–6   →  gap 1.0 mm      , Halbach
   k ≈  2     →  gap 1.0 mm      , alternating polarity (don't)
```

Concretely, for a **3 kg robot**:

| Target downforce | N52 mass @ 10 N/g | N52 mass @ 6 N/g | Number of 20×20×5 blocks (18 g) @10 N/g |
|---|---|---|---|
| 98 N (10 kgf) | 10 g | 16 g | 1 |
| 294 N (30 kgf) | 29 g | 49 g | 2 |
| 490 N (50 kgf) | 49 g | 82 g | 3 |
| 785 N (80 kgf) | 79 g | 131 g | 5 |

**Recommendation:** budget **100–150 g of N52** for a 3 kg robot (≈6–8 × 20×20×5 mm blocks, or ~40 × 5×5×5 mm cubes). At 6–10 N/g that is **590–1500 N (60–150 kgf)** of downforce — comfortably into the range where traction is no longer the limiting factor. *You must weigh your own array on a scale: put the magnet array on a kitchen scale with a steel plate on top, zero it, then pull the plate off vertically and read the peak.* This costs nothing and replaces every estimate above with your own data.

### 1.4 How force falls with distance — the gap table

Computed from §1.1 with `Br` = 1.43 T (N52), `t` = 5 mm, `A` = 400 mm² (20×20 mm face), **estimate**, clamped at `B_sat` = 1.6 T:

| Gap | `B_gap` (T) | Force (N) | Force (kgf) | Fraction of force at 0.1 mm | Loss per extra 0.1 mm |
|---|---|---|---|---|---|
| 0.10 mm | 1.402 | 312.8 | 31.9 | 1.000 | −3.7% |
| 0.25 mm | 1.362 | 295.2 | 30.1 | 0.944 | −3.7% |
| 0.50 mm | 1.300 | 269.0 | 27.4 | 0.860 | −3.5% |
| 0.75 mm | 1.243 | 246.1 | 25.1 | 0.787 | −2.6% |
| 1.00 mm | 1.192 | 226.0 | 23.0 | **0.722** | −2.6% |
| 1.50 mm | 1.100 | 192.6 | 19.6 | 0.616 | −2.5% |
| 2.00 mm | 1.021 | 166.1 | 16.9 | **0.531** | — |
| 3.00 mm | 0.894 | 127.1 | 13.0 | 0.406 | — |
| 5.00 mm | 0.715 | 81.4 | 8.3 | 0.260 | — |
| 8.00 mm | 0.612 | 48.1 | 4.9 | 0.154 | — |

**Robust gap ratios that need no magnet data at all** (`F ∝ B²` and `B ∝ (t/g)/((t/g)+1)`; **estimate**):

| Magnet thickness `t` | F(1.0 mm)/F(0.5 mm) | F(2.0 mm)/F(1.0 mm) | F(3 mm)/F(1 mm) |
|---|---|---|---|
| 3 mm | 0.766 | 0.640 | ~0.44 |
| 5 mm | **0.840** | 0.735 | 0.56 |
| 8 mm | 0.892 | 0.810 | 0.66 |
| 10 mm | 0.911 | 0.840 | 0.70 |

**Two consequences that change hardware decisions:**

1. **Thicker magnets are worth it asymmetrically.** Going from `t` = 3 mm to `t` = 10 mm cuts the 1→3 mm gap sensitivity from −56% to −30%. If your chassis flexes, thicker magnets are your insurance.
2. **The exponent is not a fixed `n`.** `F ∝ 1/g^n` is a bad model. Fitted to the table above, the *local* exponent is ≈ **0.36** over 0.1–0.5 mm, ≈ **0.45** over 0.7–1.5 mm, ≈ **0.71** over 1.5–3.0 mm and ≈ **0.95** over 3.0–5.0 mm. It only approaches the textbook `g^-2` once `g` exceeds roughly `2t`. **Use the table, not a power law.** (The theoretical asymptotic exponent is exactly 2, since `B → Br·t/g` as `g ≫ t`.)
3. **Over a third of your downforce is gone by 2 mm.** 269.0 N at 0.5 mm → 226.0 N at 1.0 mm (**−16.0%**) → 192.6 N at 1.5 mm (**−28.4%**) → 166.1 N at 2.0 mm (**−38.2%**). This is why the magnet standoff is the most valuable 0.5 mm in the whole robot.

**Cross-check against the two independent published datasets** (validates the model):

| Dataset | Gap | Model prediction | Published measurement | Agreement |
|---|---|---|---|---|
| 5×5×5 N52 cube (IJMERR 2020, Halbach) | 0.1 mm | 20.7 N | 13.1 N | model 1.58× high (leakage) |
| Same | 0.5 mm | 17.8 N | 8.4 N | model 2.11× high |
| Same | 1.0 mm | 14.9 N | 5.3 N | model 2.82× high |
| 60-magnet Halbach (IJMERR 2021) | ~0 | 20.7 N/magnet | 14.1 N/magnet | model 1.47× high |

The growing discrepancy with gap is exactly the fringing loss NovaSolver warns about, and it is why the **8–10 N/g band is the honest design figure, not 14–22 N/g.** The model is a good *relative* tool (gap sensitivity, grade comparison, shape comparison) and a poor *absolute* predictor.

### 1.5 Grade choice: N35 vs N42 vs N52

| Grade | `Br` (T) | `(BH)max` (MGOe) | Max service temp (standard) | Relative force (∝Br²) | Notes |
|---|---|---|---|---|---|
| N35 | ~1.17–1.21 | 35 | 80 °C | 0.67 | cheapest; only if space-limited-not-mass-limited |
| N42 | ~1.30 | 42 | 80 °C | 0.83 | best value; **harder to demagnetise than N52** |
| N48 | ~1.37 | 48 | 80 °C | 0.92 | |
| N52 | ~1.43–1.45 | 52 | 80 °C | **1.00** | max force per gram; most brittle, most demagnetisation-prone |
| N35SH | ~1.17–1.21 | 35 | **150 °C** | 0.67 | for high-temp; not needed here |

Sources: [NovaSolver](https://novasolver.jp/en/tools/magnet-strength-neodymium-air-gap.html) (Br values, temp coefficients, `k_arr`), [ABCM CREEM 2014 paper](https://abcm.org.br/app/webroot/anais/creem/2014/Projeto%20de%20M%C3%A1quinas/AN%C3%81LISE%20NUM%C3%89RICA%20DA%20INFLU%C3%8ANCIA%20DE%20%C3%8DM%C3%83S%20DE%20NEOD%C3%8DMIO%20NA%20RELA%C3%87%C3%83O%20INDU%C3%87%C3%83O%20PESO%20EM%20ESTRUTURAS%20DE%20ROB%C3%94S%20DE%20SUM%C3%94.pdf) (NdFeB Br 14 600 G = 1.46 T, HcMax 12 300 Oe, BHmax 26–51 MGOe vs SmCo/AlNiCo/ceramic).

**Verdict:** **N42 for most of the array, N52 only if you are mass-limited.** The difference is ~20% in force, and N42 is cheaper and mechanically tougher. Temperature is a non-issue in a 3-minute indoor match, but note `Br` falls **−0.12 %/°C** and force (∝Br²) therefore **−0.24 %/°C** — a magnet that reaches 80 °C is 13% weaker than at 25 °C. Vendor pages explicitly warn magnets permanently degrade above 80 °C and to **not grind them or use heat** ([JSumo](https://www.jsumo.com/neodymium-magnet-block-strong-n52-10mm-x-5mm-x-15-mm)).

### 1.6 Shape: why rectangular beats disc near wheels and the wedge

| Aspect | Disc / cylinder | Block / rectangular | Consequence for a sumo robot |
|---|---|---|---|
| Packing into a rectangular chassis | ~78.5% of a square cell (π/4) | ~100% | Blocks put **27% more pole area in the same footprint** |
| Wedge / wheel-well geometry | curve leaves gaps | can be cut long and thin (e.g. 10×5×15) to run the full width | a 200 mm-wide robot can carry a 200 mm-wide magnet line under the blade |
| Magnetising direction | axial is easy; diametric needs custom | through-thickness is standard and cheapest | blocks give a predictable, flat pole face → uniform gap |
| Edge field / `B` uniformity | pole face `B` peaks at centre, falls at rim | **more uniform** across the face | uniform `B` = uniform downforce = predictable traction |
| Cost per N | usually higher | lower | JSumo's 20×20×5 block is $4.50 for 18 g |
| Stacking for thickness | hard | trivial: stack 2× 5 mm → 10 mm equivalent | lets you trade `t/g` ratio (§1.4) |

**The `B`-uniformity argument is empirical, not theoretical.** The Brazilian ABCM/JMEA work explicitly chose a **ring** geometry (OD 40 mm, ID 6 mm, `t` = 10 mm, N42) precisely because ring magnets can be magnetised axially *and* diametrically, and because they wanted a *uniform* field: *"the model of magnet proposed has the best ratio distance/magnetic field, where it developed a relatively uniform field of sufficient intensity, varying 5200 to 3600 gauss"* over its working range ([ABCM CREEM 2014](https://abcm.org.br/app/webroot/anais/creem/2014/Projeto%20de%20M%C3%A1quinas/AN%C3%81LISE%20NUM%C3%89RICA%20DA%20INFLU%C3%8ANCIA%20DE%20%C3%8DM%C3%83S%20DE%20NEOD%C3%8DMIO%20NA%20RELA%C3%87%C3%83O%20INDU%C3%87%C3%83O%20PESO%20EM%20ESTRUTURAS%20DE%20ROB%C3%94S%20DE%20SUM%C3%94.pdf), [JMEA 5 (2015) 197–200](https://pdfs.semanticscholar.org/e1bd/ba9e02226587f4042d5eb018628bcd565206.pdf)). They report K&J pull force **46.18 lb = 20.94 kgf = 205.4 N** for that ring.

> **Sanity check on that ring (estimate).** Annulus area = π/4·(40² − 6²) = **1228.4 mm²**. If F = 205.4 N, implied mean `B = √(2μ0·205.4/(1228.4e-6)) = **0.648 T*** over the annulus. Plausible for a 10 mm-thick N42 ring at zero gap with a 6 mm hole. Six such magnets = **125.6 kgf (1232 N)**, which is where the paper's famous *"increase of 40 times the weight of the robot"* claim comes from (125.6 / 3 kg = 41.9×). **Cited for calibration only — the paper contains no measured pull-off test and no chassis implementation, and its "40× weight" figure is a design target, not a verified result.** The same authors' FEA did show structural deformation of **0.2658 mm** at that loading, which is a useful warning: 1+ kN of magnet force will visibly flex your chassis.

### 1.7 From downforce to friction force

```
F_traction(max) = μ · N_total = μ · (m_robot·g + F_magnets)
```

Computed (**estimate**) at μ = 0.7 (conservative) and μ = 1.0 (optimistic):

| Robot | Extra downforce | `N_total` | Traction @ μ=0.7 | Traction @ μ=1.0 | **Equivalent ballasted mass** @ μ=1.0 |
|---|---|---|---|---|---|
| 1 kg | 0 | 9.8 N | 6.9 N (0.7 kgf) | 9.8 N (1.0 kgf) | 1.0 kg |
| 1 kg | 10 kgf (98 N) | 107.9 N | 75.5 N | 107.9 N | **11.0 kg** |
| 1 kg | 30 kgf (294 N) | 304.0 N | 212.8 N | 304.0 N | **31.0 kg** |
| 3 kg | 0 | 29.4 N | 20.6 N | 29.4 N | 3.0 kg |
| 3 kg | 10 kgf | 127.5 N | 89.2 N | 127.5 N | 13.0 kg |
| 3 kg | 30 kgf | 323.6 N | 226.5 N | 323.6 N | **33.0 kg** |
| 3 kg | 50 kgf | 519.8 N | 363.8 N | 519.8 N | 53.0 kg |
| 3 kg | 80 kgf | 814.0 N | 569.8 N | 814.0 N | **83.0 kg** |

**Coefficient of friction values — evidence-status is weak, be careful.** I could **not** find a sumo-specific measured μ for rubber/urethane on a polyurethane-coated steel dohyo. For orientation only: rubber on dry clean steel is commonly quoted in the **0.6–0.9** band and urethane on steel roughly **0.5–0.7**; both fall sharply with contamination (oil, dust, dohyo paint removed by magnet scraping). **Marked UNCONFIRMED.** The one genuinely useful operational fact I did find is the cleaning practice: the NEMO 03 designers state *"washing the tires each time before the fight to clean them of any dirt. Technical acetone is the best in this regard"* ([miniSUMO-JS, p.4](https://marcinjablonski.rwbb.pl/wp-content/uploads/2022/03/miniSUMO-JS-en.pdf)). **Measure your own μ**: place the robot on a steel plate, add ballast until it slides, `μ = tan(θ)` on a tilting plate.

**Non-fabricated takeaway:** even 10 kgf of downforce multiplies your traction by **~10×**, and 30 kgf by **~11× (1 kg class) / ~11× (3 kg class)**. Beyond ~30 kgf, the marginal benefit to *traction* is small — the remaining reason to add downforce is **resisting being lifted and pushed**, not accelerating.

### 1.8 Risks — with mitigations

| Risk | Mechanism / evidence | Mitigation |
|---|---|---|
| **Pulled down, losing ground clearance** | The 2021 paper's own test rig showed an *apparent force increase* at nominally zero gap caused by **"deformation of the material from which the test system was built"** — your chassis will bow too. FEA of the ABCM ring design gave **0.2658 mm** deflection. | Use a stiff baseplate: JSumo recommends **5–6 mm aluminium, 60XX/70XX series** ([JSumo](https://blog.jsumo.com/how-to-make-sumo-robot/)). Set your minimum gap from a **loaded** measurement (robot on the dohyo, batteries in), not an unloaded one. Add **0.3–0.5 mm nylon/PTFE skids** as hard stops so the magnets can never touch. |
| **Collecting steel debris** | NdFeB magnets pick up swarf, staples, dohyo paint flakes. Debris *becomes* a spacer that increases your gap. | Pot the magnets in epoxy or cover with a thin non-magnetic skid; wipe down between rounds; **never** store near tools. |
| **Hall / IMU / sensor interference** | The 2021 paper solved this by design: *"The housing used in the electromagnet directs the propagation of the magnetic field while preventing it from affecting the other components of the robot — the magnetic field does not interfere with the operation of the control electronics and sensors."* | Keep **>40 mm** between the magnet array and any Hall sensor, magnetometer, or encoder; **do not use a magnetometer at all**; use a **steel keeper/return yoke** above the magnets to close the flux path upward; shielded twisted pair for encoder lines. |
| **Demagnetisation from impact** | NdFeB has high `Hcj` but its own operating point in a *wide-gap* circuit is low. NovaSolver: *"if the operating point sits above 70% of Br, choose N52; below 50%, prefer N42 or N35SH"* — i.e. **N52 in a badly-designed wide-gap circuit can demagnetise and end up weaker than N42**. A hard front-on impact is exactly a demagnetising shock. | Choose **N42** if your gap is >1 mm; keep the working point high (small gap, thick magnet); avoid hitting the dohyo edge with the magnet pack. |
| **Shattering / chipping** | Sintered NdFeB is brittle; nickel plating chips at edges. Vendors warn to **not grind and not heat** ([JSumo](https://www.jsumo.com/neodymium-magnet-block-strong-n52-10mm-x-5mm-x-15-mm)). See also [supermagnete FAQ on coating chipping](https://www.supermagnete.it/eng/faq/Why-does-the-coating-of-my-magnets-chip) and [First4Magnets on protecting magnets from chipping](https://www.first4magnets.com/blog/how-to-protect-magnets-from-chipping/). | **Bed magnets fully in machined pockets** so the steel takes the impact, not the magnet; epoxy them in (Araldite-class epoxy is what the ABCM authors specify, to avoid chemical attack on the magnet); leave a 0.2–0.3 mm epoxy or tape skin over the face; **radius all corners**. |
| **Dohyo paint damage ⇒ disqualification** | The 2021 paper: *"Damage resulting from peeling off the paint layer before the collision disqualifies the robot from the fight, and those caused during the collision are not taken into account."* | Keep magnets ≥0.3 mm off the surface; smooth the skids; this is a real DQ risk that a pure "minimum gap" strategy creates. |
| **Legality** | *"Devices to increase down force, such as a vacuum pump or magnets, are only allowed in the 3 kg class. They are not allowed in all other classes."* — [RoboGames Art. 6.7](https://robogames.net/rules/all-sumo.php) | **If the team may also enter 1 kg / mini, magnets are illegal there.** Check your specific event's rulebook before building two robots around magnets. |

---

## 2. Drivetrain for a magnetic arena

### 2.1 Motor data (from manufacturer/vendor pages — no interpolated numbers)

**Pololu 37D metal gearmotors.** Source: [Pololu #4753 50:1 with encoder product page](https://www.pololu.com/product/4753) and its full 12 V / 24 V comparison table.

| Version | Gear ratio | No-load speed (RPM) | **Extrapolated stall torque** | Stall current | Max power | Price |
|---|---|---|---|---|---|---|
| 12 V | 1:1 | 10 000 | 0.5 kg·cm (49 mN·m) | 5.5 A | 7 W | — |
| 12 V | 19:1 | 530 | **8.5 kg·cm (0.834 N·m)** | 5.5 A | 12 W | $60.95 w/ enc. |
| 12 V | 30:1 | 330 | 14 kg·cm (1.373 N·m) | 5.5 A | 12 W | |
| 12 V | 50:1 | 200 | **21 kg·cm (2.059 N·m)** | 5.5 A | 10 W | $60.95 w/ enc. |
| 12 V | 70:1 | 150 | 27 kg·cm (2.648 N·m) | 5.5 A | 10 W | |
| 12 V | 100:1 | 100 | **34 kg·cm (3.334 N·m)** | 5.5 A | 8 W | |
| 12 V | 131:1 | 76 | 45 kg·cm (4.413 N·m) | 5.5 A | 6 W | |
| 12 V | 150:1 | 67 | 49 kg·cm (4.806 N·m) | 5.5 A | 6 W | |
| 24 V | 19:1 | 530 | 9.5 kg·cm | 3 A | 13 W | |
| 24 V | 50:1 | 200 | **23 kg·cm (2.256 N·m)** | 3 A | 12 W | |
| 24 V | 100:1 | 100 | **39 kg·cm (3.825 N·m)** | 3 A | 8 W | |

Critical caveats **from Pololu's own text**, verbatim: *"The listed stall torques and currents are theoretical extrapolations; units will typically stall well before these points as the motors heat up."* and *"The recommended upper limit for continuously applied loads is **10 kg·cm (150 oz·in)**, and the recommended upper limit for instantaneous torque is **25 kg·cm (350 oz·in)**."* Also: *"a general recommendation for brushed DC motor operation is **25% or less of the stall current**."* Shaft is 6 mm D, 16 mm long; mounting holes are 6× M3 on a 15.5 mm hexagon; mass **≈200 g** (UNCONFIRMED exact figure for the encoder versions). Encoder: 64 CPR at the motor shaft = **3200 CPR at the output** (50:1).

**Maxon DCX 35 L** (Ø35 mm, graphite brushes, ball bearings) — [maxon product page](https://www.maxongroup.co.kr/maxon/view/product/motor/dcmotor/DCX/DCX35/DCX35L01GBKL511):

| Parameter | Value |
|---|---|
| Nominal voltage | 24 V |
| No-load speed | 7720 rpm |
| No-load current | 146 mA |
| **Nominal (max continuous) torque** | **121 mN·m** |
| Nominal current | 4.26 A |
| **Stall torque** | **2030 mN·m (2.03 N·m)** |
| **Stall current** | **69.3 A** |
| Torque constant | 29.3 mN·m/A |
| Speed constant | 326 rpm/V |
| Speed/torque gradient | 3.86 rpm/mN·m |
| Terminal resistance | 0.346 Ω |
| Rotor inertia | 96.6 g·cm² |
| Mechanical time constant | 3.91 ms |
| Max permitted speed | 12 300 rpm |
| Mass | **385 g** |
| Price | **CHF 331.80 (1–4 off)** ≈ $370 each |

**Maxon RE35** (via [JSumo](https://www.jsumo.com/maxon-re35-dc-motor-24v-model-273752-323890), which used it in a robot that took 2nd at All Japan International Robot Sumo 2013 and calls it *"Popular model for lots of Japanese sumo robots too"*): Ø35 mm, 6 mm shaft, **7800 rpm at 24 V**, **stall 40 A / continuous 5 A**, mass **340 g**, price **$420 (out of stock)**. JSumo's editorial: *"Maxon RE35 models (35 mm dia, 340 g) have better usage capability than RE40 (40 mm dia, 480 g) … cheaper and much lighter."* Note the RE35 has **no gearbox** — the 7800 rpm is at the motor shaft.

**JSumo Titan 12 V 1000 RPM HP** ([product page](https://www.jsumo.com/jsumo-titan-dc-gearhead-motor-12v-1000-rpm-hp)): Ø37 mm × 75 mm, 6 mm × 17 mm shaft, 6× M3 front holes, no-load **240 mA**, **stall 5.9 A**, **stall torque 7.5 kg·cm (0.735 N·m)**, mass **190 g**, **$27.00**. Vendor explicitly says: *"Best Motors for **non magnetic** style sumo robots. If dohyo is wood, this motor is must!"* — **i.e. this is not the motor for a magnetic arena.**

**JSumo Symtec Q** ([product page](https://www.jsumo.com/symtec-q-gear-motor-12v-1450rpm)) — the only vendor motor explicitly marketed for magnetic dohyos:

| Parameter | Value |
|---|---|
| Voltage | 12 V (**rated to 24 V**) |
| Gear ratio | **9.28:1** |
| Speed | **1450 RPM @ 12 V** |
| No-load current | 2.90 A |
| **Stall current** | **121 A** |
| **Stall torque (tested)** | **44 kg·cm (4.31 N·m / 4314.9 mN·m / 38.2 in-lb)** |
| Peak energy | 400 W (0.53 hp) |
| Torque constant | 0.36 kg·cm/A |
| Coil inductance / resistance | 87.3 µH / **140 mΩ** |
| Weight | **640 g** |
| Dimensions | gearbox 98 × 48 × 25.5 mm; motor Ø45 × 40 mm |
| Gear material / shaft | **hardened steel** / 30 × 10 mm D-type, **double-bearing supported** |
| Price | **$94.50** (pre-order; *"Earliest shipment date is October 2026"* — **check availability before committing**) |

Vendor notes: *"We tested these motors from 12V to 24V they work well and handle overvoltaging good"* and *"Suitable for: Combat Robots, **Sumo Robots (Magnetic & Non-Magnetic)**, … All Terrain Robots (**From 3 kg to 20 kg**)"*.

**Generic Chinese "37GB" 12 V gearmotors.** A typical listing is [37GB-520, 12 V, 35 RPM, 37 mm D-shaft](https://kitsguru.com/products/gb37-520-dc12v-12rpm-min-miniature-forward-and-reverse-brushed-dc-speed-reducer-motor-copy). I **could not confirm** reliable stall-torque or stall-current figures for these; quoted torques on marketplace listings are usually *rated*, not stall, and vary wildly between sellers. **Treat as UNCONFIRMED.** They are dimensionally similar to the Pololu 37D but have plastic or sintered gears and no datasheet — **not recommended for a magnetic 3 kg robot** where a single impact stall can be >5 A per motor.

**N20 / N30 micro gearmotors** — appropriate only for micro-sumo (≤100 g). **UNCONFIRMED** for 1 kg class; they cannot survive the stall currents a magnetic 1 kg robot demands.

### 2.2 Speed from RPM and wheel diameter

`v [m/s] = RPM × π × D / 60` (**estimate** — pure kinematics, but assumes zero slip):

| RPM | 40 mm | 50 mm | 60 mm | 75 mm | 90 mm |
|---|---|---|---|---|---|
| 100 | 0.21 | 0.26 | 0.31 | 0.39 | 0.47 |
| 150 | 0.31 | 0.39 | 0.47 | 0.59 | 0.71 |
| 200 | 0.42 | **0.52** | 0.63 | 0.79 | 0.94 |
| 300 | 0.63 | 0.79 | 0.94 | 1.18 | 1.41 |
| 500 | 1.05 | 1.31 | 1.57 | 1.96 | 2.36 |
| 1000 | 2.09 | 2.62 | 3.14 | 3.93 | 4.71 |
| 1450 | 3.04 | 3.80 | 4.56 | 5.69 | 6.83 |
| 2000 | 4.19 | 5.24 | 6.28 | 7.85 | 9.42 |

RPM needed for a target speed (**estimate**):

| Target | 40 mm | 50 mm | 60 mm | 75 mm | 90 mm |
|---|---|---|---|---|---|
| 1.0 m/s | 477 | 382 | 318 | 255 | 212 |
| 2.0 m/s | 955 | 764 | 637 | 509 | 424 |
| 3.0 m/s | 1432 | 1146 | 955 | 764 | 637 |
| 5.0 m/s | 2387 | 1910 | 1592 | 1273 | 1061 |
| 6.5 m/s | 3104 | 2483 | 2069 | 1655 | 1379 |

**This table explains the Japanese "18:1–20:1 with big wheels" convention immediately.** A 5000 rpm motor shaft through an 18:1 reduction gives 278 rpm at the wheel; on a **75 mm** wheel that is **1.09 m/s**, on a 90 mm wheel **1.31 m/s**. If you instead used a 30 mm wheel you would get 0.44 m/s and be a sitting target.

**But be careful about the direction of the torque trade — many builders get this backwards.** `T_wheel = F·r`, so **a larger wheel *increases* the torque you must find**, it does not reduce it. The Japanese big-wheel/low-ratio recipe works for a different and more subtle reason:

```
F_pull = 2·T_motor·ratio·η / D          v = (RPM_motor/ratio)·π·D/60
Eliminate D:   F_pull = 2·T_motor·ratio·η·(RPM_motor/ratio)·π / (60·v)
                      = π·η·T_motor·RPM_motor / (30·v)
```

**The pull force available at a given speed depends only on the motor's `T·RPM` product (i.e. its power), not on the wheel diameter or the gear ratio at all.** Choosing `D` and `ratio` only moves you along the motor's torque–speed line. So:

* Big wheels + low ratio and small wheels + high ratio deliver **the same** `F` at the same `v`. The difference is **where the losses are**:
  * A **low ratio** (4.4:1, one or two stages) has **far less gear friction, backlash and shock fragility** than 50:1–150:1 (four or five stages). Pololu warns its own high-ratio units are *"constrained by gearbox load limits"* — note the asterisks on the 70:1–150:1 rows of its table, where output power is quoted *at the max recommended load of 10 kg·cm* rather than at the true peak.
  * A **big wheel** at low ratio therefore lets a powerful motor deliver its power **through a gearbox that can actually survive sumo impacts.**
* The price is exactly what the equations say: big wheels need big `T_motor·ratio`, which means **a big motor**. That is the whole cost of the Japanese approach, and it is why they pay CHF 332 for a Maxon.

Senju is the proof: **6.5 m/s with a 4.4:1 reduction** (see §2.5). A 37D-based robot cannot copy that — at 4.4:1 a 37D's 0.5 kg·cm motor would give 2.2 kg·cm at the wheel.

### 2.3 Required wheel torque to break traction

`T_wheel = μ · (m·g + F_mag) · r` (**estimate**; this is the *minimum* torque to use all available grip — anything more is wasted and just heats the motor). All in **kg·cm**, per **wheel**, sharing the load 50/50 between two wheels:

| Robot | F_mag | μ | N_total | F_max | D=30 | D=40 | D=50 | D=60 | D=75 |
|---|---|---|---|---|---|---|---|---|---|
| 1 kg | 0 | 0.7 | 9.8 N | 6.9 N | 1.0 | 1.4 | 1.7 | 2.1 | 2.6 |
| 1 kg | 10 kgf | 1.0 | 107.9 N | 107.9 N | 16.5 | 22.0 | 27.5 | 33.0 | 41.2 |
| 1 kg | 30 kgf | 1.0 | 304.0 N | 304.0 N | 46.5 | 62.0 | 77.5 | 93.0 | 116.2 |
| 3 kg | 0 | 0.7 | 29.4 N | 20.6 N | 3.1 | 4.2 | 5.2 | 6.3 | 7.9 |
| 3 kg | 10 kgf | 1.0 | 127.5 N | 127.5 N | 19.5 | 26.0 | **32.5** | 39.0 | 48.7 |
| 3 kg | 30 kgf | 1.0 | 323.6 N | 323.6 N | 49.5 | 66.0 | **82.5** | 99.0 | 123.7 |
| 3 kg | 50 kgf | 1.0 | 519.8 N | 519.8 N | 79.5 | 106.0 | **132.5** | 159.0 | 198.7 |
| 3 kg | 80 kgf | 1.0 | 814.0 N | 814.0 N | 124.5 | 166.0 | 207.5 | 249.0 | 311.2 |

**Read this carefully — it is the crux of the whole drivetrain decision.** For a 3 kg robot with 30 kgf of downforce and a 50 mm wheel you need **82.5 kg·cm (8.09 N·m) per wheel**. Pololu's 37D tops out at **34 kg·cm** extrapolated and is only rated for **10 kg·cm continuous / 25 kg·cm instantaneous**. **No Pololu 37D can fully exploit 30 kgf of downforce.** You have three legitimate options:

1. **Less downforce.** 10 kgf ⇒ 32.5 kg·cm/wheel needed vs 34 available. This is the sweet spot for a 37D-based robot.
2. **Smaller wheels.** At D = 30 mm and 30 kgf you need 49.5 kg·cm — still too much for one 37D, but fine for two 37D 100:1 on a **4WD** robot (4 × 34 = 136 kg·cm total).
3. **Bigger motors.** Maxon DCX35L + custom 18:1 (Japanese approach) or JSumo Symtec Q.

### 2.4 What each motor can actually pull

Pulling force available at the contact patch, `F = T_output / r`, **per wheel**, from the table in §2.1 (**estimate**):

| Motor | T_out (N·m) | @ 40 mm | @ 50 mm | @ 60 mm | Speed @ 50 mm |
|---|---|---|---|---|---|
| Pololu 37D 12 V 19:1 | 0.834 | 41.7 N | 33.3 N | 27.8 N | 0.52 m/s |
| Pololu 37D 12 V 30:1 | 1.373 | 68.6 N | 54.9 N | 45.8 N | 0.86 m/s |
| Pololu 37D 12 V 50:1 | 2.059 | 103.0 N | **82.4 N** | 68.6 N | 0.52 m/s |
| Pololu 37D 12 V 70:1 | 2.648 | 132.4 N | 105.9 N | 88.3 N | 0.39 m/s |
| Pololu 37D 12 V 100:1 | 3.334 | 166.7 N | **133.4 N** | 111.1 N | 0.26 m/s |
| Pololu 37D 24 V 50:1 | 2.256 | 112.8 N | 90.2 N | 75.2 N | 0.52 m/s |
| Pololu 37D 24 V 100:1 | 3.825 | 191.2 N | 153.0 N | 127.5 N | 0.26 m/s |
| JSumo Titan 12 V 1000 rpm | 0.735 | 36.8 N | 29.4 N | 24.5 N | 2.62 m/s |
| **JSumo Symtec Q 9.28:1** | 4.315 | 215.7 N | **172.6 N** | 143.8 N | 3.80 m/s |
| **Maxon DCX35L 24 V, no gb** | 2.030 | 101.5 N | 81.2 N | 67.7 N | 20.2 m/s (unusable — needs gearing) |

Peak mechanical power at half-stall, `T_stall·ω_noload/4` (**estimate**): Pololu 37D range **8.7–11.9 W**; JSumo Titan 19.3 W; **JSumo Symtec Q 163.8 W**; **Maxon DCX35L 410 W**. This is the clearest single indicator of which league each motor is in: a 37D is a ~10 W motor. JSumo's own guidance is **50–150 W, 12–24 V** for a sumo robot ([JSumo](https://blog.jsumo.com/how-to-make-sumo-robot/)) — which the Symtec Q meets and the 37D does not.

### 2.5 Worked design points

**Design A — 3 kg MegaSumo, budget, 4WD (RECOMMENDED for $500)**
* 4 × Pololu 37D **24 V 100:1** (no encoder version ≈ $40 each) = **$160**
* Wheel dia **50 mm** ⇒ v = 100 × π × 0.05/60 = **0.26 m/s**; torque **3.825 N·m × 4 = 15.3 N·m total**
* Magnet budget **40 g N52** (2 × 20×20×5 blocks + 4 × 10×5×15) ⇒ **≈240–400 N (25–40 kgf)** downforce at 6–10 N/g
* Traction available = 1.0 × (29.4 + 300) ≈ **330 N**; force available at wheels = 15.3/0.025 = **612 N**. **Motor-limited, not traction-limited** — good, and it means you can add more magnets.
* 0.26 m/s is slow. Add a second speed mode by switching to 50:1 (0.52 m/s, 2.059 N·m × 4 = 8.2 N·m ⇒ 330 N — exactly traction-limited). **Two interchangeable gearbox sets is the cheapest "gearing" upgrade you can buy.**

**Design B — 3 kg MegaSumo, performance (the Japanese recipe)**
* 2 × Maxon DCX35L 24 V ($370 ea ⇒ **$740 — over budget**) OR 2 × JSumo Symtec Q ($94.50 ea ⇒ **$189 but shipping Oct 2026**)
* Custom **18:1** on a **75–90 mm** wheel. With DCX35L: 7720/18 = 429 rpm ⇒ v = 429·π·0.075/60 = **1.68 m/s** at 75 mm. Wheel torque = 2.030 × 18 × 0.75 = **27.4 N·m per wheel**, i.e. 27.4/0.0375 = **731 N of pull per wheel**. Massively traction-limited with any magnet array — which is exactly what you want, because it means **no wheelspin ever, and full grip is always available for pushing**.
* Validate against the real hero robot: **Senju**, 4th at the 26th All Japan International Robot Sumo (Tokyo, Dec 2014), used **2 × Maxon DCX35L 24 V with a custom 4.4:1 gearbox and reported a max speed of 6.5 m/s** ([JSumo build log](https://blog.jsumo.com/senju-4-th-winner-japan-international-robot-sumo-december-2014-26th/)). *Sanity check (**estimate**): if 6.5 m/s were at the wheel, rpm = 6.5·60/(π·D). At D = 90 mm that is 1379 rpm at the wheel ⇒ 6068 rpm at the motor after 4.4:1, which is within the DCX35L's 7720 rpm no-load. So Senju's 6.5 m/s is consistent with ~90 mm wheels and **overvolting above 24 V** — which JSumo recommends explicitly for this motor.* This is the single most instructive data point in this report: **a 6.5 m/s, magnet-equipped, 3 kg robot with a 4.4:1 reduction.** Low ratio, huge wheels, huge motor, overvolted.

**Design C — 1 kg class (magnets illegal under RoboGames rules; check your event)**
* 2 × Pololu 20D/25D or 37D 12 V 50:1, **40 mm** wheel, v = 0.42 m/s; T_wheel needed with 10 kgf downforce at μ=1.0 = 22.0 kg·cm vs 21 kg·cm available — **marginal.** Use 4WD or 30:1... no: use **12 V 70:1** (27 kg·cm) and accept 0.31 m/s, or drop to 30 mm wheels (16.5 kg·cm needed) and keep the 50:1.

### 2.6 Motor drivers / H-bridges

| Driver | Continuous | Peak | Voltage drop / R_DS(on) | Max V | Price | Verdict for this build |
|---|---|---|---|---|---|---|
| **BTS7960 / IBT-2** | ~**43 A** per the BTS7960 half-bridge datasheet (the IBT-2 module stacks two) | — | 2× R_DS(on) ≈ **16 mΩ** total (8 mΩ per FET typ.) | 5.5–27 V | ~$6–12 | **Best value for 37D and Symtec-class motors.** Widely cloned; buy 4, they're cheap. **UNCONFIRMED** for genuine Infineon vs clone parts — derate to ~20 A continuous. |
| **VNH5019** | **30 A** | 60 A | R_DS(on) 18 mΩ total; `V_drop` ≈ 0.54 V at 30 A | 5.5–24 V | ~$27 ([Pololu #1451](https://www.pololu.com/product/1451)) | Excellent; Pololu itself recommends it for the 37D. Has current-sense output (useful for collision detection, §5.3). |
| **Pololu G2 High-Power 24v13 / 24v14 / 24v18** | 13 / 14 / 18 A | 40–60 A | R_DS(on) ~2–4 mΩ | 6.5–30 V | $35–60 | Pololu's own recommendation for 37D; the 24v18 version covers a 5.5 A stall with **>3× margin**. |
| **Cytron MDD10A** | 10 A | 30 A | — | 5–25 V | ~$22 | Adequate for one 37D pair. |
| **Cytron MDDS30** | 30 A | 80 A | — | 7–30 V | ~$30 | Good for Symtec Q / Maxon. |
| **DRV8871** | **3.6 A** | 6 A (current-limited) | R_DS(on) 0.45 Ω total ⇒ **1.6 V drop at 3.6 A** | 6.5–45 V | ~$8 | **Unsuitable** — a single 37D stalls at 5.5 A. |
| **L298N** | **2 A** | 3 A | **1.4–3.2 V** drop (bipolar Darlington) | 5–46 V | ~$3 | **Unsuitable.** A 37D stall is 2.75× its rating, and the voltage drop destroys your torque. (It appears in the literature — [Tirian et al. 2015](https://acta.fih.upt.ro/pdf/2015-3/ACTA-2015-3-21.pdf) use an L298N at "maximum current of 2 amperes" for a *mini*-sumo — but not for a magnetic 3 kg robot.) |

**Selection rule (estimate):** `I_continuous(driver) ≥ I_stall(motor)`. Pololu states *"we generally recommend a motor controller that can handle continuous currents above the stall current of your motor"* ([Pololu #4753](https://www.pololu.com/product/4753)). For 4 × 37D at 5.5 A stall (12 V) that is **22 A total**; for 2 × Symtec Q at 121 A stall it is **242 A**, which no hobby driver survives — you must **current-limit or PWM-limit the Symtec** and never let it sit at stall.

### 2.7 Overvolting ("give that juice")

**What it buys (estimate, and this is elementary DC-machine theory, not a measured claim):**
```
ω_noload ∝ V        (speed scales linearly with voltage)
T_stall   = k_t·V/R  ∝ V   (stall torque scales linearly with voltage)
P_max     ∝ V²
```
So **12 V → 24 V doubles both speed and stall torque, and quadruples peak power.** There is no free torque constant — the motor's `k_t` is fixed by its magnets and winding.

**What it costs:**
* **Heat ∝ I²R.** Doubling voltage doubles the current at a given torque output, so copper loss at that torque **quadruples**. `P_copper = I²·R_terminal`. For the Maxon DCX35L, `R = 0.346 Ω`; at its 69.3 A stall that is **1661 W** of heat in a 385 g motor. Its winding thermal time constant is **43 s** and motor thermal time constant **1030 s**, with max winding temp **+155 °C** and max permissible winding temperature rise to +100 °C housing.
* **Brush and commutator life** falls roughly with the square of current density. Pololu's guidance: *"a general recommendation for brushed DC motor operation is 25% or less of the stall current."*
* **Gearbox** becomes the weak link — Pololu explicitly caps continuous load at 10 kg·cm and instantaneous at 25 kg·cm regardless of what the motor can make.

**Evidence that overvolting is what winners do:**
* JSumo's own product copy for the Maxon RE35: *"we suggest you to **overvoltage that motors** for achieving real agile power."*
* JSumo's Symtec Q: *"We tested these motors from 12V to 24V they work well and **handle overvoltaging good**."*
* JSumo measured a **Maxon RE40 (12 V) on a 4S LiPo (16.8 V nominal)** and recorded **peak 7 A and peak 105 W** — against the datasheet's 105 A stall and 150 W rating, i.e. *"I think I couldn't enforce motor enough"* ([Maxon Motor Graph](https://blog.jsumo.com/maxon-motor-graph/)). **This is an important negative result: even at 1.4× nominal voltage and hard acceleration, the motor was nowhere near its rated power.** Real robots are traction- and time-limited, not motor-limited, at the moment of contact.
* The IJMERR 2021 paper, on the motor consequences of magnet drag: *"In a robot in this category, the nominal operating parameters of the engine are often deliberately exceeded. The increase in the current flowing through the windings occurs as a result of adding additional resistance from the attraction force of the magnets."* and *"Moving away from the engine's endurance limit may cause permanent structural damage."*

**How to manage it (concrete):**
1. **Choose the motor voltage to match your battery, then overvolt modestly.** 24 V motor on 6S LiPo (22.2 V nom, 25.2 V full) is *not* overvolting. 12 V motor on 4S (14.8 V nom) is 1.23× — safe. 12 V motor on 4S at full charge is 1.4×.
2. **PWM-limit sustained duty to ≤70%** except during the push. `I_rms` scales with duty.
3. **Add a hardware current limit or a fuse** sized at ~2× the continuous rating. A stalled 4WD 37D robot draws 22 A; a 30 A fuse protects the drivers and the battery without nuisance blows.
4. **Thermal path matters more than the FET.** Bolt drivers to the aluminium chassis with thermal pads (JSumo's own build guide uses a heatsink on the driver); use thermal paste; expose the motor cans to airflow.
5. **Cap the stall time in software.** If commanded duty is 100% and encoder counts are zero for >150 ms, cut to 40% and reverse briefly. **Estimate:** at 69 A stall the DCX35L's winding time constant is 43 s, so a 150 ms stall is thermally harmless — but at 121 A (Symtec Q) with 140 mΩ you are dissipating 2 kW into a 640 g motor, and the copper will not survive many seconds.
6. **The "give that juice" tactic** (see §5.3) is not really about voltage: it is about **holding 100% duty through the contact event** instead of easing off. That is free. Do that first, before you rewind or overvolt anything.

---

## 3. Wheels and traction

### 3.1 What the evidence actually says

| Source | Guidance | Verbatim |
|---|---|---|
| [JSumo, How to Make a Good Sumo Robot](https://blog.jsumo.com/how-to-make-sumo-robot/) | **Dia 35–55 mm**; **hard rubber or polyurethane**; **machined aluminium rims**; smaller is preferred for low inertia | *"35 to 55mm diameter wheels are used at our sumo robots. I prefer smaller wheels, because of having low inertia. You need to make custom made your wheels from hard rubber or polyurethane. And also wheel rims should be machined from aluminum."* |
| [miniSUMO-JS / NEMO 03 (winner, Robotic Day Prague 2018)](https://marcinjablonski.rwbb.pl/wp-content/uploads/2022/03/miniSUMO-JS-en.pdf) | **Modelling silicone**, washed with acetone before every fight | *"The constructors decided to use modeling silicone, which is also easy to mix and gives great grip… The key to victory is also washing the tires each time before the fight to clean them of any dirt. Technical acetone is the best in this regard."* |
| [Pololu 37D docs](https://www.pololu.com/product/4753) | 80 mm and 90 mm Pololu wheels and 6 mm scooter-wheel adapters exist for the 37D shaft | useful if you go the big-wheel route |
| [Tirian et al., Acta Tehnica Corviniensis 2015](https://acta.fih.upt.ro/pdf/2015-3/ACTA-2015-3-21.pdf) | 2 × Pololu-type motors at **100:1** — "a balance between speed and power" | *"If the strategy focuses on a powerful and slow robot, then motors with a high transfer rate are recommended. If the contrary, a swift and agile robot is needed, then the motors of choice will be a low transfer rate."* |

**There is no published Shore A recommendation specific to magnetic arenas. Marked UNCONFIRMED.** The following is engineering reasoning, not a citation:

### 3.2 Why hard rubber / urethane, and not soft silicone, on steel

| Property | Soft silicone (Shore A 20–30) | Hard rubber / cast urethane (Shore A 60–80) | Hard TPU 3D-printed (Shore 95A) |
|---|---|---|---|
| Contact patch | very large, conforms to surface | moderate | small |
| `μ` on clean steel | high, but **falls off fast with load** — the tread shears and rolls | **stable under high load** | moderate |
| Rolling resistance under 30–50 kgf | **very high** — the tyre permanently deforms; measurable power loss and heat | low | low |
| Wear | rapid under load | slow | medium (layer lines wear) |
| Behaviour when the magnet array slams it into the plate | squashes, throwing the air gap off by 0.5–1 mm | negligible deflection | negligible |
| When soft silicone *is* right | painted / non-magnetic / low-downforce arenas; mini-sumo; low load | — | prototyping only |

**The decisive argument on a magnetic dohyo is not `μ` — it is the air gap.** Soft silicone deflects under 300–800 N of magnet load, which *increases* your magnet-to-steel gap and *directly* cuts your downforce by the table in §1.4 (−3.5% per 0.1 mm at 0.5 mm gap). **A squishy tyre is a self-defeating magnet part.** Use hard tyres, keep the gap, and put the compliance in the *caster/skid* instead.

### 3.3 Diameter and width

| Class | Diameter | Width | Why |
|---|---|---|---|
| **1 kg mini/micro** | **30–40 mm** | 12–15 mm | small radius keeps torque demand low; the robot has little downforce |
| **3 kg MegaSumo (budget 37D)** | **40–50 mm** | 15–20 mm | 50 mm gives 0.26–0.52 m/s at 100–200 rpm and keeps T_wheel at 133 kg·cm for 30 kgf downforce |
| **3 kg MegaSumo (Maxon/Symtec)** | **60–90 mm** | 20–25 mm | large radius lets a **4.4:1–20:1** reduction make 1.1–1.7 m/s; matches the measured Senju configuration |

**The diameter/gear-ratio trade is exact and worth stating as an equation:**

```
v = (RPM_motor / ratio) · π · D / 60
T_wheel = T_motor · ratio · η          (η ≈ 0.7–0.8 for a spur/helical gearbox)
F_pull  = T_wheel / (D/2) = 2·T_motor·ratio·η / D
```

So **the pull force is independent of wheel diameter** given a fixed motor and ratio — but the *speed* scales with `D`. Increasing `D` at fixed ratio makes you faster **and** reduces the torque you must find elsewhere. Increasing `D` at fixed *speed* means you can **reduce the ratio**, which reduces gearbox losses and backlash and increases shock tolerance. That is the entire justification for the Japanese big-wheel/low-ratio school: **it is a reliability play, bought with a very expensive high-torque motor.**

**Width note (estimate).** Wider is better up to the point where the contact patch `μ` saturates and lateral scrub in turns costs you. For a 3 kg robot with 30+ kgf downforce, `μ_effective` is limited by the steel/compound pair, not by contact area — so **widen only to reduce wear and heat, not to gain grip.**

### 3.4 Drive layout

| Layout | Verdict for a magnetic dohyo |
|---|---|
| **2WD + 2 skids/casters** | Simplest, lightest. **Risk:** with 30+ kgf of downforce, a small caster wheel can dig in and act as a pivot; and a caster that touches down takes normal load off the drive wheels. **Use fixed PTFE/nylon skids set 0.3 mm *higher* than the wheels** so they only touch under extreme tilt. |
| **2WD + 2 casters** | Acceptable only with large-diameter casters (>20 mm) and hard wheels. Small hard casters chatter on a painted steel plate. |
| **4WD (4 driven wheels)** | **Strongly recommended for a magnetic 3 kg robot.** Doubles the available torque (solving the §2.3 shortfall), removes all caster failure modes, and means a lifted wheel does not cost you drive. Cost: 2 more motors (~$80 with 37Ds), more mass, slightly worse turning. **Most 3 kg magnetic robots that do well are 4WD or 2WD-with-large-wheels.** |
| **Omni / mecanum** | **Wrong for sumo.** Reduced traction in the push direction, fragile rollers, and rollers cannot take 300 N of normal load. |
| **4WD with opposed/side wheels** | Used by some builders to resist being pushed sideways. Adds mass and complexity; only worth it once everything else is done. |

---

## 4. Blades, wedges and body geometry

### 4.1 Commercial blade specifications (real products, real numbers)

From [JSumo Blades & Razors](https://www.jsumo.com/blades-razors). **Note the general guidance on that page: *"A well mounted blade is sharpened at an effective angle (usually between 15 and 25 degrees)"***:

| Product | Dimensions | Thickness | Edge/blade angle | Material | Price |
|---|---|---|---|---|---|
| High Carbon Steel Blade No 1 Black | 200 × 29.9 mm | **3 mm** | **23°** | high carbon steel | $43.50 |
| High Carbon Steel Blade No 2 Black | 200 × 26.3 mm | **1.9 mm** | **23°** | high carbon steel | $41.00 |
| High Carbon Steel Blade No 5 Black | 200 × 24.5 mm | **1.5 mm** | **14.5°** | high carbon steel | $42.50 |
| High Carbon Steel Blade No 6 Black | 200 × 20.9 mm | **1.8 mm** | **14.8°** | high carbon steel | $42.50 |
| Tool Steel Sumo Robot Blade No 1 | 200 × 30.7 mm | **2.85 mm** | **23°** | **tool steel** | $39.95 |
| Tool Steel Sumo Robot Blade No 2 | 200 × 26.5 mm | **1.9 mm** | **23°** | **tool steel** | $38.50 |
| HSS Sumo Robot Blade No 3 | — | — | — | HSS | $39.95 |
| Japan Razor Blade | 200 × 18.4 mm | **0.245 mm** | **23°** | spring steel | $7.25 |
| Japan Razor Blade | 200 × 23.8 mm | **0.38 mm** | **27°** | spring steel | $7.60 |
| Japan Razor Blade | 200 × 17.9 mm | **0.45 mm** | **30°** | spring steel | $7.35 |
| Mini Katana Blade (minisumo) | 100 mm | — | — | with 3M tape | $4.95 |

**Note the shape of the market: the blades cluster at two angles — a shallow group at 14.5–14.8° (the two "Black No 5/6" high-carbon blades) and a dominant group at 23°, with the thin razors running steeper still at 23–30°.** The thick blades are wide (20.9–30.7 mm) and shallow (14.5–23°) — those are the *lifting* wedges. The thin razors are 0.245–0.45 mm and cost $7. **The configuration the sources actually describe is a thin flexible razor lip backed by a stiff thick wedge.**

Supporting guidance from [JSumo's design guide](https://blog.jsumo.com/how-to-make-sumo-robot/): *"Blades should be made from thin spring steel or HSS material. We are using both at our sumo robot projects. **Spring steel gives little flexibility but not very durable. You need to change often.** On the other hand, **HSS gives us extreme rigidness. But also that is little fragile too due to very hard impacts in matchs.**"* and *"While designing robot blade think it as **changeable**. If something happens or if your blade becomes obsolete you need to change quickly. For thin blades we attach with 3M brand or similar strong double sided tapes. And for other thick blades we are using M3 or M2.5 machine screws."*

**Materials comparison** (hardness figures are standard ranges — **UNCONFIRMED against a single citable source**; treat as orientation):

| Material | Hardness | Density | Wedge verdict |
|---|---|---|---|
| **Tool steel (A2 / D2 / O1)** | 58–62 HRC (D2), 60–62 (A2) | 7.7–7.85 g/cm³ | **Best.** Takes and holds a sharp edge, resists galling, will not bend. Brittle at very high hardness — use D2 over O1 if impacts are brutal. |
| **High-carbon steel** | 55–62 HRC | 7.85 | nearly as good, cheaper, tougher |
| **HSS** | 62–67 HRC | 8.0–8.7 | hardest and most wear-resistant, **most brittle** — JSumo calls it "a little fragile" |
| **Spring steel (0.2–0.5 mm)** | 45–50 HRC | 7.85 | flexible lip; **use as the leading 5 mm, not the whole wedge** |
| **Hardened stainless (440C)** | 58–60 HRC | 7.7 | excellent corrosion resistance, good edge |
| **Titanium (Grade 5 / Ti-6Al-4V)** | ~36 HRC | **4.43** | **Wrong for a blade.** Half the mass but it cannot hold a sharp edge, galls against steel, and is 3–5× the cost. *Unconfirmed but widely held* — I found a vendor article explicitly titled ["Why not use titanium for blades"](https://id.haibowellti.com/info/why-not-use-titanium-for-blades-17514956626830336.html). **Use titanium for the *carrier* if you want, never the edge.** |
| **Aluminium (6061 / 7075)** | — | 2.70 | chassis only (7075 for the baseplate). Never a blade. |

**Legal limit:** *"All edges, including but not limited to the front scoop, must not be sharp enough to scratch or damage the ring… In general, edges with a radius of greater than .005" [0.127 mm], as would be obtained with an unsharpened .010" thick metal strip, should be ok."* — [RoboGames Art. 6.8](https://robogames.net/rules/all-sumo.php). **A 0.127 mm edge radius is essentially a sharp blade, so you have a lot of latitude — but a blade that *scratches the ring* can get you DQ'd.**

### 4.2 Wedge geometry — the numbers

| Parameter | Value | Reasoning |
|---|---|---|
| **Main wedge angle** | **14–25°**, with **23° the industry reference point** | every commercial sumo blade is 14.5–30°; 23° dominates the range |
| **Ramp angle if you go steeper** | **45°** | the NEMO 03 (1st place, Robotic Day Prague 2018) uses a 45° "plow" which *"does not work as a push plow, but as a ramp, which aims to undermine the opponent's vehicle pushing against the robot from the front and throwing it off balance or completely pushing it out of the ring"* — an explicitly different strategy |
| **Leading edge thickness** | **0.2–0.5 mm** at the lip, thickening to 1.8–3 mm within 20–30 mm | thin = gets under; thick = survives |
| **Blade ground clearance** | **0.5–1.5 mm**, measured **with the robot loaded and powered** | below ~0.3 mm you risk abrading the paint and being DQ'd (IJMERR 2021); above ~2 mm opponents get under you |
| **Blade mounting** | **floating** — bolted through slotted holes or on a stiffener so the edge can follow dohyo irregularities | a rigidly mounted blade 0.5 mm off a plate that itself bows 0.265 mm (measured in the ABCM FEA) will either scrape or lift |
| **Width** | **full robot width (200 mm in MegaSumo)** | you cannot be flanked by a frontal attack |
| **Contact pressure** | the blade should see a **downward** preload | with magnets near the front, the blade is pressed into the plate, which is exactly what makes it dig |

**How the wedge should sit relative to the opponent's wedge:** the goal is not "lower always wins" — it is **the lower *and stiffer* wedge wins**. Two thin blades meeting edge-to-edge will either pass each other (one rides up the other) or chatter. The design that wins is: **(a)** a lip thin enough to get under, **(b)** backing material immediately behind the lip so the opponent's blade cannot push your lip upward, and **(c)** enough downforce at the front that lifting your blade lifts their whole robot. **Concrete target: ≤0.5 mm lip, ≤1.5 mm ground clearance, ≥2 mm backing thickness within 15 mm of the lip, and magnets directly above/behind the blade.** The IJMERR 2020 paper states the placement principle directly: *"the most vulnerable areas are around the wheels and the plough (front main blade), so it is crucial that most of the magnets are placed in those sections."*

### 4.3 Deflection geometry, matte black, and anti-lift

| Feature | Specification | Why |
|---|---|---|
| **Side panels** | inclined **30–60° from vertical**, chamfered at the top so they are a ramp *in both directions* | an opponent attacking your flank rides up and loses forward force; a square side gives them a flat push face |
| **Rear** | chamfered or rounded | you do not want to give a flat face when you are being pushed out backwards |
| **Matte black surfaces** | sandblast or use matte black anodising / matte black PLA on all outward faces | *Some evidence:* the NEMO 03's own sensor testing found **"dark colours (Black) are detected later than lighter objects (White, Yellow, Red)… black objects were imperceptible to the sensor about 30–40 mm further than white or yellow objects"** ([miniSUMO-JS](https://marcinjablonski.rwbb.pl/wp-content/uploads/2022/03/miniSUMO-JS-en.pdf)). **A matte black robot is literally 30–40 mm harder for a GP2Y0A41SK0F-class IR sensor to see.** This is measured, from a winning robot's design report. **Do it.** Note the same effect also applies against *your* sensors — so your own sensor algorithm must be tuned for dark opponents. |
| **Centre of gravity** | **as low as physically possible; slightly *behind* the blade** | low CG resists tipping under a frontal hit; a CG behind the blade means a lift force on the blade creates a *restoring* moment. The NEMO 03 uses a **4 mm steel base plate** *"as a kind of floor"* specifically to get *"low center of gravity, thanks to which the robot is very resistant to any attempts to disturb the balance and possible overturning caused by the opponent's robot hitting the side."* |
| **Hard to lift** | **concentrate magnet mass at the perimeter and under the front**, keep the mass centroid high enough that the magnets are the lowest point | the magnets are what resist lifting; if the opponent can get a lever under a corner with no magnet nearby, that corner lifts |
| **Hard to flip** | wide track (wheelbase/track ≥ 0.8), low CG, no tall superstructure | `F_flip ∝ m·g·(track/2)/h_CG`. Halving `h_CG` doubles the force needed to roll you. |
| **Avoid being immobilised** | 4 driven wheels; an **anti-lift lip on the rear** angled the wrong way for a rear attack; a **gyro/IMU to detect being rotated** and a scripted escape | the rules give a rematch (not a loss) if the robots orbit for 5 s — but if you are pinned you lose on points. Have a hard-coded "reverse + spin + charge" escape. |
| **Do not fall over** | if a *wheeled* robot falls over, `Yuhkoh` is **not** counted and the match continues ([RoboGames Art. 14.3](https://robogames.net/rules/all-sumo.php)) — so falling over is not instant death, but it is a guaranteed loss of the round in practice. Do not rely on it. |

### 4.4 "Senior"/high-school class techniques and documented trick mechanisms

**This is the one genuinely documented trick mechanism I could find, and it is from a first-place robot:**

> **NEMO 03's "flag" (a decoy / bullfighter's cape).** *"the robot's secret weapon, which was to be a kind of folding 'Cloth for a bull', but in this case the 'bull' would be the enemy's robot. How would that work? The **SG90 modelling servo** placed inside the robot, at the moment of the beginning of the fight, receives an impulse from the plate to **lower the wire with the 'flag' at its end** — the operation would be aimed at **deceiving the opponent's robot, which would mistake the flag for its target**, driving with full force into the thin wire — a piece of paper or other light material. The robot would at best fall out of the ring immediately."*
> — [miniSUMO-JS / NEMO 03 class report, section 3 "Innovations"](https://marcinjablonski.rwbb.pl/wp-content/uploads/2022/03/miniSUMO-JS-en.pdf), with photographs showing the flag in "Fight" mode and "Waiting" mode.

**Why flags work — the actual mechanism.** An IR-reflectance sumo robot does not detect *a robot*; it detects *a reflective surface in its sensor cone*. A light-coloured flag on a thin wire presents **exactly that signature, out at a distance where the opponent commits to a full-speed charge**, while presenting **zero mass and zero pushing surface**. The opponent charges past you, or off the ring. **This is legal under RoboGames rules** (it is not a jamming device, not a thrown object, not a liquid/powder, and it stays attached to the robot — Art. 6.1–6.5). It *may* be illegal under stricter rulebooks that prohibit "devices that deceive the opponent's sensors"; **check your specific rulebook.**

**Other documented mechanisms and the evidence status:**

| Technique | Evidence | Implementation notes |
|---|---|---|
| **Servo-raised / geometry-changing blade** | The NEMO 03 servo precedent proves the mechanism class is used. **No other documented sumo example found — UNCONFIRMED for blades specifically.** | Use a **metal-gear servo (MG996R class, ~10 kg·cm at 6 V, $10.95 at JSumo)** with a **latch or over-centre toggle**, not a direct servo push — the servo must not have to hold against the opponent's force. Better still: a **spring-loaded blade normally down, servo-cocked to raise it**, so the servo is only loaded for the 100 ms of actuation. |
| **Side blades / side arms (dohyo-ken)** | Widely used in Japanese high-school builds; **no citable spec found — UNCONFIRMED.** | Weld/bolt 1.5–2 mm tool-steel plates angled outboard-forward at ~45°, extending to the full 200 mm width. They convert a flank attack into a ride-up. Add a magnet under each one. |
| **Second/backup blade** | Standard practice implied by JSumo's "think of the blade as changeable" | Carry 3 spare blades to every event; a match can be lost to one chipped edge. |
| **Latch/release mechanisms** | **UNCONFIRMED** for sumo specifically. | The RC-combat and combat-robot literature is the right place to research this further. |
| **Anti-lift rear lip** | Common; **UNCONFIRMED** as a documented sumo technique. | A rear plate angled *downwards-outwards* so a rear attack pushes your robot down, not up. |

---

## 5. Sensors and software

### 5.1 Opponent detection — real parts

| Sensor | Range | Output | Update / response | Supply | Notes | Price |
|---|---|---|---|---|---|---|
| **JSumo JS60F** ([page](https://www.jsumo.com/js60f-infrared-sensor-60cm-range-with-background-suspension)) | **60 cm** | **TTL digital** | **0.9 ms** | 3.3–5 V, 10 mA | **±10° sensing angle**; "background suspension" (ignores the dohyo behind the target); 3.5 g; 15.7 × 12.9 × 11.7 mm; reverse-voltage protection; locking connector, 20 cm cable. Vendor: *"volume reductions make integration easier, especially in designs that utilize multiple sensors (such as **5 sensor Mini sumo robot designs**)"*. | **$12.95** |
| **JSumo JS40F** | predecessor | digital | — | 5 V | *"has been used in thousands of robots"*; used by the Senju team? No — Senju used Keyence/Omron. | — |
| **Sharp GP2Y0A41SK0F** | **4–30 cm** | **analog** | fast | 5 V | **Triangulation**, not reflectance — *"Regardless of the color, structure of the object and even its temperature, these sensors are able to detect this object"* (NEMO 03). **BUT** the same source measured that **black objects are detected 30–40 mm later than white/yellow**. | ~$13 |
| **Sharp GP2Y0A21YK0F** | **10–80 cm** | analog | fast | 5 V | *"The sensor of choice"* for the mini-sumo in [Tirian et al. 2015](https://acta.fih.upt.ro/pdf/2015-3/ACTA-2015-3-21.pdf); the paper rates Sharp as *"most suitable… they have a very fast response"* and says **"the ultrasound sensors are not so efficient for sumo, as their response is relatively slow."** | ~$14 |
| **Sharp GP2Y0A02YK0F** | 20–150 cm | analog | fast | 5 V | for a large ring | ~$16 |
| **Keyence PZ-G41N** | — | digital | — | — | used **×5** on Senju (4th, All Japan 2014) for opponent detection | industrial, ~$100+ |
| **Omron E3Z-D62** | — | digital | — | — | used **×2** on Senju | industrial |
| **QTR-1A** | line only | analog | — | 5 V | **used by Senju for white-line detection** (per the builder's own comment reply) | ~$3 |
| **VL53L0X ToF** | 30–2000 mm | I²C | ~30 ms default, ~20–33 ms typical | 2.8–5 V | **Latency is the problem, not range** — see the table in §5.4. At 3 m/s, 30 ms = 90 mm. Usable as a *mid-range* cue, not as your primary trigger. | ~$5 |
| **HC-SR04 ultrasonic** | 2–400 cm | digital pulse | ~10–60 ms round trip; **min range ~20–25 mm** dead zone; 15° cone; acoustic cross-talk between robots | 5 V | **Avoid as primary.** See the Sharp-vs-ultrasonic quote above and the ringing/cross-talk issue. |
| **ACS712 / INA226 current sense** | — | analog / I²C | ACS712 ~5 µs; **INA226 conversion time programmable 140 µs – 8.244 ms** | 5 V / 3.3 V | **Best "opponent locked" detector you can build.** See §5.3. | $2–9 |

### 5.2 Why 5 sensors, and where they go

The 5-sensor frontal array is the standard the *sensor vendor itself* cites for mini-sumo. Concrete geometry for a 200 × 200 mm MegaSumo robot:

```
        ← 200 mm →
   ┌─────────────────────┐
   │  S1   S2   S3   S4  │ S5     S1..S5 on a 180 mm arc,
   │  ↖    ↑    ↑    ↑   │        mounted 5–10 mm behind the blade lip,
   │   \   |    |   /    │        pointing 0°, ±16°, ±32° off-centre
   │    ╲  |    |  ╱     │
   │     ╲ |    | ╱      │        Front pair (S1,S5) at the outer corners
   │      [  CHASSIS  ]  │        so a flanking opponent is seen before
   │                     │        it reaches the side panel.
   └─────────────────────┘
```

* **5 × JS60F at ±10° each**, spaced so the ±10° cones **overlap at 200 mm** (the robot's own width). Two adjacent ±10° sensors mounted 40 mm apart have cones that overlap from ~115 mm outwards — which is *inside* the distance at which you need to commit. **Mount the outer sensors angled ±16–20° mechanically** so their cones tile the full frontal arc.
* **Mount them as far forward as possible** — flush with or 5 mm behind the blade lip. Every 10 mm you move them forward buys you 10 mm of reaction distance.
* **Do not rely on a single centre sensor.** An opponent approaching at 30° off-axis will enter the side cone only.
* **Add 2 rear sensors** (or wide-angle ones) — you will be pushed backwards at some point.

**Alternatives and when to use them:**
* **Phototransistor pairs** (bare IR LED + phototransistor, no modulation) are what a TCRT5000/QRE1113 essentially is. Cheap, fast, but **totally vulnerable to ambient light and to the opponent's emitters**.
* **Laser ToF (VL53L0X/L1X)** — good range and immunity to surface colour, but 20–33 ms latency. Use it as a **second-stage confirmation** at 200–600 mm, not as the trigger.
* **Ultrasonic** — the 15° cone and 20 mm dead zone mean it cannot see an opponent that is already touching you; the round-trip latency means it cannot trigger a charge. **Use only as a long-range "is anything out there" cue in search mode.**
* **Current sensing to detect the push** — see §5.3. This is the highest-value non-IR sensor on the robot.

### 5.3 The "give that juice" tactic and current-based contact detection

**What "give that juice" actually is.** I could not find the phrase in a citable primary source — **UNCONFIRMED as a named tactic.** Based on how it is used in builder communities, it means: **at the instant of contact, command 100% duty (jump from a current-limited cruise duty to full battery voltage across the motors) instead of continuing to modulate.** The engineering content is real and well-founded:

* At cruise you are PWM-limiting to avoid wheelspin and heat. At contact you *want* wheelspin-free maximum force, which means maximum current, which means maximum duty.
* Because `F = k_t·I·ratio/r` and the motors are traction-limited (see §2.4) rather than torque-limited, full duty at contact usually just means the motors draw more current and push harder **with no wheelspin, because the magnets hold you down**. **Downforce is what makes "give that juice" work.** On a wooden dohyo the extra current just spins the wheels.
* The IJMERR 2021 paper describes exactly this effect from the magnet array's perspective: *"The increase in the current flowing through the windings occurs as a result of adding additional resistance from the attraction force of the magnets."*

**How to implement it (concrete):**

```c
// One-line version: cruise at 70% duty, contact at 100%
set_duty( (F_contact_detected) ? 255 : 180 );
```

**Detecting contact without a sensor:** during a push, motor current rises and encoder speed falls. Detect with a **windowed comparator on current** and a **stall check on the encoder**:

```c
// contact when current > threshold AND wheel speed < expected
bool contact = (I_meas > I_contact_thresh) && (rpm_meas < RPM_SEARCH * 0.5f);
```

* With **INA226** you get a digital current reading with a configurable conversion time as low as **140 µs** — fast enough to be a real-time trigger.
* With **VNH5019** you get a built-in current-sense output (CS pin) for free.
* **Estimate:** the current delta at contact is large. A 3 kg robot cruising at 400 N of traction-limited force on a 50 mm wheel needs `T = 400 × 0.025 = 10 N·m` total; at a 24 V 37D's `k_t` this is easily 3–5 A per motor, versus <1 A free-running. A threshold at 2× free-run current gives a reliable edge.
* **Combine with IR**: IR says "something is there", current says "I am actually touching it". Use `IR AND current` to declare `PUSHING`, and `current only` to declare `BLOCKED` (something non-reflective and hard in front of you).

### 5.4 Edge / ring detection

**Dohyo and line specifications** (from [RoboGames Unified Sumo Rules, Art. 3](https://robogames.net/rules/all-sumo.php)):

| Class | Dohyo height | **Diameter** | Material | Shikiri line width × length × separation | **White border width** |
|---|---|---|---|---|---|
| Mega / Humanoid (3 kg) | 5.00 cm | **154.0 cm** | **Polyurethane-coated steel plate** | 2 cm × 20 cm, sep. 20 cm | **5 cm** |
| Mini / Kit | 2.50 cm | 77.0 cm | Laminate/melamine-coated wood | 1 cm × 10 cm, sep. 10 cm | 2.5 cm |
| Micro | 1.25 cm | 38.5 cm | Melamine composite | 0.5 × 5 cm, sep. 5 cm | 1.25 cm |
| Nano | 0.625 cm | 19.25 cm | Melamine composite | 0.25 × 2.5 cm, sep. 2.5 cm | 0.625 cm |

The border is *"a white circular ring… on the outer edge of the playing surface. The ring area extends to the outside edge of this circular line."* The shikiri (start) lines are *"two painted parallel **brown** (or equivalent for absorption of IR light) lines"* — i.e. **the start lines are deliberately IR-dark**, so they read the same as the dohyo interior. **Your edge sensors must distinguish dohyo-interior from white border, and must not be fooled by the brown shikiri lines.**

*Note: the official Fujisoft All Japan dohyo specification PDFs at `fsi.co.jp/sumo/rule/pdf/dohyo.pdf` and `fsi.co.jp/sumo/robot/en/robotsumo-rule-2017.pdf` now return **HTTP 404**; the search index still lists them. If you are entering the All Japan tournament, get the current dohyo spec directly from Fujisoft — **do not assume the RoboGames dimensions apply.** This is a genuine gap in this research.*

**Sensor count and placement:**

| Count | Placement | Comment |
|---|---|---|
| 2 | one at each front corner | minimum; cannot detect a corner-first departure |
| **3** | front-left, front-centre, front-right | **recommended minimum for a 1 kg robot** |
| **5** | as above + two at mid-side, angled 45° outboard | **recommended for 3 kg** — detects a side-first departure during a spin |
| **8** | full ring around the perimeter | belt-and-braces; the delay of sequentially reading 8 analog channels may cost you more than the coverage gains. **Read them in parallel via a mux + fast ADC, or use digital sensors.** |

**Where to place them, geometrically:** the outboard sensor must sit **outboard of the wheel contact patch**, or the wheel will cross the border before the sensor sees it. **Estimate:** at a 3 m/s traverse with a 0.9 ms digital response and a 0.5 ms control loop, total latency ≈ **1.4 ms ⇒ 4.2 mm of travel.** That is negligible. **The real budget is the mechanical offset**, not the electronics. Put the sensor **≤10 mm inboard of the wheel's outer edge and ≤15 mm forward of the wheel centre**, and you will have >100 mm of margin at the ring edge.

**Analog vs digital thresholds:**

| Approach | Pros | Cons | Recommendation |
|---|---|---|---|
| **Digital** (JS60F, comparator with trimpot) | 0.9 ms response; no ADC cost; immune to code latency | threshold is fixed at build time; drifts with ambient light and battery voltage | **Use for edge detection** — but **calibrate at the venue** and add a 3.3 V/5 V supply regulator |
| **Analog + digital threshold** (QTR, raw phototransistor) | calibratable; you can see *how* white the white is | 1 ADC conversion ≈ **~104 µs at 10-bit on a 16 MHz AVR** (13 ADC clocks at 125 kHz) ⇒ reading 5 channels serially is **~520 µs**; oversampling ×4 costs 2 ms | **Use for opponent distance** where you want a gradient; **never serially oversample 8 edge sensors in the main loop** |
| **Synchronous / modulated detection** | kills ambient light and opponent-emitter interference | needs a driver transistor and code | **Do this for your edge sensors** — modulate the emitter at ~10 kHz and read only the AC component |

**Avoiding false positives** (scratches, glare, reflective opponent parts):

1. **Require N consecutive readings** (3 is usually enough; at 1 ms loop time that is 3 ms = 9 mm at 3 m/s).
2. **Two thresholds — hysteresis.** Declare `EDGE` above a high threshold and only clear it below a *lower* threshold.
3. **Multi-sensor voting.** Do not stop for one sensor; require **≥2 of 5** or the two outboard sensors in agreement.
4. **Look at the derivative.** A scratch gives a single-sample spike; a real edge gives a sustained ramp over 5–30 mm.
5. **Auto-calibrate at the start of each round**, on the shikiri line, taking the min and max of each channel over one full spin. This costs 500 ms of a 3-minute match and is the single highest-value calibration you can do.
6. **Subtract ambient**: sample the phototransistor with the emitter **off**, then **on**, and use the difference. This removes venue lighting entirely.
7. **Reflective opponent parts:** an opponent with a polished aluminium wedge will read as "white" to a downward edge sensor only if it is reflected into the sensor's *downward* cone — which requires it to be almost touching you. Use a **10 mm recessed shroud** around each edge sensor so it can only see the floor.
8. **Ambient light subtraction + N-of-M voting** on the *opponent* sensors too: the worst false positive is charging at a reflection off the white border.

### 5.5 IR interference / jamming

**Rule:** *"Jamming devices, such as IR LEDs intended to saturate the opponents IR sensors, are not allowed."* — [RoboGames Art. 6.1](https://robogames.net/rules/all-sumo.php). So deliberate jamming is illegal. **But accidental interference is not.** Two robots each with 5 unmodulated IR emitters are, functionally, jamming each other.

**Mitigations, in order of effectiveness:**

1. **Modulate your emitters at a carrier frequency ~10–40 kHz and detect only that frequency.** This makes your receiver blind to the opponent's DC-ish or differently-modulated emitters, and to ambient light. This is the single most effective technique and it is what a TV remote does.
2. **Time-division:** emit only during a narrow window (e.g. 200 µs) and sample in that window. Two robots doing this will occasionally collide in time; a **pseudo-random slot offset** seeded from the microsecond timer at boot makes sustained collisions unlikely.
3. **Different wavelengths:** many sumo IR sensors use ~880–950 nm. If your event permits, use **~780 nm** emitters with a matched narrow-band filter, or **~1050 nm**, to dodge the crowd.
4. **Narrow your acceptance angle mechanically.** A 10 mm tube around the phototransistor reduces off-axis interference dramatically.
5. **Use a triangulating sensor (Sharp) rather than a reflectance sensor** — the Sharp measures the *position* of the spot, not its intensity, which is why NEMO 03 found it *"unable to cheat them"* and *"regardless of the color, structure of the object and even its temperature"* (with the 30–40 mm black-object caveat).
6. **Use the opponent's emitters as a beacon.** With a narrow-band receiver tuned to the common 940 nm and no emitter of your own, an opponent's IR spill becomes a free direction finder. This is legal (you are receiving, not jamming).

### 5.6 Tactic library — implementable algorithms

**Architecture: a flat state machine with a hard pre-emption for EDGE.**

```c
enum State { BOOT, WAIT_START, SEARCH, TRACK, CHARGE, PUSH, EDGE_ESCAPE, RETREAT, BAIT, STUCK };
uint32_t t_state;              // ms in current state
uint8_t  edge_streak, opp_streak;

void loop_1kHz() {
    // ---- highest priority: never lose the ring ----
    if (edge_confirmed())  { enter(EDGE_ESCAPE); return; }

    switch (state) {
    case SEARCH:  /* see below */      break;
    case TRACK:   /* see below */      break;
    case CHARGE:  /* see below */      break;
    case PUSH:    /* see below */      break;
    case EDGE_ESCAPE: /* see below */  break;
    case RETREAT: /* see below */      break;
    case BAIT:    /* see below */      break;
    case STUCK:   /* see below */      break;
    }
}
```

**1. `SEARCH` — circle search / spin-and-scan** (the documented baseline)

```
Init:       duty_L = +SEARCH_DUTY, duty_R = -SEARCH_DUTY   // spin in place, ~30-40% duty
            (alternate the spin direction every 400 ms to avoid orbiting a fixed point)
Each 20 ms: read the 5 opponent sensors.
Trigger:    if any sensor reads opponent for >= 2 consecutive samples (>= 2 ms):
                record WHICH sensor (left / centre / right)
                -> TRACK
Timeout:    if no detection for 1500 ms -> switch to ZIGZAG (see below)
```
*Rationale (documented):* NEMO 03 — *"when the sensors did not detect any movement, the robot with spins at a moderate speed in the place 'looking' for an opponent, at any moment being ready to give a quick frontal blow."* ([miniSUMO-JS](https://marcinjablonski.rwbb.pl/wp-content/uploads/2022/03/miniSUMO-JS-en.pdf))

**2. `ZIGZAG` — search while covering ground**

```
Init:       drive forward at 60% duty for T_fwd = 250 ms
            then rotate 90 deg (opposite signs, 70% duty) for T_rot = 120 ms
            alternate the rotation sign each cycle
            Repeat. Any opponent detection -> TRACK.
```
*Rationale:* a stationary searching robot can be found and charged; a mobile searcher covers the 154 cm ring in ~800 ms and is harder to target. **Estimate:** at 0.5 m/s a 250 ms forward leg covers 125 mm.

**3. `TRACK` — opponent locking (keep the target centred)**

```
Each 1 ms: read all 5 sensors.
sensor  L    LC    C    RC    R
weight -2   -1    0    +1    +2
error = sum(weight_i * active_i) / sum(active_i)
turn  = Kp * error            // Kp ~ 60-90 duty counts per unit error
duty_L = BASE + turn ;  duty_R = BASE - turn
BASE ramps from 60% to 100% over 150 ms (see CHARGE)
if error == 0 and C active  -> CHARGE
if no sensor active for 30 ms -> SEARCH
```
*This is the "opponent locking" pattern:* the robot does **not** aim at a point, it drives a **null-seeking controller** on the sensor pattern, which is robust to a single sensor failing.

**4. `CHARGE` / `PUSH` — attack and the juice**

```
CHARGE:  duty_L = duty_R = 100%;  a hard 150 ms full-duty sprint toward the opponent.
         (100% duty is safe here because the magnets prevent wheelspin.)
PUSH:    entered when contact is confirmed:
             contact = (I_meas > 2 * I_free)  AND  (rpm_meas < 0.5 * rpm_expected)
         duty = 100% held; disable the edge-escape for the first 120 ms
             (you cannot be pushed out in 120 ms if you are the one pushing)
         if contact lost for > 60 ms:
             if opponent still seen -> CHARGE again
             else                  -> TRACK
         if contact held > 1500 ms with no movement -> STUCK
```
*Estimate for "the first 100–300 ms":* with 30 kgf of downforce and μ = 1.0 you can accelerate at **108 m/s²** (§5.7) — **artificially high**, because it exceeds what the motors can supply. The *real* limit in Design A is `a = F_motor/m = 612 N / 3 kg = 204 m/s²` — also above the traction limit — so **the traction limit of ~108 m/s² governs, and the first 300 ms is entirely a question of whether your duty was already at 100%.** There is no torque-limited acceleration phase. **This is the key insight: on a magnetic dohyo, the whole first 300 ms is won or lost in software, not in the drivetrain.**

**5. `EDGE_ESCAPE` — never lose the ring**

```
Trigger:  edge_streak >= 3 on >= 2 sensors, OR the 2 outboard sensors for >= 2 samples
Action:   reverse BOTH motors at 90% duty for T_esc = 200 ms
          then spin away from the offending side at 70% duty for 150 ms
          then -> SEARCH (or TRACK if the opponent is visible)
Guard:    suppressed for 120 ms after entering PUSH (see above)
Retry:    if EDGE_ESCAPE triggers 3 times within 1 s, go to RETREAT for 600 ms
```
*Rationale (documented):* NEMO 03 — *"the written user program in this case ordered the robot to perform a maneuver to escape from the dangerous place."*

**6. `RETREAT` / "wait and retreat" / defensive**

```
Action:   drive backwards at 50% duty toward the ring centre
          (you know which way is in: it is opposite the last EDGE trigger)
          while still reading opponent sensors
Exit:     after 600 ms, OR on opponent detection -> TRACK
Purpose:  if you are losing the pushing contest, do not lose the ring too.
          Re-engage from a better angle.
```
*Estimate:* a 600 ms retreat at 0.3 m/s moves you 180 mm — enough to get off the border and reset the engagement.

**7. `BAIT` — the flag / decoy**
Use the NEMO 03 mechanism (§4.4). Deploy in `WAIT_START` so the flag is out before the opponent's first charge. The opponent commits to a full-speed charge at the decoy, and you are somewhere else. **Legal under RoboGames; verify against your own rulebook.**

**8. `STUCK` — anti-immobilisation**

```
Trigger:  contact held > 1500 ms AND |rpm| < 5 for > 800 ms
Action:   full reverse 300 ms, then a hard 180-degree spin at 100% for 250 ms,
          then CHARGE.
Repeat:   up to 3 times, then alternate the spin direction.
```
*Estimate:* the rules give a rematch (not a loss) if the robots orbit with no progress for 5 s ([RoboGames Art. 14.5.1](https://robogames.net/rules/all-sumo.php)), so a stuck robot is not immediately dead — but it is losing on the judges' scorecard.

### 5.7 Startup timing and the first 300 ms

**The rules.** RoboGames: *"Autonomous robot operation must begin automatically **no less than five seconds** after being started by the user. **Robots starting before the five second mark forfeit that Yuhkoh point.**"* and *"During these five seconds, players must clear out of the ring area."* ([Art. 5.3, 8](https://robogames.net/rules/all-sumo.php)). The match clock *"shall start ticking five seconds after the start is announced"* (Art. 11). So **you get a known, fixed 5-second arming window.** Use it:

> ⚠️ **Rulebook-dependent — this is the single most dangerous assumption in the startup design.** The RoboGames wording (*"must begin automatically no less than five seconds after being started by the user"*) is a **maximum** delay, and it is a **forfeit condition if you move early**. The Japanese All Japan rules reportedly require the robot **not to move** before the start signal, with a **false-start penalty** — which is the same constraint from the other direction. **Either way: you must not twitch during the arming window, and you must move instantly at the signal.** I could not re-verify the current All Japan wording because the Fujisoft rule PDF now returns HTTP 404. **Read your own event's rulebook and confirm (a) how long the arming window is, (b) what triggers "start", and (c) whether early movement is a forfeit, a warning, or ignored.** A robot that creeps 2 mm during the arming window can lose the round before it starts.

```
t = -5.0 s   Power on. Boot, self-test, gyro zero, sensor auto-calibration
             (spin once on the shikiri line to learn the floor's reflectance).
t = -0.2 s   Blade deployed, flag deployed (if used), duty = 0
t =  0.0 s   START. duty_L = duty_R = 100% within ONE control loop.
t =  0.005 s Motors energised (driver enable + PWM already configured)
t =  0.020 s Motor current at peak; robot at traction-limited acceleration
t =  0.150 s Speed ~1 m/s (if downforce is high); opponent's shikiri line reached
t =  0.300 s Contact or clear miss. State = PUSH or TRACK.
```

**Is that achievable?** **Estimate** the traction-limited acceleration for a 3 kg robot:

| Downforce | μ | Acceleration | Time to 1 m/s | Distance to reach 1 m/s | Time to 3 m/s |
|---|---|---|---|---|---|
| 0 | 0.7 | 6.9 m/s² | **146 ms** | 73 mm | 437 ms |
| 0 | 1.0 | 9.8 m/s² | 102 ms | 51 mm | 306 ms |
| 10 kgf | 0.7 | 29.7 m/s² | 34 ms | 17 mm | 101 ms |
| 10 kgf | 1.0 | 42.5 m/s² | 24 ms | 12 mm | 71 ms |
| **30 kgf** | **1.0** | **107.9 m/s² (11 g)** | **9 ms** | **4.6 mm** | **28 ms** |
| 50 kgf | 1.0 | 173.3 m/s² | 6 ms | 2.9 mm | 17 ms |
| 80 kgf | 1.0 | 271.3 m/s² | 4 ms | 1.8 mm | 11 ms |

**Read that table twice.** With 30 kgf of downforce, the traction-limited time to 1 m/s is **9 ms** and the distance is **4.6 mm**. **The chassis is not the constraint. Your code is.** A 5 ms `delay()`, a `Serial.print`, an `analogRead` of 8 channels, or a 20 ms sensor polling interval **costs you more than the entire acceleration phase**.

**Therefore the winning startup checklist:**
1. **Do not poll sensors in the 0–150 ms window.** Set 100% duty and *hold it* for at least 150 ms before you look at anything except the edge sensors.
2. **Read edge sensors in the 0–150 ms window** — this is the *only* thing that can kill you in that window.
3. **No `delay()` in the main loop, ever.** Use a timer-based scheduler; keep the loop period ≤ 1 ms.
4. **No `Serial.print` in the match loop.** Use an LED or a post-match dump.
5. **Configure PWM and the driver enable before the 5-second mark.** Enabling the driver at t = 0 costs you 1–10 ms.
6. **Use hardware timers / direct port writes for the edge-sensor reads.** An `analogRead()` is ~104 µs; eight of them is 832 µs — 9% of your entire 9 ms acceleration phase. A digital sensor removes this entirely.
7. **Batch: highest-value single change is to replace analog edge sensors with digital ones** (JS60F, 0.9 ms).
8. **Sensor-response budget** (from §5.4, `d = v·t`): at 3 m/s, 1 ms = 3 mm, 10 ms = 30 mm, 20 ms = 60 mm. At 6.5 m/s (Senju's speed), 10 ms = 65 mm and 20 ms = 130 mm. **At Senju speeds, a 20 ms sensor poll means you have already travelled 13 cm past the ring edge before you react.** This is why Japanese robots use industrial digital sensors with sub-millisecond response and why they cost $100+.

**The opening-engagement play (recommended):**
```
t = 0.000  100% duty, both motors forward.  Do NOT look at opponent sensors yet.
t = 0.000  Read only the 2 outboard edge sensors, every 500 us.
t = 0.100  Begin reading the opponent sensors.
t = 0.150  If opponent detected -> CHARGE (already at 100%).
           If not detected       -> keep straight, the opponent started on the
                                    same line and must be within 200 mm ahead.
t = 0.300  If still nothing -> the opponent did not charge; enter SEARCH-spin.
```
**Rationale:** both robots start on shikiri lines 20 cm apart facing each other ([RoboGames Art. 3.2](https://robogames.net/rules/all-sumo.php)). **A straight 100% charge for 300 ms at 30 kgf of downforce cannot be stopped and will make contact.** The only way to lose the opening is to hesitate.

---

## 6. Published winning-design teardowns

### 6.1 Comparison table

| Robot | Team / event | Result | Motors | Ratio | Sensors | Notes | Source |
|---|---|---|---|---|---|---|---|
| **Senju** | H-Tech Robot Team (Istanbul, TR) / **26th All Japan International Robot Sumo, Tokyo, Dec 2014** | **4th** | **2 × Maxon DCX35L 24 V**; custom MOSFET H-bridge | **Custom 4.4:1 gearbox** | **5 × Keyence PZ-G41N** + **2 × Omron E3Z-D62**; **QTR-1A** for white line | **Max speed 6.5 m/s**; aluminium + steel mechanics; custom sharp front blade; **neodymium magnet array with a documented magnet-placement diagram** | [JSumo](https://blog.jsumo.com/senju-4-th-winner-japan-international-robot-sumo-december-2014-26th/) |
| **NEMO 03** | Artur Willchowski & Jan Sobiecki, Technical School Complex, Grudziądz (PL) | **1st, Robotic Day Prague 2018 (minisumo)** | **Pololu 50:1** ("standard motors used in MiniSumo robots") | 50:1 | **Sharp GP2Y0A41SK0F** analog + standard reflection ground sensors | **4 mm steel base plate** for low CG; **45° angled steel "plow" as a ramp** (thickened ~2 mm vs previous gen); cast **modelling silicone** tyres, washed with acetone pre-fight; **7.4 V LiPo**; black PLA FDM body; **SG90 servo-deployed flag decoy** | [miniSUMO-JS report](https://marcinjablonski.rwbb.pl/wp-content/uploads/2022/03/miniSUMO-JS-en.pdf) |
| **Polish MegaSumo research platform** | Białystok University of Technology | Research (IJMERR 2020/2021) | — | — | — | **60 neodymium 5×5×5 N52 magnets in a Halbach array + 2 electromagnets**; measured **846 N / 1334 N** downforce; 3 kg limit; 6 mm Al floor plate; 10 mm steel target | [IJMERR 2021](https://www.ijmerr.com/uploadfile/2021/0624/20210624100758933.pdf), [IJMERR 2020](https://ijmerr.com/uploadfile/2020/0417/20200417064856590.pdf) |
| **ABCM/JMEA "40× weight" design** | UEMA / UFPA (BR) | Conference design study, **never built** | — | — | — | **6 × N42 ring magnets OD40 / ID6 / t10 mm**, 20.94 kgf each ⇒ **125.6 kgf (1232 N) = 41.9× a 3 kg robot's weight**; 6061 aluminium fairing; FEA max deformation **0.2658 mm** | [ABCM CREEM 2014](https://abcm.org.br/app/webroot/anais/creem/2014/Projeto%20de%20M%C3%A1quinas/AN%C3%81LISE%20NUM%C3%89RICA%20DA%20INFLU%C3%8ANCIA%20DE%20%C3%8DM%C3%83S%20DE%20NEOD%C3%8DMIO%20NA%20RELA%C3%87%C3%83O%20INDU%C3%87%C3%83O%20PESO%20EM%20ESTRUTURAS%20DE%20ROB%C3%94S%20DE%20SUM%C3%94.pdf), [JMEA 5 (2015) 197–200](https://pdfs.semanticscholar.org/e1bd/ba9e02226587f4042d5eb018628bcd565206.pdf) |
| **JSumo "Fusion"** | Fırat Dede / JSumo (TR) | vendor build | — | **7.2:1, module 1** (another robot: **5:1, module 0.6**) | — | build-log disclosure of gear modules actually used | [JSumo](https://blog.jsumo.com/how-to-make-sumo-robot/) |
| **JSUMO robot** | Fırat Dede / JSumo (TR) | **2nd, All Japan International Robot Sumo 2013** | **Maxon RE35 24 V** | custom | — | vendor states the RE35 *"is the same model used at our robot JSUMO which won 2.place at All International Robot Sumo 2013"* and is *"popular for lots of Japanese sumo robots too"* | [JSumo RE35 page](https://www.jsumo.com/maxon-re35-dc-motor-24v-model-273752-323890) |
| **Turkish team electromagnet robot** | (unnamed, via IJMERR 2021) | competed | — | — | — | *"The only exception is the UK team of builders, which used an electromagnet instead of permanent magnets… based on a single, large electromagnet, which was turned on at the beginning of the fight and turned off only after its end. However, **the robot constructed in this way moved very slowly around the dohyo and was vulnerable to enemy attacks from the side and the back.**"* | [IJMERR 2021](https://www.ijmerr.com/uploadfile/2021/0624/20210624100758933.pdf) |
| **US sumo capstone** | Northern Arizona University, ME capstone 2017 | student build | **2 × Maxon RE 35, 15 V, $20 each (surplus)** | — | — | cited for the *motor choice* precedent and the surplus-market price point | [NAU Final Report](https://sce.nau.edu/capstone/projects/ME/2017/SumoBotA/Final%20Report.pdf) — **NOTE: I could not extract text from this PDF; the motor/price figures come from the search index snippet and are UNCONFIRMED.** |

### 6.2 Design rules of thumb extracted from published sources

1. **Magnets go under the wheels and the plough.** *"the most vulnerable areas are around the wheels and the plough (front main blade), so it is crucial that most of the magnets are placed in those sections."* — IJMERR 2020.
2. **Halbach beats alternating polarity by 1.65–2.83×** for the same magnet count, and the advantage *grows* with gap. Its cost is assembly difficulty: *"One of the disadvantage of Halbach's array is very difficult arrangement of magnets."* — IJMERR 2020.
3. **100 Halbach magnets ≈ 200 alternating-polarity magnets** (measured peak 1274.8 N vs 1592.8 N — a 318 N / 20% difference) ⇒ **you can delete half your magnet mass and lose 20% of your downforce.** — IJMERR 2020.
4. **Samarium-cobalt is not worth it** despite 250 °C tolerance (high cost); **ceramic needs 18× the volume** for the same force; NdFeB has *"the best value for induction/weight."* — ABCM 2014 / JMEA 2015.
5. **Fix magnets with epoxy, never machine them.** *"Magnets are not machinable materials: the incorrect method for fixing or drilling can oxidize it and affect its magnetic field. The best way to fix it in the robot structure is to use a special glue called professional Araldite."* — ABCM 2014.
6. **Motor power class: 50–150 W, 12–24 V.** *"Between 50-150 watt, 12-15-18-24 Volt motors are suitable."* — JSumo. A Pololu 37D is a ~10 W motor; it is **not** in this class.
7. **Gear ratio: 4:1 to 10:1 if you have a big motor; 50:1+ if you don't.** *"In my opinion between 4:1 to 10:1 is ok for robot projects. You can choose lower ratios for speed and higher ratios of strong pushing force."* — JSumo (referring to add-on gearboxes on Maxon-class motors). NEMO 03 uses 50:1 Pololus. Senju uses 4.4:1 on Maxons.
8. **Gear module 0.6–0.8.** *"Smaller modules have high precision but also have less strength. Big moduled gears have less precision but have more strength… We suggest 0.6 or 0.8 module gears for newer designs."* — JSumo.
9. **Wheels 35–55 mm, hard rubber/urethane, aluminium rims.** — JSumo.
10. **Chassis: 5–6 mm aluminium, 60XX/70XX.** *"You can tap the aluminum quickly. 5-6 mm thickness aluminum is excellent material for chassis… Always try to choose high strength aluminum alloys. 60XX and 70XX series are JSumo's choices."* — JSumo. NEMO 03 went further with a **4 mm steel** base for CG and stiffness.
11. **Build the blade to be replaceable.** — JSumo.
12. **Design for an early version of the same robot.** NEMO 03 is *"a continuation of the series project the 'NEMO' minisumo robot family"* — the winning robot was version 3.
13. **Speed ceiling of a real champion: 6.5 m/s** (Senju, 3 kg, magnets, 4.4:1). **Theoretical ceiling of the Polish research platform: 5–7 m/s.** These agree, and they tell you the practical target band is **1.5–3 m/s for a first build, 5–6.5 m/s for a champion.**

---

## 7. A concrete $500 build plan

### 7.1 Recommended: 3 kg MegaSumo, 4WD, ~$450 (or ~$531 with full sensor fit-out)

| Item | Spec | Qty | Unit | Total | Source |
|---|---|---|---|---|---|
| Motors | **Pololu 37D 24 V 100:1** (#4685, no encoder) | 4 | ~$40 | **$160** | [Pololu](https://www.pololu.com/product/4753) |
| Motor drivers | **BTS7960 / IBT-2** (43 A) | 4 | ~$8 | **$32** | generic |
| Wheels | 50 mm dia × 20 mm, **Shore A 70 cast urethane** on aluminium hubs | 4 | ~$12 | **$48** | JSumo / custom cast |
| Hubs | 6 mm shaft universal aluminium hubs | 4 | ~$6 | **$24** | [Pololu #1083](https://www.pololu.com/product/1083) |
| Magnets | **N52 20×20×5 mm blocks** (18 g, 78.5 N claimed) + **10×5×15 mm blocks** (10 g) | 4 + 6 | $4.50 / $2.50 | **$33** | [JSumo](https://www.jsumo.com/neodymium-magnet-square-block-strong-n52-20mm-x-20mm-x-5-mm) |
| Blade | **Tool Steel Sumo Blade No 1**, 200 × 30.7 × 2.85 mm @ 23° | 1 | $39.95 | **$40** | [JSumo](https://www.jsumo.com/sumo-robot-blade-no1) |
| Spare blades | High-carbon No 5 (1.5 mm, 14.5°) + 2 thin razors | 3 | — | **$25** | JSumo |
| Opponent sensors | **JS60F** (60 cm, digital, 0.9 ms, ±10°) | 5 | $12.95 | **$65** | [JSumo](https://www.jsumo.com/js60f-infrared-sensor-60cm-range-with-background-suspension) |
| Edge sensors | Digital reflectance, 5 down + 2 rear | 7 | ~$2 | **$14** | generic |
| Current sense | **INA226** module (140 µs conversion) | 1 | ~$6 | **$6** | TI |
| MCU | Arduino Nano / STM32 "Blue Pill" | 1 | ~$6 | **$6** | — |
| Battery | **4S LiPo 1000 mAh 45C** (14.8 V nom / 16.8 V full) | 1 | ~$18 | **$18** | — |
| Chassis | 7075 aluminium plate, 6 mm, cut and drilled | — | — | **$40** | local |
| Fasteners / epoxy / misc | M3, Araldite, PTFE skid tape | — | — | **$20** | — |
| | | | | **≈ $531** | *sub-total; see trims below to land at $450* |

**Trims to land under $500** (in order of least pain — none of these cost you a match):
* Spare blades: buy **1** spare instead of 3 → **−$17**
* Opponent sensors: **3** instead of 5 for your first build; add the outer pair in Month 4 → **−$26**
* Wheels: cast your own in Shore A 70 urethane from a 3D-printed mould instead of buying → **−$25**
* Chassis: use 6 mm **6061** instead of 7075 → **−$15**
* **Total saved ≈ $83 ⇒ ≈ $448**

**Predicted performance (estimate):**
* Speed: `100 rpm × π × 0.050 / 60` = **0.26 m/s** in 100:1; swap to 50:1 gearboxes for **0.52 m/s** (2 sets of gearboxes ≈ +$80 — *the single best upgrade*).
* Wheel torque: `3.825 N·m × 4 = 15.3 N·m` total ⇒ `F = 15.3/0.025 = **612 N**` of drive force available.
* Magnet array: 4 × 18 g + 6 × 10 g = **132 g of N52** ⇒ at **6–10 N/g** that is **790–1320 N (81–135 kgf)** of downforce. **This is more than you want.** Halve it: 2 blocks + 4 thin = **76 g** ⇒ **456–760 N (46–77 kgf)**. Still enormous. **Start with ~40–60 g and add more only if you measure a traction problem.**
* Traction with 50 kgf downforce at μ=1.0: `1.0 × (29.4 + 490) = **520 N**`. Drive force available 612 N ⇒ **traction-limited**. Correct.

### 7.2 If you can exceed $500: the two upgrades that matter

1. **JSumo Symtec Q (2 × $94.50 = $189)** instead of 4 × 37D. Gives **4.31 N·m and 1450 rpm** per motor at 12 V (172.6 N of pull each at 50 mm, **3.80 m/s**). *Verify the October 2026 shipping date before ordering.*
2. **Upgrade the wheels to 75–90 mm** once you have Symtec/Maxon-class motors. `v` goes to 5.7–6.8 m/s and you match the measured Senju configuration.

### 7.3 6-month schedule

| Month | Milestone | Pass criterion |
|---|---|---|
| 1 | **Measure your magnets.** Buy 4 magnets + a $10 kitchen scale + a 3 mm steel plate. Build the gap-vs-force curve yourself. Order the rest. | You have your own N/g number and your own gap table. |
| 2 | **Chassis + drivetrain bench test.** 4WD running, no magnets. Measure free-run current, stall current, top speed. | Speed within 20% of the §2.2 prediction; stall current < driver rating × 0.5 |
| 3 | **First magnet array on the robot.** Measure tractive force with a spring scale against a wall. Verify the downforce by weighing the robot on a scale with a steel plate under it. | Measured downforce within 30% of your Month-1 prediction |
| 4 | **Sensors and state machine.** All 8 states implemented, 1 kHz loop, no `delay()` anywhere. | Loop period ≤ 1 ms measured with an oscilloscope or a pin toggle; edge escape works 100/100 trials |
| 5 | **Combat testing.** 200+ practice rounds. Tune duty thresholds, contact-current threshold, Kp of the tracker. | Win rate > 70% against your own B-team robot |
| 6 | **Reliability + spares.** 2 complete spare drivetrains, 3 spare blades, 2 spare batteries, spare sensors. | Robot survives 30 consecutive rounds without a mechanical failure |

---

## 8. What I could not confirm — an explicit gap list

Do not let these become fabricated numbers downstream.

| Claim | Status |
|---|---|
| Coefficient of friction, rubber/urethane/silicone on a **polyurethane-coated steel dohyo** | **UNCONFIRMED.** No sumo-specific measurement found. Used μ = 0.7 and 1.0 as bounds. **Measure it yourself.** |
| Shore A recommendation specifically for **magnetic** arenas | **UNCONFIRMED.** JSumo says "hard rubber or polyurethane" without a hardness number. My 60–80 Shore A recommendation is *engineering reasoning*, not a citation. |
| Exact mass of Pololu 37D gearmotors | **UNCONFIRMED** (~200 g estimated from the category). |
| Stall torque / current of generic Chinese 37GB-family motors | **UNCONFIRMED.** Marketplace figures are rated, not stall. |
| N20/N30 gearmotors for a 1 kg magnetic robot | **UNCONFIRMED** and probably inadequate. |
| Current official **All Japan (Fujisoft) dohyo specification** | **UNCONFIRMED — the PDFs at `fsi.co.jp/sumo/rule/pdf/dohyo.pdf` and `fsi.co.jp/sumo/robot/en/robotsumo-rule-2017.pdf` now return HTTP 404.** RoboGames dimensions are used as a proxy. **If you enter All Japan, get the spec from Fujisoft directly.** |
| The phrase **"give that juice"** as a documented named tactic | **UNCONFIRMED as a term.** The underlying technique (full duty at contact) is well-supported and is implemented in §5.6. |
| **Servo-raised blade** / latch mechanisms in sumo specifically | **UNCONFIRMED.** The NEMO 03 flag-on-servo proves the actuator class; no blade-raising sumo example found. |
| **Side blades / dohyo-ken** with concrete dimensions | **UNCONFIRMED.** Widely discussed, no citable spec found. |
| Titanium being unsuitable for blades | Standard engineering consensus, but the only source found is a **vendor marketing article** ([haibowellti](https://id.haibowellti.com/info/why-not-use-titanium-for-blades-17514956626830336.html)). Treat as *likely true, weakly sourced*. |
| Material hardness values (HRC) for tool steel / HSS / 440C | Standard reference ranges — **not sourced to a single citation** in this report. |
| The NAU capstone report's Maxon RE35 purchase at $20 each | From a **search-index snippet**; the PDF was not text-extractable. **UNCONFIRMED** — but it does suggest **surplus Maxon motors are the cheapest path to a 100 W+ drivetrain**, which is worth 30 minutes of eBay searching. |
| The 100-magnet alternating-polarity simulation values in IJMERR 2020 Table III | **Suspected copy-paste error** (identical to the 200-magnet column). Use the experimental peak values instead. |

---

## 9. One-page summary

**Magnets.** Two equations govern everything: `B_gap = Br·(t/g)/((t/g)+1)` and `F = B²A/(2μ0)`. N52's `Br` is only ~11% above N42's, so **the gap dominates**. Measured arrays deliver **5–15 N per gram of N52** depending on gap; design at **8–10 N/g** with a **0.3–0.5 mm** gap. A **Halbach** layout gives **1.65–2.83×** the force of alternating polarity for identical magnets — measured. **100 Halbach magnets ≈ 200 alternating-polarity magnets.** Measured real-robot downforce: **846 N (86 kgf) from 60 magnets totalling 56 g** on a 3 kg robot. Put magnets **under the wheels and the front plough**. **Rectangular blocks beat discs** on packing density, `B` uniformity, and the ability to run a continuous magnet line under a 200 mm blade. Cap your force by the **steel's 1.6 T saturation** (1.0 N/mm²). And remember: **only 0.3 mm of extra gap costs you 10% of your downforce, so a soft tyre is a self-defeating magnet part.**

**Drivetrain.** With 30 kgf of downforce a 3 kg robot with 50 mm wheels needs **82.5 kg·cm per wheel** to use all its grip. A Pololu 37D gives **34 kg·cm extrapolated, 10 kg·cm continuous**. **No 37D can exploit 30 kgf.** Either use 4WD of 37Ds with ~10 kgf of downforce, or move to **JSumo Symtec Q (44 kg·cm tested, 1450 rpm, 12–24 V, $94.50)** or **Maxon DCX35L (2.03 N·m stall, 7720 rpm, 385 g, CHF 332)**. The Japanese recipe is a **very large motor with a very low ratio (4.4:1 measured on the 4th-place Senju) and 75–90 mm wheels**, producing **6.5 m/s**. Drivers: **BTS7960 (43 A, ~$8)** or **Pololu G2 / VNH5019**; **never an L298N (2 A, 1.4–3.2 V drop)** or **DRV8871 (3.6 A)**. **Overvolting doubles speed and torque and quadruples heat** — JSumo explicitly recommends it for the Maxon RE35 and states the Symtec Q "handles overvoltaging good"; but their own instrumented test of a 12 V Maxon RE40 at 16.8 V reached only **7 A / 105 W against a 105 A / 150 W rating**, proving real robots are **traction- and time-limited, not motor-limited**.

**Wheels.** Hard rubber or cast urethane (Shore A ~60–80) on aluminium rims, **50–60 mm** for a 3 kg robot, **30–40 mm** for 1 kg. **4WD.** Soft silicone is for painted, low-downforce arenas — on a magnetic dohyo, a squishy tyre throws off your air gap and costs you the very downforce that makes it grip. Wash tyres with acetone before every round.

**Blades and geometry.** Every commercial sumo blade is **14.5–30° with 23° dominant**; tool steel or high-carbon at **1.8–3 mm**, edge **0.5–1.5 mm off the plate (measured loaded)**, mounted **floating** on a stiffener, full 200 mm width. Matte black surfaces are **measurably 30–40 mm harder for IR sensors to see** (NEMO 03 measurement). **Low CG, 4 mm steel or 6 mm 7075 baseplate, perimeter magnet placement, wide track.** The one documented trick mechanism is the **NEMO 03 servo-deployed flag decoy**, which exploits the fact that IR sensors detect *reflectivity*, not *robots*.

**Sensors and software.** **5 × JS60F (60 cm, digital, 0.9 ms, ±10°, $12.95)** across the front, **5–7 edge sensors**, plus **current sensing (INA226, 140 µs) to confirm contact**. Modulate your emitters to defeat IR cross-talk; deliberate jamming is illegal. Implement 8 states with **edge escape as a hard pre-emption**. **The decisive fact: with 30 kgf of downforce, traction-limited acceleration is 108 m/s² — 0 to 1 m/s in 9 ms and 4.6 mm.** The chassis is not the constraint; **your code is.** No `delay()`, no `Serial.print`, no 20 ms polling. **Hold 100% duty for the first 150 ms and read only the edge sensors.**

**The single highest-value thing you can do this month:** buy four magnets, a kitchen scale, and a 3 mm steel plate, and **measure your own force-vs-gap curve.** It costs $30, takes an afternoon, and replaces every estimate in §1 with your own data.

---

### Source index

Primary / peer-reviewed:
[Łapińska et al., IJMERR 9(5) 2020, "Research of Various Magnetic Systems Used in Autonomous MegaSumo Robots"](https://ijmerr.com/uploadfile/2020/0417/20200417064856590.pdf) ·
[Dziubek et al., IJMERR 10(6) 2021, "Research of Hybrid Magnetic System Used in Autonomous MegaSumo Robots"](https://www.ijmerr.com/uploadfile/2021/0624/20210624100758933.pdf) ·
[Soares/Mendes/Tavares et al., ABCM CREEM 2014 (Portuguese)](https://abcm.org.br/app/webroot/anais/creem/2014/Projeto%20de%20M%C3%A1quinas/AN%C3%81LISE%20NUM%C3%89RICA%20DA%20INFLU%C3%8ANCIA%20DE%20%C3%8DM%C3%83S%20DE%20NEOD%C3%8DMIO%20NA%20RELA%C3%87%C3%83O%20INDU%C3%87%C3%83O%20PESO%20EM%20ESTRUTURAS%20DE%20ROB%C3%94S%20DE%20SUM%C3%94.pdf) ·
[Mendes et al., J. Mechanics Engineering and Automation 5 (2015) 197–200 (English version)](https://pdfs.semanticscholar.org/e1bd/ba9e02226587f4042d5eb018628bcd565206.pdf) ·
[Tirian et al., Acta Tehnica Corviniensis VIII(3) 2015](https://acta.fih.upt.ro/pdf/2015-3/ACTA-2015-3-21.pdf)

Rules:
[RoboGames Unified Sumo Robot Rules](https://robogames.net/rules/all-sumo.php) · All Japan / Fujisoft dohyo & rules PDFs — **now 404, contact Fujisoft directly**

Datasheets & vendor pages:
[Pololu 37D gearmotors](https://www.pololu.com/product/4753) · [Pololu VNH5019 carrier](https://www.pololu.com/product/1451) · [maxon DCX 35 L](https://www.maxongroup.co.kr/maxon/view/product/motor/dcmotor/DCX/DCX35/DCX35L01GBKL511) · [JSumo Maxon RE35 24 V](https://www.jsumo.com/maxon-re35-dc-motor-24v-model-273752-323890) · [JSumo Symtec Q](https://www.jsumo.com/symtec-q-gear-motor-12v-1450rpm) · [JSumo Titan 1000 rpm](https://www.jsumo.com/jsumo-titan-dc-gearhead-motor-12v-1000-rpm-hp) · [JSumo Blades & Razors](https://www.jsumo.com/blades-razors) · [JSumo JS60F](https://www.jsumo.com/js60f-infrared-sensor-60cm-range-with-background-suspension) · [JSumo N52 20×20×5](https://www.jsumo.com/neodymium-magnet-square-block-strong-n52-20mm-x-20mm-x-5-mm) · [JSumo N52 10×5×15](https://www.jsumo.com/neodymium-magnet-block-strong-n52-10mm-x-5mm-x-15-mm)

Design guides & build logs:
[JSumo, "How to Make a Good Sumo Robot"](https://blog.jsumo.com/how-to-make-sumo-robot/) · [JSumo, "Maxon Motor Graph"](https://blog.jsumo.com/maxon-motor-graph/) · [JSumo, Senju (4th, All Japan 2014)](https://blog.jsumo.com/senju-4-th-winner-japan-international-robot-sumo-december-2014-26th/) · [Sobiecki & Willchowski, "NEMO 03" miniSUMO class report (1st, Prague 2018)](https://marcinjablonski.rwbb.pl/wp-content/uploads/2022/03/miniSUMO-JS-en.pdf) · [NovaSolver neodymium air-gap simulator & theory](https://novasolver.jp/en/tools/magnet-strength-neodymium-air-gap.html) · [K&J Magnetics gap calculator](https://www.kjmagnetics.com/magnet-gap-calculator.asp) · [supermagnete FAQ: magnet coating chipping](https://www.supermagnete.it/eng/faq/Why-does-the-coating-of-my-magnets-chip) · [First4Magnets: protecting magnets from chipping](https://www.first4magnets.com/blog/how-to-protect-magnets-from-chipping/)
