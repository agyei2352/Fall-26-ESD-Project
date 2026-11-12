"""
SolidWorks / 3D CAD Enclosure Generator for ESD Wristband Monitor
Generates:
1. Enclosure_Top_Cover.stl
2. Enclosure_Bottom_Base.stl
3. Battery_Door.stl
4. Complete_Enclosure_Assembly.stl
5. ESD_Wristband_Enclosure.scad (Parametric OpenSCAD design)
Matching the exact 32.0 x 40.0 mm bare nRF52840 PCB layout.
"""
import os
import math
import struct
import shutil

OUTPUT_DIR = r"C:\Fall 26 ESD Project\SolidWorks Design"
PCB_STEP_SRC = r"C:\Fall 26 ESD Project\PCB Design\ESD_Wristband_Monitor.step"

class MeshBuilder:
    def __init__(self, name="Part"):
        self.name = name
        self.triangles = [] # List of ((nx, ny, nz), (v1x, v1y, v1z), (v2x, v2y, v2z), (v3x, v3y, v3z))

    def add_triangle(self, v1, v2, v3):
        # Compute normal
        ax, ay, az = v2[0] - v1[0], v2[1] - v1[1], v2[2] - v1[2]
        bx, by, bz = v3[0] - v1[0], v3[1] - v1[1], v3[2] - v1[2]
        nx = ay * bz - az * by
        ny = az * bx - ax * bz
        nz = ax * by - ay * bx
        length = math.sqrt(nx * nx + ny * ny + nz * nz)
        if length > 1e-9:
            nx, ny, nz = nx / length, ny / length, nz / length
        else:
            nx, ny, nz = 0.0, 0.0, 1.0
        self.triangles.append(((nx, ny, nz), v1, v2, v3))

    def add_quad(self, v1, v2, v3, v4):
        # Two triangles for a planar quad
        self.add_triangle(v1, v2, v3)
        self.add_triangle(v1, v3, v4)

    def add_box(self, x, y, z, dx, dy, dz):
        # 8 vertices
        p0 = (x, y, z)
        p1 = (x + dx, y, z)
        p2 = (x + dx, y + dy, z)
        p3 = (x, y + dy, z)
        p4 = (x, y, z + dz)
        p5 = (x + dx, y, z + dz)
        p6 = (x + dx, y + dy, z + dz)
        p7 = (x, y + dy, z + dz)

        # Bottom (z)
        self.add_quad(p0, p3, p2, p1)
        # Top (z + dz)
        self.add_quad(p4, p5, p6, p7)
        # Front (y)
        self.add_quad(p0, p1, p5, p4)
        # Back (y + dy)
        self.add_quad(p2, p3, p7, p6)
        # Left (x)
        self.add_quad(p0, p4, p7, p3)
        # Right (x + dx)
        self.add_quad(p1, p2, p6, p5)

    def add_cylinder(self, cx, cy, z_base, radius, height, num_segments=32):
        angle_step = 2.0 * math.pi / num_segments
        bot_center = (cx, cy, z_base)
        top_center = (cx, cy, z_base + height)

        for i in range(num_segments):
            a1 = i * angle_step
            a2 = (i + 1) * angle_step
            cos1, sin1 = math.cos(a1), math.sin(a1)
            cos2, sin2 = math.cos(a2), math.sin(a2)

            b1 = (cx + radius * cos1, cy + radius * sin1, z_base)
            b2 = (cx + radius * cos2, cy + radius * sin2, z_base)
            t1 = (cx + radius * cos1, cy + radius * sin1, z_base + height)
            t2 = (cx + radius * cos2, cy + radius * sin2, z_base + height)

            # Bottom cap
            self.add_triangle(bot_center, b2, b1)
            # Top cap
            self.add_triangle(top_center, t1, t2)
            # Side quad
            self.add_quad(b1, b2, t2, t1)

    def add_tube(self, cx, cy, z_base, r_inner, r_outer, height, num_segments=32):
        angle_step = 2.0 * math.pi / num_segments
        for i in range(num_segments):
            a1 = i * angle_step
            a2 = (i + 1) * angle_step
            cos1, sin1 = math.cos(a1), math.sin(a1)
            cos2, sin2 = math.cos(a2), math.sin(a2)

            # Inner
            ib1 = (cx + r_inner * cos1, cy + r_inner * sin1, z_base)
            ib2 = (cx + r_inner * cos2, cy + r_inner * sin2, z_base)
            it1 = (cx + r_inner * cos1, cy + r_inner * sin1, z_base + height)
            it2 = (cx + r_inner * cos2, cy + r_inner * sin2, z_base + height)

            # Outer
            ob1 = (cx + r_outer * cos1, cy + r_outer * sin1, z_base)
            ob2 = (cx + r_outer * cos2, cy + r_outer * sin2, z_base)
            ot1 = (cx + r_outer * cos1, cy + r_outer * sin1, z_base + height)
            ot2 = (cx + r_outer * cos2, cy + r_outer * sin2, z_base + height)

            # Bottom cap
            self.add_quad(ib1, ib2, ob2, ob1)
            # Top cap
            self.add_quad(it1, ot1, ot2, it2)
            # Outer wall
            self.add_quad(ob1, ob2, ot2, ot1)
            # Inner wall
            self.add_quad(ib2, ib1, it1, it2)

    def add_rounded_prism(self, x, y, z, dx, dy, dz, r, num_segments=8):
        # 2D rounded rectangle extruded along Z
        # Centers of the 4 corner arcs
        cx1, cy1 = x + r, y + r
        cx2, cy2 = x + dx - r, y + r
        cx3, cy3 = x + dx - r, y + dy - r
        cx4, cy4 = x + r, y + dy - r

        pts = []
        # Bottom-right arc
        for i in range(num_segments + 1):
            ang = -math.pi / 2.0 + (math.pi / 2.0) * (i / num_segments)
            pts.append((cx2 + r * math.cos(ang), cy2 + r * math.sin(ang)))
        # Top-right arc
        for i in range(num_segments + 1):
            ang = 0.0 + (math.pi / 2.0) * (i / num_segments)
            pts.append((cx3 + r * math.cos(ang), cy3 + r * math.sin(ang)))
        # Top-left arc
        for i in range(num_segments + 1):
            ang = math.pi / 2.0 + (math.pi / 2.0) * (i / num_segments)
            pts.append((cx4 + r * math.cos(ang), cy4 + r * math.sin(ang)))
        # Bottom-left arc
        for i in range(num_segments + 1):
            ang = math.pi + (math.pi / 2.0) * (i / num_segments)
            pts.append((cx1 + r * math.cos(ang), cy1 + r * math.sin(ang)))

        # Triangulate top and bottom using fan from center
        center_bot = (x + dx / 2.0, y + dy / 2.0, z)
        center_top = (x + dx / 2.0, y + dy / 2.0, z + dz)

        N = len(pts)
        for i in range(N):
            p_cur = pts[i]
            p_nxt = pts[(i + 1) % N]

            b1 = (p_cur[0], p_cur[1], z)
            b2 = (p_nxt[0], p_nxt[1], z)
            t1 = (p_cur[0], p_cur[1], z + dz)
            t2 = (p_nxt[0], p_nxt[1], z + dz)

            # Bottom cap
            self.add_triangle(center_bot, b2, b1)
            # Top cap
            self.add_triangle(center_top, t1, t2)
            # Side wall
            self.add_quad(b1, b2, t2, t1)

    def write_stl(self, filepath):
        header = f"SolidWorks Enclosure: {self.name}".encode('ascii')[:80].ljust(80, b'\x00')
        count = len(self.triangles)
        with open(filepath, 'wb') as f:
            f.write(struct.pack('<80sI', header, count))
            for norm, v1, v2, v3 in self.triangles:
                f.write(struct.pack('<3f3f3f3fH',
                                    norm[0], norm[1], norm[2],
                                    v1[0], v1[1], v1[2],
                                    v2[0], v2[1], v2[2],
                                    v3[0], v3[1], v3[2],
                                    0))
        print(f"Generated {filepath} ({count} triangles)")

