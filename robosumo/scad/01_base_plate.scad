// ============================================================================
//  01 — Основа (шасі) 200 x 200 мм
//  Друкований прототип. Бойова версія — той самий контур з алюмінію 4 мм.
//
//  Що є: пази під колеса, отвори моторів 37D на шестикутнику 15,5 мм,
//         монтажна сітка M3 під електроніку, кабельні проходи.
// ============================================================================

include <params.scad>

module base_plate() {
    difference() {
        union() {
            // основна плита
            rounded_plate(CHASSIS_W, CHASSIS_L, PLATE_T, 12);
        }

        // --- пази під колеса: колесо виступає за корпус на 2–3 мм ---
        for (sx = [-1, 1], sy = [-1, 1])
            translate([sx * WHEEL_TRACK/2, sy * WHEELBASE/2, -EPS])
                linear_extrude(height = PLATE_T + 2*EPS)
                    offset(r = 2) offset(delta = -2)
                        square([WHEEL_W + 6, WHEEL_D + 6], center = true);

        // --- посадкові місця моторів: кишеня + отвори кріплення ---
        for (sx = [-1, 1], sy = [-1, 1])
            translate([sx * WHEEL_TRACK/2, sy * WHEELBASE/2, 0]) {
                translate([0, 0, PLATE_T])
                    motor_body_pocket(2.5);
                motor_mount_holes(PLATE_T + 6);
            }

        // --- монтажна сітка M3 під плати ---
        // крок 40 мм дає багато варіантів розміщення без свердління
        for (x = [-60 : 40 : 60], y = [-40 : 40 : 40])
            translate([x, y, -EPS])
                cylinder(d = M3_CLEAR, h = PLATE_T + 2*EPS);

        // --- кабельні проходи ---
        for (x = [-45, 45])
            translate([x, -70, -EPS])
                cylinder(d = 8, h = PLATE_T + 2*EPS);
        translate([0, 55, -EPS])
            cylinder(d = 12, h = PLATE_T + 2*EPS);

        // --- полегшення: кишені знизу, щоб зняти масу й дати доступ повітрю ---
        // (не наскрізні — залишаємо 2 мм м'яса)
        for (x = [-30, 30], y = [-15, 15])
            translate([x, y, -EPS])
                linear_extrude(height = PLATE_T - 2)
                    offset(r = 4) offset(delta = -4)
                        square([34, 20], center = true);
    }
}

base_plate();
