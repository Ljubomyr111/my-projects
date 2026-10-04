// ============================================================================
//  02 — Хомут мотора 37D
//  Притискає корпус редуктора до основи. Ставиться зверху мотора.
// ============================================================================

include <params.scad>

CLAMP_WALL  = 5;
CLAMP_T     = 6;
CLAMP_LIP   = 3;    // наскільки хомут заходить на корпус

module motor_clamp() {
    difference() {
        // плита з отвором під корпус мотора
        hull() {
            translate([-MOTOR_BODY_D/2 - CLAMP_WALL, 0, 0])
                cylinder(d = CLAMP_WALL*2, h = CLAMP_T);
            translate([ MOTOR_BODY_D/2 + CLAMP_WALL, 0, 0])
                cylinder(d = CLAMP_WALL*2, h = CLAMP_T);
        }

        // посадкове місце корпусу мотора (з зазором 0.3 мм)
        translate([0, 0, -EPS])
            cylinder(d = MOTOR_BODY_D + 0.6, h = CLAMP_T + 2*EPS);

        // два гвинти M3 у площину основи, рознесені як суміжні отвори мотора
        for (sx = [-1, 1])
            translate([sx * MOTOR_HEX_PITCH/2,
                       MOTOR_BODY_D/2 + CLAMP_WALL, -EPS])
                cylinder(d = M3_CLEAR, h = CLAMP_T + 2*EPS);

        // фаски під головки гвинтів
        for (sx = [-1, 1])
            translate([sx * MOTOR_HEX_PITCH/2,
                       MOTOR_BODY_D/2 + CLAMP_WALL, CLAMP_T])
                cylinder(d1 = M3_CLEAR, d2 = 6.4, h = 1.6);
    }

    // два «вуха», що тримають мотор від осьового зсуву
    for (sx = [-1, 1])
        translate([sx * (MOTOR_BODY_D/2 + CLAMP_WALL/2), 0, CLAMP_T - 1])
            difference() {
                cylinder(d = CLAMP_WALL, h = 3);
                translate([0, 0, -EPS])
                    cylinder(d = MOTOR_BODY_D + 0.6, h = 3 + 2*EPS);
            }
}

motor_clamp();