def build_top_cover():
    mb = MeshBuilder("Enclosure_Top_Cover")
    # Outer bounds: X: -2.3 to 34.3 (dx=36.6), Y: -2.3 to 42.3 (dy=44.6)
    # Z: 0.0 to 5.3 (height=5.3 mm, ceiling from 3.5 to 5.3)
    # 1. Main outer shell with rounded corners (R=3.0mm)
    mb.add_rounded_prism(-2.3, -2.3, 3.5, 36.6, 44.6, 1.8, r=3.0) # Roof ceiling

    # 2. Outer side walls: from Z=0.0 to 3.5
    # Left wall (X: -2.3 to -0.5)
    mb.add_box(-2.3, -2.3, 0.0, 1.8, 44.6, 3.5)
    # Right wall (X: 32.5 to 34.3)
    mb.add_box(32.5, -2.3, 0.0, 1.8, 44.6, 3.5)
    # Front wall (Y: -2.3 to -0.5)
    mb.add_box(-0.5, -2.3, 0.0, 33.0, 1.8, 3.5)
    # Back wall (Y: 40.5 to 42.3)
    mb.add_box(-0.5, 40.5, 0.0, 33.0, 1.8, 3.5)

    # 3. LED Light Guide Channels / Bezels (Cylinders on top of the cover)
    # Green LED at (29.5, 21.0), Yellow at (29.5, 25.0), Red at (29.5, 29.0)
    for led_y in [21.0, 25.0, 29.0]:
        mb.add_tube(29.5, led_y, 3.5, r_inner=1.0, r_outer=1.6, height=1.8)

    # 4. Corner Screw Bosses (4 corners for M2 screws)
    boss_coords = [
        (0.5, 0.5),
        (31.5, 0.5),
        (0.5, 39.5),
        (31.5, 39.5)
    ]
    for bx, by in boss_coords:
        mb.add_tube(bx, by, 0.0, r_inner=1.0, r_outer=2.2, height=3.5)

    # 5. Top Silkscreen / Logo Ridge
    mb.add_box(6.0, 3.0, 5.3, 20.0, 1.2, 0.4) # Aesthetic accent stripe

    top_stl = os.path.join(OUTPUT_DIR, "Enclosure_Top_Cover.stl")
    mb.write_stl(top_stl)
    return mb

