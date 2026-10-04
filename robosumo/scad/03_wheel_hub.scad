// ============================================================================
//  03 — Маточина колеса Ø50 на вал 6 мм (D-подібний)
//  З'єднує вал мотора 37D з колесом. Шість гвинтів M3 по колу 30 мм.
// ============================================================================

include <params.scad>

HUB_D       = WHEEL_D - 2;      // трохи менше колеса
HUB_T       = 8;
HUB_BOLT_PCD = 30;              // коло болтів колеса
HUB_BOLTS   = 6;
D_FLAT      = 0.5;              // лиска на валу (D-подібний профіль)

module wheel_hub() {
    difference() {
        // тіло маточини
        cylinder(d = HUB_D, h = HUB_T);

        // центральний отвір під вал 6 мм з лискою
        difference() {
            cylinder(d = MOTOR_SHAFT_D + 0.15, h = HUB_T + 2*EPS, center = true);
            // зрізаємо лиску з одного боку
            translate([MOTOR_SHAFT_D/2 - D_FLAT, 0, 0])
                cube([MOTOR_SHAFT_D, MOTOR_SHAFT_D + 2, HUB_T + 4], center = true);
        }

        // отвори під гвинти колеса
        bolt_circle(HUB_BOLT_PCD, HUB_BOLTS, M3_CLEAR, HUB_T + 4);

        // полегшення: шість кишень між болтами
        for (i = [0 : HUB_BOLTS-1])
            rotate([0, 0, i * 360 / HUB_BOLTS + 30])
                translate([HUB_BOLT_PCD/2, 0, -EPS])
                    hull() {
                        translate([-4, 0, 0]) cylinder(d = 6, h = HUB_T - 3 + EPS);
                        translate([ 4, 0, 0]) cylinder(d = 6, h = HUB_T - 3 + EPS);
                    }

        // фаска під ступицю, щоб колесо сідало без перекосу
        translate([0, 0, HUB_T])
            cylinder(d1 = HUB_D + 2, d2 = HUB_D - 4, h = 1.2);
    }
}

wheel_hub();
