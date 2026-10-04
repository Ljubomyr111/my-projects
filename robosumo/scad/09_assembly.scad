// ============================================================================
//  09 — Збірка (перевірка взаємного розташування)
//  НЕ для друку. Імпортує реальні STL деталей і додає спрощені моделі
//  покупних вузлів (мотори, колеса, плати, пак, клин).
//
//  Спочатку згенеруй STL:
//    openscad -o ../stl/01_base_plate.stl 01_base_plate.scad   (і так далі)
//  або просто відкрий цей файл у GUI OpenSCAD — імпорт підхопить ../stl/.
//
//  Перемикай шари нижче, щоб перевірити конкретний вузол.
// ============================================================================

include <params.scad>

// --- що показувати ----------------------------------------------------------
SHOW_ENVELOPE = true;    // габаритний бокс класу 200x200
SHOW_PARTS    = true;    // реальні друковані деталі з ../stl/
SHOW_MOTORS   = true;
SHOW_WHEELS   = true;    // колесо + маточина
SHOW_BOARDS   = true;
SHOW_BATTERY  = true;
SHOW_BLADE    = true;
SHOW_MAGNETS  = true;

STL = "../stl/";

// ============================================================================
//  Габаритний бокс класу — робот мусить влізти на старті
// ============================================================================
module class_envelope() {
    %translate([0, 0, 60])
        cube([CHASSIS_W, CHASSIS_L, 120], center = true);
}

// ============================================================================
//  Покупні вузли (спрощені)
// ============================================================================

// Pololu 37D у зборі: редуктор + мотор + вал
module motor_37d() {
    color("Silver")
        rotate([90, 0, 0])
            cylinder(d = MOTOR_BODY_D, h = MOTOR_TOTAL_L);
    color("Goldenrod")
        translate([0, 0, -MOTOR_TOTAL_L/2 - MOTOR_SHAFT_L/2])
            rotate([90, 0, 0])
                cylinder(d = MOTOR_SHAFT_D, h = MOTOR_SHAFT_L);
}

// Маточина, надіта на вал (див. 03_wheel_hub.scad)
module hub() {
    color("Peru")
        translate([0, 0, -MOTOR_SHAFT_L/2 - HUB_T/2 + 2])
            rotate([90, 0, 0])
                cylinder(d = HUB_D_ASSY, h = HUB_T, center = true);
}

// Колесо, прикручене до маточини
module wheel() {
    color("DimGray")
        translate([0, 0, -MOTOR_SHAFT_L/2 - HUB_T - WHEEL_W/2 + 2])
            rotate([90, 0, 0])
                cylinder(d = WHEEL_D, h = WHEEL_W, center = true);
}

HUB_D_ASSY = WHEEL_D - 2;
HUB_T      = 8;

module board(w, l, t, col) {
    color(col) cube([l, w, t], center = true);
}

// Магніти N52: два блоки під клином + чотири біля коліс
module magnets() {
    color("IndianRed") {
        for (x = [-50, 50])
            translate([x, CHASSIS_L/2 - 32, PLATE_T + MAG_D/2])
                cube([20, 20, MAG_D], center = true);
        for (sx = [-1, 1], sy = [-1, 1])
            translate([sx * (WHEEL_TRACK/2 + 28), sy * WHEELBASE/2,
                       PLATE_T + MAG_D/2])
                cube([10, 5, MAG_D], center = true);
    }
}

// Сталевий клин 190x30x3, затиснутий у тримачі й нахилений на 12°.
// Тримач стоїть плазом, тож клин теж плазом: довга вісь уздовж X,
// тонка — уздовж Y, і нахил навколо X піднімає задній край.
module blade() {
    color("LightSlateGray")
        translate([0, CHASSIS_L/2 - 8, PLATE_T + 14])
            rotate([-BLADE_ANGLE, 0, 0])
                cube([BLADE_W, 30, BLADE_T], center = true);
}

// ============================================================================
//  Збірка
// ============================================================================
module assembly() {
    if (SHOW_ENVELOPE) class_envelope();

    if (SHOW_PARTS) {
        color("SteelBlue")     import(str(STL, "01_base_plate.stl"));
        color("CornflowerBlue") translate([0, 0, PLATE_T])
                                   import(str(STL, "06_driver_tray.stl"));
        color("CadetBlue")     translate([0, 25, PLATE_T])
                                   import(str(STL, "07_battery_tray.stl"));
        color("Goldenrod")     translate([0, CHASSIS_L/2 - 20, PLATE_T])
                                   import(str(STL, "04_sensor_mount.stl"));
        color("Sienna")        translate([0, CHASSIS_L/2 - 8, PLATE_T])
                                   import(str(STL, "05_blade_holder.stl"));
        color("DarkOrange")    translate([WHEEL_TRACK/2 - 30, -CHASSIS_L/2 + 28,
                                          PLATE_T])
                                   import(str(STL, "08_servo_mount.stl"));
    }

    if (SHOW_MOTORS)
        for (sx = [-1, 1], sy = [-1, 1])
            translate([sx * WHEEL_TRACK/2, sy * WHEELBASE/2, PLATE_T])
                motor_37d();

    // Колеса стоять у пазах основи (WHEELBASE), а не на краю плити:
    // передня пара на Y = +65, тож клин і сенсорна планка на Y = 85..115
    // не перетинаються з шинами.
    if (SHOW_WHEELS)
        for (sx = [-1, 1], sy = [-1, 1])
            translate([sx * WHEEL_TRACK/2, sy * WHEELBASE/2, PLATE_T - 2]) {
                hub();
                wheel();
            }

    if (SHOW_BOARDS) {
        board(NANO_W, NANO_L, 6, "SteelBlue");
        // чотири драйвери на ложементі
        for (c = [-1, 1], r = [-1, 1])
            translate([c * (BTS_W/2 + 2), r * (BTS_L/2 + 2), PLATE_T + 6])
                board(BTS_W, BTS_L, 8, "DarkGreen");
    }

    if (SHOW_BATTERY)
        color("MediumPurple")
            translate([0, 25, PLATE_T + LIP_H/2])
                cube([LIP_W, LIP_L, LIP_H], center = true);

    if (SHOW_MAGNETS) magnets();
    if (SHOW_BLADE)   blade();
}

assembly();