def build_bottom_base():
    mb = MeshBuilder("Enclosure_Bottom_Base")
    # Base bounds: X: -2.3 to 34.3 (dx=36.6), Y: -2.3 to 42.3 (dy=44.6)
    # Z: -6.8 to 0.0 (Floor from -6.8 to -5.0, walls from -5.0 to 0.0)

    # 1. Base floor plate
    mb.add_rounded_prism(-2.3, -2.3, -6.8, 36.6, 44.6, 1.8, r=3.0)

    # 2. Side walls: from Z=-5.0 to 0.0
    # Left wall
    mb.add_box(-2.3, -2.3, -5.0, 1.8, 44.6, 5.0)
    # Right wall
    mb.add_box(32.5, -2.3, -5.0, 1.8, 44.6, 5.0)
    # Front wall
    mb.add_box(-0.5, -2.3, -5.0, 33.0, 1.8, 5.0)
    # Back wall
    mb.add_box(-0.5, 40.5, -5.0, 33.0, 1.8, 5.0)

    # 3. PCB Standoff Ledges in 4 corners (Support PCB at Z = -1.6 mm)
    # Bottom of PCB rests on these standoffs
    boss_coords = [
        (0.5, 0.5),
        (31.5, 0.5),
        (0.5, 39.5),
        (31.5, 39.5)
    ]
    for bx, by in boss_coords:
        mb.add_tube(bx, by, -5.0, r_inner=0.9, r_outer=2.4, height=3.4)

    # 4. Wrist Contact Terminals Bosses / Snap Apertures on bottom floor
    # J1 at (6.0, 36.0), J2 at (16.0, 36.0), J3 at (26.0, 36.0)
    for jx in [6.0, 16.0, 26.0]:
        mb.add_tube(jx, 36.0, -6.8, r_inner=1.8, r_outer=2.8, height=2.2)

    # 5. Keystone 3002 Battery Retention Support Ring (Center at 16.0, 22.0)
    mb.add_tube(16.0, 22.0, -5.0, r_inner=10.2, r_outer=11.6, height=1.6)

    # 6. Integrated Wristband Strap Lugs (Standard 20mm watch strap width)
    # Top strap lugs extending from Y = 42.3 to 49.0
    # Left lug (X: 2.0 to 6.0)
    mb.add_box(2.0, 42.3, -6.0, 4.0, 6.7, 4.5)
    mb.add_cylinder(4.0, 49.0, -6.0, radius=2.25, height=4.5)
    # Right lug (X: 26.0 to 30.0)
    mb.add_box(26.0, 42.3, -6.0, 4.0, 6.7, 4.5)
    mb.add_cylinder(28.0, 49.0, -6.0, radius=2.25, height=4.5)

    # Bottom strap lugs extending from Y = -2.3 to -9.0
    # Left lug (X: 2.0 to 6.0)
    mb.add_box(2.0, -9.0, -6.0, 4.0, 6.7, 4.5)
    mb.add_cylinder(4.0, -9.0, -6.0, radius=2.25, height=4.5)
    # Right lug (X: 26.0 to 30.0)
    mb.add_box(26.0, -9.0, -6.0, 4.0, 6.7, 4.5)
    mb.add_cylinder(28.0, -9.0, -6.0, radius=2.25, height=4.5)

    base_stl = os.path.join(OUTPUT_DIR, "Enclosure_Bottom_Base.stl")
    mb.write_stl(base_stl)
    return mb

