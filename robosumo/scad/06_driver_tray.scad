// ============================================================================
//  06 — Ложемент 4 x BTS7960
//  Матч триває «до вибиття», тобто без ліміту часу — драйвери гріються
//  безперервно. Тому під кожною платою продув і отвори під стійки.
// ============================================================================

include <params.scad>

TRAY_WALL   = 4;
TRAY_GAP    = 4;        // просвіт між платами для повітря
TRAY_T      = 4;

module driver_tray() {
    cols = 2;
    rows = 2;
    W = cols * BTS_W + (cols + 1) * TRAY_GAP + 2 * TRAY_WALL;
    H = rows * BTS_L + (rows + 1) * TRAY_GAP + 2 * TRAY_WALL;

    difference() {
        cube([W, H, TRAY_T], center = true);

        for (c = [0 : cols-1], r = [0 : rows-1]) {
            cx = -W/2 + TRAY_WALL + TRAY_GAP + BTS_W/2 + c * (BTS_W + TRAY_GAP);
            cy = -H/2 + TRAY_WALL + TRAY_GAP + BTS_L/2 + r * (BTS_L + TRAY_GAP);

            // продув під платою
            translate([cx, cy, -TRAY_T])
                linear_extrude(height = TRAY_T + 2*EPS)
                    offset(r = 2) offset(delta = -2)
                        square([BTS_W * 0.65, BTS_L * 0.65], center = true);

            // отвори під стійки плати
            for (dy = [-BTS_HOLE_DY/2, BTS_HOLE_DY/2],
                 dx = [-BTS_HOLE_DX/2, BTS_HOLE_DX/2])
                translate([cx + dx, cy + dy, -TRAY_T])
                    cylinder(d = M3_CLEAR, h = TRAY_T + 2*EPS);
        }

        // кабельні вирізи між колонками
        translate([0, 0, -TRAY_T])
            cube([TRAY_GAP + 2, H - 2*TRAY_WALL, TRAY_T + 2*EPS], center = true);

        // два кріплення до основи
        for (sx = [-1, 1])
            translate([sx * (W/2 - 5), 0, -TRAY_T])
                cylinder(d = M3_CLEAR, h = TRAY_T + 2*EPS);
    }

    // стійки під вентилятор 40 мм по кутах
    for (sx = [-1, 1], sy = [-1, 1])
        translate([sx * (W/2 - 5), sy * (H/2 - 5), 0])
            difference() {
                cylinder(d = 7, h = TRAY_T + 6);
                translate([0, 0, -EPS])
                    cylinder(d = M3_CLEAR, h = TRAY_T + 8);
            }
}

driver_tray();
