// ============================================================================
//  08 — Кріплення серво SG90 для розкладних бокових клинів
//  Правила дозволяють змінювати габарит після старту, тож серво
//  викидає бокові клини за ~100–150 мс після сигналу.
// ============================================================================

include <params.scad>

BRACKET_T   = 5;
SERVO_CLEAR = 0.4;

module servo_mount() {
    W = SERVO_L + 14;
    H = SERVO_W + 14;

    difference() {
        union() {
            // основна площина
            cube([W, H, BRACKET_T], center = true);

            // два вушка під гвинти серво (SG90 кріпиться за вушка)
            for (sx = [-1, 1])
                translate([sx * (SERVO_L/2 + 3), 0, BRACKET_T/2])
                    cube([8, SERVO_W + 8, BRACKET_T + 2], center = true);
        }

        // кишеня під корпус серво
        translate([0, 0, BRACKET_T/2 + 2])
            cube([SERVO_L + SERVO_CLEAR, SERVO_W + SERVO_CLEAR,
                  BRACKET_T + 24], center = true);

        // проріз під качалку
        translate([SERVO_L/2 - 4, 0, BRACKET_T/2 + 8])
            rotate([0, 90, 0])
                cylinder(d = 8, h = 20, center = true);

        // отвори кріплення до основи
        for (sx = [-1, 1], sy = [-1, 1])
            translate([sx * (W/2 - 5), sy * (H/2 - 5), -EPS])
                cylinder(d = M3_CLEAR, h = BRACKET_T + 2*EPS);

        // виріз під кабель серво
        translate([-W/2, 0, BRACKET_T/2])
            cube([10, 10, BRACKET_T + 4], center = true);
    }
}

servo_mount();