def build_battery_door():
    mb = MeshBuilder("Battery_Door")
    # Circular twist-lock / snap battery door for CR2032
    # Radius = 11.0 mm (Diameter 22 mm), thickness = 1.6 mm
    cx, cy, cz = 16.0, 22.0, -6.8
    mb.add_cylinder(cx, cy, cz, radius=11.0, height=1.6)

    # Coin slot for toolless opening (Width = 14 mm, depth = 2.0 mm, height = 0.8 mm)
    # Modeled as a raised grip rib with coin recess
    mb.add_box(cx - 7.0, cy - 1.2, cz + 1.6, 14.0, 2.4, 0.8)

    # Retention locking tabs at 0 and 180 degrees
    mb.add_box(cx - 12.2, cy - 2.0, cz + 0.8, 1.4, 4.0, 0.8)
    mb.add_box(cx + 10.8, cy - 2.0, cz + 0.8, 1.4, 4.0, 0.8)

    door_stl = os.path.join(OUTPUT_DIR, "Battery_Door.stl")
    mb.write_stl(door_stl)
    return mb

def build_complete_assembly(top_mb, base_mb, door_mb):
    mb = MeshBuilder("Complete_Enclosure_Assembly")
    # Combine triangles from all 3 bodies in their mated positions
    mb.triangles.extend(top_mb.triangles)
    mb.triangles.extend(base_mb.triangles)
    mb.triangles.extend(door_mb.triangles)

    assy_stl = os.path.join(OUTPUT_DIR, "Complete_Enclosure_Assembly.stl")
    mb.write_stl(assy_stl)

def generate_openscad_script():
    scad_content = """// ====================================================================
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
"""
    scad_path = os.path.join(OUTPUT_DIR, "ESD_Wristband_Enclosure.scad")
    with open(scad_path, "w", encoding="utf-8") as f:
        f.write(scad_content)
    print(f"Generated {scad_path}")

def copy_pcb_step():
    if os.path.exists(PCB_STEP_SRC):
        dest = os.path.join(OUTPUT_DIR, "ESD_Wristband_Monitor_PCB.step")
        shutil.copy2(PCB_STEP_SRC, dest)
        print(f"Copied PCB STEP to {dest}")

if __name__ == "__main__":
    print("Generating SolidWorks 3D CAD Enclosure...")
    top = build_top_cover()
    base = build_bottom_base()
    door = build_battery_door()
    build_complete_assembly(top, base, door)
    generate_openscad_script()
    copy_pcb_step()
    print("All SolidWorks 3D CAD files generated successfully!")

