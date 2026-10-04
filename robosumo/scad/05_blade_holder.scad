// ============================================================================
//  05 — Тримач клина
//  Тримає сталевий клин 3 мм під кутом 12° до підлоги.
//  Клин — головна зброя: він має заходити ПІД клин суперника.
// ============================================================================

include <params.scad>

HOLDER_W    = BLADE_W - 10;
HOLDER_H    = 30;
HOLDER_T    = 8;
SLOT_CLEAR  = 0.4;      // зазор під клин 3 мм

module blade_holder() {
    difference() {
        // корпус з нахилом під кутом клина; низ сидить на плиті (z = 0)
        translate([0, 0, HOLDER_H/2])
            rotate([-BLADE_ANGLE, 0, 0])
                cube([HOLDER_W, HOLDER_T, HOLDER_H], center = true);

        // паз під клин — той самий нахил, тож клин лягає в паз площиною
        translate([0, 0, HOLDER_H/2 + 3])
            rotate([-BLADE_ANGLE, 0, 0])
                cube([HOLDER_W - 20, BLADE_T + SLOT_CLEAR, HOLDER_H + 10],
                     center = true);

        // гвинти фіксації клина
        for (i = [0 : BLADE_SCREWS-1]) {
            x = -HOLDER_W/2 + 18
                + i * (HOLDER_W - 36) / max(1, BLADE_SCREWS - 1);
            translate([x, 0, HOLDER_H/2 - 6])
                rotate([-BLADE_ANGLE, 0, 0])
                    rotate([90, 0, 0])
                        cylinder(d = M3_CLEAR, h = HOLDER_T + 12, center = true);
        }

        // кріплення до основи: два отвори M3
        for (sx = [-1, 1])
            translate([sx * (HOLDER_W/2 - 15), -HOLDER_T/2 - 2, -EPS])
                cylinder(d = M3_CLEAR, h = HOLDER_H + 2*EPS);

        // полегшення знизу
        translate([0, -HOLDER_T/2 - 1, -EPS])
            linear_extrude(height = HOLDER_H * 0.45)
                offset(r = 3) offset(delta = -3)
                    square([HOLDER_W - 30, HOLDER_T - 1], center = true);
    }
}

blade_holder();
