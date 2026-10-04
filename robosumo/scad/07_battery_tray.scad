// ============================================================================
//  07 — Ложемент 6S LiPo
//  Тримає пак так, щоб він не зсувався під ударом. Знизу — зазор для
//  ременя, зверху відкрито для заміни за секунди.
// ============================================================================

include <params.scad>

TRAY_WALL   = 5;
TRAY_T      = 5;
STRAP_W     = 20;       // ширина липучки-ременя

module battery_tray() {
    W = LIP_W + 2 * TRAY_WALL;
    L = LIP_L + 2 * TRAY_WALL;

    difference() {
        union() {
            // днище
            cube([W, L, TRAY_T], center = true);

            // дві бокові стінки вздовж довгої осі
            for (sx = [-1, 1])
                translate([sx * (W/2 - TRAY_WALL/2), 0, LIP_H/2])
                    cube([TRAY_WALL, L, LIP_H], center = true);

            // торцеві стінки
            for (sy = [-1, 1])
                translate([0, sy * (L/2 - TRAY_WALL/2), LIP_H/2])
                    cube([W, TRAY_WALL, LIP_H], center = true);
        }

        // кишеня під пак
        translate([0, 0, TRAY_T])
            cube([LIP_W + 0.6, LIP_L + 0.6, LIP_H + 2], center = true);

        // пази під ремінь — два, щоб пак не гойдався
        for (y = [-L/4, L/4])
            translate([0, y, -EPS])
                cube([W + 4, STRAP_W, TRAY_T + 2*EPS], center = true);

        // отвори кріплення до основи
        for (y = [-L/2 + 8, L/2 - 8], x = [-W/2 + 6, W/2 - 6])
            translate([x, y, -EPS])
                cylinder(d = M3_CLEAR, h = TRAY_T + 2*EPS);

        // вирізи для силових проводів і балансирного роз'єму
        translate([0, -L/2 + TRAY_WALL/2, LIP_H * 0.6])
            cube([16, TRAY_WALL + 4, 12], center = true);
        translate([W/2 - TRAY_WALL/2, L/3, LIP_H * 0.5])
            cube([TRAY_WALL + 4, 14, 10], center = true);
    }
}

battery_tray();
