// ====================================================================
// Parametric Wearable Enclosure for ESD Wristband Monitor
// Bare Nordic nRF52840-QIAA (aQFN-73) PCB
// Board Dimensions: 32.0 mm x 40.0 mm x 1.6 mm
// ====================================================================

$fn = 64;

// --- Parametric Dimensions ---
pcb_w = 32.0;            // PCB Width (X)
pcb_l = 40.0;            // PCB Length (Y)
pcb_t = 1.6;             // PCB Thickness
clearance = 0.5;         // Per-side clearance
wall_t = 1.8;            // Shell wall thickness
corner_r = 3.0;          // Outer corner fillet radius

top_cavity_h = 3.5;      // Height above PCB for SoC and components
bot_cavity_h = 4.5;      // Height below PCB for Keystone 3002 battery clip
standoff_h = 4.2;        // Height of internal PCB support ledge

outer_w = pcb_w + 2 * (clearance + wall_t); // 36.6 mm
outer_l = pcb_l + 2 * (clearance + wall_t); // 44.6 mm

// --- Module: Rounded Box ---
module rounded_box(w, l, h, r) {
    hull() {
        translate([r, r, 0]) cylinder(h=h, r=r);
        translate([w - r, r, 0]) cylinder(h=h, r=r);
        translate([w - r, l - r, 0]) cylinder(h=h, r=r);
        translate([r, l - r, 0]) cylinder(h=h, r=r);
    }
}

// --- Module: Top Cover ---
module top_cover() {
    difference() {
        // Outer Body
        rounded_box(outer_w, outer_l, top_cavity_h + wall_t, corner_r);
        
        // Inner Cavity
        translate([wall_t, wall_t, -0.1])
            rounded_box(pcb_w + 2 * clearance, pcb_l + 2 * clearance, top_cavity_h + 0.1, corner_r - 1.0);
            
        // LED Viewing Light Pipes (Green, Yellow, Red)
        // Offset origin: (wall_t + clearance) = 2.3 mm
        translate([2.3 + 29.5, 2.3 + 21.0, -1]) cylinder(h=top_cavity_h + wall_t + 2, r=1.0);
        translate([2.3 + 29.5, 2.3 + 25.0, -1]) cylinder(h=top_cavity_h + wall_t + 2, r=1.0);
        translate([2.3 + 29.5, 2.3 + 29.0, -1]) cylinder(h=top_cavity_h + wall_t + 2, r=1.0);
        
        // SWD Programming Port (Left edge)
        translate([-0.5, 2.3 + 7.0 - 3.5, 0.5])
            cube([wall_t + 1, 7.0, 3.0]);
    }
    
    // Internal Screw Bosses
    for (pos = [[3.5, 3.5], [outer_w - 3.5, 3.5], [3.5, outer_l - 3.5], [outer_w - 3.5, outer_l - 3.5]]) {
        translate([pos[0], pos[1], 0]) {
            difference() {
                cylinder(h=top_cavity_h, r=2.2);
                translate([0, 0, -0.1]) cylinder(h=top_cavity_h + 0.2, r=1.0); // M2 screw tap
            }
        }
    }
}

// --- Module: Bottom Base ---
module bottom_base() {
    difference() {
        union() {
            // Main Enclosure Base
            rounded_box(outer_w, outer_l, bot_cavity_h + wall_t, corner_r);
            
            // Watch Strap Lugs (Top: 20mm strap gap)
            translate([2.0, outer_l, 0]) cube([4.0, 6.7, bot_cavity_h + wall_t]);
            translate([outer_w - 6.0, outer_l, 0]) cube([4.0, 6.7, bot_cavity_h + wall_t]);
            
            // Watch Strap Lugs (Bottom: 20mm strap gap)
            translate([2.0, -6.7, 0]) cube([4.0, 6.7, bot_cavity_h + wall_t]);
            translate([outer_w - 6.0, -6.7, 0]) cube([4.0, 6.7, bot_cavity_h + wall_t]);
        }
        
        // Internal Battery Cavity
        translate([wall_t, wall_t, wall_t])
            rounded_box(pcb_w + 2 * clearance, pcb_l + 2 * clearance, bot_cavity_h + 1.0, corner_r - 1.0);
            
        // Contact A Snap Aperture (J1)
        translate([2.3 + 6.0, 2.3 + 36.0, -1]) cylinder(h=wall_t + 2, r=1.8);
        // Contact B Snap Aperture (J2)
        translate([2.3 + 16.0, 2.3 + 36.0, -1]) cylinder(h=wall_t + 2, r=1.8);
        // Earth Ground Snap Stud Aperture (J3)
        translate([2.3 + 26.0, 2.3 + 36.0, -1]) cylinder(h=wall_t + 2, r=1.8);
        
        // Circular CR2032 Battery Replacement Door Opening (22 mm dia)
        translate([2.3 + 16.0, 2.3 + 22.0, -1]) cylinder(h=wall_t + 2, r=11.0);
    }
}

// --- Render Full Assembly or Specific Part ---
// Uncomment the part you wish to render:
color("SlateGray") translate([0, 0, 15]) top_cover();
color("DimGray") bottom_base();
