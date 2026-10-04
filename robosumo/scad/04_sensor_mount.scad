// ============================================================================
//  04 — Кріплення QTR-8A на планці клина
//  Тримає сенсорну планку на висоті 1.5–2 мм над ареною — це критично,
//  бо кожен міліметр кліренсу краде притискну силу магнітів.
// ============================================================================

include <params.scad>

MOUNT_T     = 4;
MOUNT_SLOT  = 4.2;      // паз, щоб регулювати висоту після складання
SENSOR_GAP  = 1.75;     // робоча висота сенсорів над підлогою

module sensor_mount() {
    W = QTR_L + 14;
    H = 22;

    difference() {
        union() {
            // площина кріплення сенсора
            translate([0, 0, 0])
                cube([W, H, MOUNT_T], center = true);

            // вертикальна стійка з пазом під регулювання висоти
            translate([0, H/2 - 3, MOUNT_T/2])
                cube([26, 6, 34], center = true);
        }

        // отвори під сенсорну планку
        for (dy = [-QTR_HOLE_DY/2, QTR_HOLE_DY/2],
             dx = [-QTR_HOLE_DX/2, QTR_HOLE_DX/2])
            translate([dx, dy, -MOUNT_T])
                cylinder(d = M2_CLEAR, h = MOUNT_T + 2*EPS + 1);

        // паз регулювання висоти в стійці
        translate([0, H/2 - 3, MOUNT_T/2 + 5])
            hull() {
                translate([0, 0, -12]) rotate([90, 0, 0])
                    cylinder(d = MOUNT_SLOT, h = 10, center = true);
                translate([0, 0,  12]) rotate([90, 0, 0])
                    cylinder(d = MOUNT_SLOT, h = 10, center = true);
            }

        // болт кріплення до основи
        translate([0, H/2 - 3, MOUNT_T/2 + 14])
            rotate([90, 0, 0])
                cylinder(d = M3_CLEAR, h = 20, center = true);

        // виріз, щоб не заважати клину
        translate([W/2, 0, 0])
            cube([16, H + 4, MOUNT_T + 4], center = true);
    }
}

sensor_mount();
