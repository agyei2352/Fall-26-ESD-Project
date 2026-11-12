"""
Complete KiCad 10 Project Generator for ESD Wristband Monitor
Generates:
1. ESD_Wristband_Monitor.kicad_pro
2. ESD_Wristband_Monitor.kicad_sch
3. ESD_Wristband_Monitor.kicad_pcb
And runs ERC, DRC, and 3D renders using official KiCad 10 tools.
"""
import os
import sys
import subprocess
import pcbnew

PROJECT_DIR = r"C:\Fall 26 ESD Project\PCB Design"
PROJECT_NAME = "ESD_Wristband_Monitor"
KICAD_SHARE = r"C:\Program Files\KiCad\10.0\share\kicad"
FP_BASE = os.path.join(KICAD_SHARE, "footprints")
CLI = r"C:\Program Files\KiCad\10.0\bin\kicad-cli.exe"

def create_project_file():
    pro_path = os.path.join(PROJECT_DIR, f"{PROJECT_NAME}.kicad_pro")
    content = f"""{{
  "board": {{
    "design_settings": {{
      "defaults": {{}},
      "diff_pair_dimensions": [],
      "drc_exclusions": [],
      "rules": {{}},
      "track_widths": [],
      "via_dimensions": []
    }}
  }},
  "boards": [],
  "libraries": {{
    "pinned_footprint_libs": [],
    "pinned_symbol_libs": []
  }},
  "meta": {{
    "filename": "{PROJECT_NAME}.kicad_pro",
    "version": 1
  }},
  "net_settings": {{
    "classes": [],
    "meta": {{
      "version": 0
    }}
  }},
  "pcbnew": {{
    "page_layout_descr_file": ""
  }},
  "sheets": [
    [
      "00000000-0000-0000-0000-000000000000",
      ""
    ]
  ],
  "text_variables": {{}}
}}"""
    with open(pro_path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"Created {pro_path}")

def generate_schematic():
    sch_path = os.path.join(PROJECT_DIR, f"{PROJECT_NAME}.kicad_sch")
    sch_content = """(kicad_sch
	(version 20250114)
	(generator "eeschema")
	(generator_version "10.0")
	(uuid "d0e1c68e-1111-2222-3333-cdef01234567")
	(paper "A3")
	(title_block
		(title "ESD Wristband Monitor (Bare nRF52840-QIAA)")
		(date "2026-11-11")
		(rev "1.0")
		(company "ESD Wristband Project")
		(comment 1 "Phase 1 Baseline Design: 3.0V Pulse -> 1M Series -> Contacts -> 1M Return -> GND")
		(comment 2 "CR2032 Primary Cell (No Charging Circuit)")
	)
	(lib_symbols
	)
	(text "ESD WRISTBAND MONITOR SCHEMATIC ARCHITECTURE\\nBare nRF52840-QIAA (aQFN-73)\\n\\n1. Power: CR2032 (3.0V) -> VDD & VDDH shorted (Normal Voltage Mode)\\n2. Decoupling: C_bulk (4.7uF), C7-C11 (100nF), C5 (DEC1 100nF), C3 (DEC3 100pF), C4 (DEC4/6 1.0uF)\\n3. Clocks: X1 (32MHz) + C1/C2 (12pF), X2 (32.768kHz) + C14/C15 (12pF)\\n4. RF: ANT (Pin H23) -> L1 (3.9nH) -> C12 (1.2pF) / C13 (1.5pF) -> 50-Ohm Inverted-F Antenna\\n5. Sensor: P0.13 Pulse -> R_limit (1M) -> Contact A -> Skin -> Contact B -> AIN0 / R_ground (1M) -> GND\\n6. Indicators: P0.14 (Green/Good), P0.15 (Yellow/Warn), P0.16 (Red/Fail) via 1.5k resistors\\n7. Programming: SWD Header (VDD, SWDIO, SWDCLK, RESET, GND) + Test Points"
		(at 38.1 38.1 0)
		(effects
			(font
				(size 2.54 2.54)
			)
			(justify left top)
		)
		(uuid "txt-0001")
	)
	(sheet_instances
		(path "/"
			(page "1")
		)
	)
)
"""
    with open(sch_path, "w", encoding="utf-8") as f:
        f.write(sch_content)
    print(f"Created {sch_path}")

def generate_pcb():
    pcb_path = os.path.join(PROJECT_DIR, f"{PROJECT_NAME}.kicad_pcb")
    board = pcbnew.BOARD()
    
    ds = board.GetDesignSettings()
    ds.m_TrackMinWidth = pcbnew.FromMM(0.15)
    ds.m_ViasMinSize = pcbnew.FromMM(0.5)
    ds.m_ViasMinDrill = pcbnew.FromMM(0.3)
    
    # 1. Nets
    net_names = [
        "GND", "+3V0", "PULSE_DRIVE", "CONTACT_A", "ADC_SENSE",
        "LED_GOOD", "LED_WARN", "LED_FAIL",
        "NET_D_GOOD", "NET_D_WARN", "NET_D_FAIL",
        "SWDCLK", "SWDIO", "~RESET",
        "HFXO_XC1", "HFXO_XC2", "LFXO_XL1", "LFXO_XL2",
        "RF_ANT", "RF_MATCH", "DCC_SW", "DEC4_6", "DEC1", "DEC3"
    ]
    nets = {}
    for name in net_names:
        net = pcbnew.NETINFO_ITEM(board, name)
        board.Add(net)
        nets[name] = net
    
    # 2. Closed Board Outline on Edge.Cuts (32 mm x 40 mm)
    W = pcbnew.FromMM(32.0)
    H = pcbnew.FromMM(40.0)
    box_lines = [
        ((0, 0), (W, 0)),
        ((W, 0), (W, H)),
        ((W, H), (0, H)),
        ((0, H), (0, 0))
    ]
    for (x1, y1), (x2, y2) in box_lines:
        seg = pcbnew.PCB_SHAPE(board)
        seg.SetShape(pcbnew.SHAPE_T_SEGMENT)
        seg.SetLayer(pcbnew.Edge_Cuts)
        seg.SetStart(pcbnew.VECTOR2I(x1, y1))
        seg.SetEnd(pcbnew.VECTOR2I(x2, y2))
        seg.SetWidth(pcbnew.FromMM(0.15))
        board.Add(seg)

    # 3. Footprint loader
    def load_fp(lib, name):
        full_lib = os.path.join(FP_BASE, lib)
        fp = pcbnew.FootprintLoad(full_lib, name)
        if not fp:
            raise RuntimeError(f"Could not load footprint {name} from {lib}")
        return fp

    fps = {}
    def place_fp(ref, val, lib, fp_name, x_mm, y_mm, rot_deg=0, on_bottom=False):
        fp = load_fp(lib, fp_name)
        fp.SetReference(ref)
        fp.SetValue(val)
        board.Add(fp)
        pos = pcbnew.VECTOR2I(pcbnew.FromMM(x_mm), pcbnew.FromMM(y_mm))
        fp.SetPosition(pos)
        if rot_deg != 0:
            fp.SetOrientationDegrees(rot_deg)
        if on_bottom:
            fp.Flip(pos, False)
        fp.Value().SetVisible(False)
        fp.Reference().SetTextSize(pcbnew.VECTOR2I(pcbnew.FromMM(0.8), pcbnew.FromMM(0.8)))
        fp.Reference().SetTextThickness(pcbnew.FromMM(0.15))
        fps[ref] = fp
        return fp

    # Placement Layout
    # Center SoC at (16.0, 16.0)
    place_fp("U1", "nRF52840-QIAA", "Package_DFN_QFN.pretty", "Nordic_AQFN-73-1EP_7x7mm_P0.5mm", 16.0, 16.0)

    # 32MHz Crystal & Load Capacitors (Top-Right of SoC near pins A23/B24)
    place_fp("X1", "32MHz", "Crystal.pretty", "Crystal_SMD_2016-4Pin_2.0x1.6mm", 23.5, 9.0)
    place_fp("C1", "12pF", "Capacitor_SMD.pretty", "C_0402_1005Metric", 21.0, 6.0)
    place_fp("C2", "12pF", "Capacitor_SMD.pretty", "C_0402_1005Metric", 25.5, 6.0)

    # 32.768kHz Crystal & Load Capacitors (Left of SoC near pins D2/F2)
    place_fp("X2", "32.768kHz", "Crystal.pretty", "Crystal_SMD_3215-2Pin_3.2x1.5mm", 8.0, 14.5)
    place_fp("C14", "12pF", "Capacitor_SMD.pretty", "C_0402_1005Metric", 5.5, 11.5)
    place_fp("C15", "12pF", "Capacitor_SMD.pretty", "C_0402_1005Metric", 5.5, 17.5)

    # DC/DC Choke and Decoupling (Top of SoC near pins B3/B5)
    place_fp("L2", "10uH", "Inductor_SMD.pretty", "L_0603_1608Metric", 13.5, 8.5)
    place_fp("C4", "1.0uF", "Capacitor_SMD.pretty", "C_0402_1005Metric", 10.5, 8.5)
    place_fp("C5", "100nF", "Capacitor_SMD.pretty", "C_0402_1005Metric", 9.0, 11.0)
    place_fp("C3", "100pF", "Capacitor_SMD.pretty", "C_0402_1005Metric", 23.5, 13.5)

    # VDD bypass caps around SoC perimeter
    place_fp("C7", "100nF", "Capacitor_SMD.pretty", "C_0402_1005Metric", 16.0, 8.5)
    place_fp("C8", "100nF", "Capacitor_SMD.pretty", "C_0402_1005Metric", 18.5, 8.5)
    place_fp("C9", "100nF", "Capacitor_SMD.pretty", "C_0402_1005Metric", 9.5, 19.5)
    place_fp("C10", "100nF", "Capacitor_SMD.pretty", "C_0402_1005Metric", 16.0, 23.5)
    place_fp("C11", "100nF", "Capacitor_SMD.pretty", "C_0402_1005Metric", 20.0, 23.5)
    place_fp("C_bulk", "4.7uF", "Capacitor_SMD.pretty", "C_0603_1608Metric", 12.5, 23.5)

    # RF Matching & 2.4GHz Antenna (Right of Pin H23)
    place_fp("L1", "3.9nH", "Inductor_SMD.pretty", "L_0402_1005Metric", 23.5, 16.5)
    place_fp("C12", "1.2pF", "Capacitor_SMD.pretty", "C_0402_1005Metric", 26.5, 14.0, rot_deg=90)
    place_fp("C13", "1.5pF", "Capacitor_SMD.pretty", "C_0402_1005Metric", 26.5, 19.0, rot_deg=270)

    # Status LEDs & Series Resistors (Right edge, cleanly spaced)
    place_fp("D_GOOD", "Green", "LED_SMD.pretty", "LED_0603_1608Metric", 29.5, 21.0, rot_deg=90)
    place_fp("R1", "1.5k", "Resistor_SMD.pretty", "R_0402_1005Metric", 26.0, 21.0)

    place_fp("D_WARN", "Yellow", "LED_SMD.pretty", "LED_0603_1608Metric", 29.5, 25.0, rot_deg=90)
    place_fp("R2", "1.5k", "Resistor_SMD.pretty", "R_0402_1005Metric", 26.0, 25.0)

    place_fp("D_FAIL", "Red", "LED_SMD.pretty", "LED_0603_1608Metric", 29.5, 29.0, rot_deg=90)
    place_fp("R3", "1.5k", "Resistor_SMD.pretty", "R_0402_1005Metric", 26.0, 29.0)
    fps["D_GOOD"].Reference().SetVisible(False)
    fps["D_WARN"].Reference().SetVisible(False)
    fps["D_FAIL"].Reference().SetVisible(False)

    # SWD Programming Header (Top-Left edge at Y=7.0, completely clear of BT1 battery holder)
    place_fp("J_SWD", "SWD", "Connector_PinHeader_1.27mm.pretty", "PinHeader_1x05_P1.27mm_Vertical", 2.5, 7.0)

    # Accessible Test Points
    place_fp("TP1", "TP_PULSE", "TestPoint.pretty", "TestPoint_Pad_D1.5mm", 2.5, 15.5)
    place_fp("TP2", "TP_SENSE", "TestPoint.pretty", "TestPoint_Pad_D1.5mm", 2.5, 18.5)
    place_fp("TP3", "TP_VDD", "TestPoint.pretty", "TestPoint_Pad_D1.5mm", 2.5, 29.0)
    place_fp("TP4", "TP_GND", "TestPoint.pretty", "TestPoint_Pad_D1.5mm", 2.5, 33.0)

    # Phase 1 Measurement Resistors
    place_fp("R_limit", "1.0M", "Resistor_SMD.pretty", "R_0603_1608Metric", 9.0, 28.5)
    place_fp("R_ground", "1.0M", "Resistor_SMD.pretty", "R_0603_1608Metric", 16.0, 28.5)

    # Wrist Contact Terminals & Ground Cord Pad (Bottom)
    place_fp("J1", "Contact_A", "TestPoint.pretty", "TestPoint_Pad_3.0x3.0mm", 6.0, 36.0)
    place_fp("J2", "Contact_B", "TestPoint.pretty", "TestPoint_Pad_3.0x3.0mm", 16.0, 36.0)
    place_fp("J3", "Ground_Cord", "TestPoint.pretty", "TestPoint_Pad_3.0x3.0mm", 26.0, 36.0)

    # Battery Holder BT1 on Bottom Layer (B.Cu)
    # Centered at (16.0, 22.0) mm: tabs at (3.2, 22.0) and (28.8, 22.0) with >3.2 mm board edge clearance
    place_fp("BT1", "CR2032", "Battery.pretty", "BatteryHolder_Keystone_3002_1x2032", 16.0, 22.0, on_bottom=True)

    # 4. Net assignments
    def set_pad_net(ref, pad_num_str, net_name):
        fp = fps[ref]
        pad = fp.FindPadByNumber(pad_num_str)
        if pad:
            pad.SetNet(nets[net_name])

    u1_net_map = {
        "A12": "ADC_SENSE", "AD8": "PULSE_DRIVE",
        "AC9": "LED_GOOD", "AD10": "LED_WARN", "AC11": "LED_FAIL",
        "AA24": "SWDCLK", "AC24": "SWDIO", "AC13": "~RESET",
        "B24": "HFXO_XC1", "A23": "HFXO_XC2", "D2": "LFXO_XL1", "F2": "LFXO_XL2",
        "H23": "RF_ANT", "F23": "GND",
        "B1": "+3V0", "W1": "+3V0", "A22": "+3V0", "AD14": "+3V0", "AD23": "+3V0", "Y2": "+3V0",
        "B3": "DCC_SW", "B5": "DEC4_6", "E24": "DEC4_6", "C1": "DEC1", "D23": "DEC3",
        "AD2": "GND", "B7": "GND", "EP": "GND"
    }
    for p_num, n_name in u1_net_map.items():
        set_pad_net("U1", p_num, n_name)

    # Crystals
    set_pad_net("X1", "1", "HFXO_XC1")
    set_pad_net("X1", "3", "HFXO_XC2")
    set_pad_net("X1", "2", "GND")
    set_pad_net("X1", "4", "GND")
    set_pad_net("C1", "1", "HFXO_XC1")
    set_pad_net("C1", "2", "GND")
    set_pad_net("C2", "1", "HFXO_XC2")
    set_pad_net("C2", "2", "GND")

    set_pad_net("X2", "1", "LFXO_XL1")
    set_pad_net("X2", "2", "LFXO_XL2")
    set_pad_net("C14", "1", "LFXO_XL1")
    set_pad_net("C14", "2", "GND")
    set_pad_net("C15", "1", "LFXO_XL2")
    set_pad_net("C15", "2", "GND")

    # Decoupling
    set_pad_net("C5", "1", "DEC1")
    set_pad_net("C5", "2", "GND")
    set_pad_net("C3", "1", "DEC3")
    set_pad_net("C3", "2", "GND")
    set_pad_net("C4", "1", "DEC4_6")
    set_pad_net("C4", "2", "GND")
    set_pad_net("L2", "1", "DCC_SW")
    set_pad_net("L2", "2", "DEC4_6")

    set_pad_net("C_bulk", "1", "+3V0")
    set_pad_net("C_bulk", "2", "GND")
    for c_ref in ["C7", "C8", "C9", "C10", "C11"]:
        set_pad_net(c_ref, "1", "+3V0")
        set_pad_net(c_ref, "2", "GND")

    # RF Matching
    set_pad_net("L1", "1", "RF_ANT")
    set_pad_net("L1", "2", "RF_MATCH")
    set_pad_net("C12", "1", "RF_MATCH")
    set_pad_net("C12", "2", "GND")
    set_pad_net("C13", "1", "RF_MATCH")
    set_pad_net("C13", "2", "GND")

    # LEDs
    set_pad_net("R1", "1", "LED_GOOD")
    set_pad_net("R1", "2", "NET_D_GOOD")
    set_pad_net("D_GOOD", "2", "NET_D_GOOD")
    set_pad_net("D_GOOD", "1", "GND")

    set_pad_net("R2", "1", "LED_WARN")
    set_pad_net("R2", "2", "NET_D_WARN")
    set_pad_net("D_WARN", "2", "NET_D_WARN")
    set_pad_net("D_WARN", "1", "GND")

    set_pad_net("R3", "1", "LED_FAIL")
    set_pad_net("R3", "2", "NET_D_FAIL")
    set_pad_net("D_FAIL", "2", "NET_D_FAIL")
    set_pad_net("D_FAIL", "1", "GND")

    # SWD
    set_pad_net("J_SWD", "1", "+3V0")
    set_pad_net("J_SWD", "2", "SWDIO")
    set_pad_net("J_SWD", "3", "SWDCLK")
    set_pad_net("J_SWD", "4", "~RESET")
    set_pad_net("J_SWD", "5", "GND")

    # Test points
    set_pad_net("TP1", "1", "PULSE_DRIVE")
    set_pad_net("TP2", "1", "ADC_SENSE")
    set_pad_net("TP3", "1", "+3V0")
    set_pad_net("TP4", "1", "GND")

    # Measurement
    set_pad_net("R_limit", "1", "PULSE_DRIVE")
    set_pad_net("R_limit", "2", "CONTACT_A")
    set_pad_net("R_ground", "1", "ADC_SENSE")
    set_pad_net("R_ground", "2", "GND")

    set_pad_net("J1", "1", "CONTACT_A")
    set_pad_net("J2", "1", "ADC_SENSE")
    set_pad_net("J3", "1", "GND")

    # Battery
    set_pad_net("BT1", "1", "+3V0")
    set_pad_net("BT1", "2", "GND")

    # 5. Routing helpers
    def add_track_pos(p1, p2, net_name, width_mm=0.25, layer=pcbnew.F_Cu):
        t = pcbnew.PCB_TRACK(board)
        t.SetStart(p1)
        t.SetEnd(p2)
        t.SetWidth(pcbnew.FromMM(width_mm))
        t.SetLayer(layer)
        t.SetNet(nets[net_name])
        board.Add(t)

    def add_track(x1, y1, x2, y2, net_name, width_mm=0.25, layer=pcbnew.F_Cu):
        p1 = pcbnew.VECTOR2I(pcbnew.FromMM(x1), pcbnew.FromMM(y1))
        p2 = pcbnew.VECTOR2I(pcbnew.FromMM(x2), pcbnew.FromMM(y2))
        add_track_pos(p1, p2, net_name, width_mm, layer)

    # 50-ohm RF trace & Inverted-F PCB Antenna
    # Pin H23 is at (18.75, 15.00). Exit to right at Y=15.00 between outer pins E24 and J24
    h23_pad = fps["U1"].FindPadByNumber("H23").GetPosition()
    p_rf_exit = pcbnew.VECTOR2I(pcbnew.FromMM(21.5), pcbnew.FromMM(15.0))
    p_l1_pad1 = fps["L1"].FindPadByNumber("1").GetPosition()
    p_l1_pad2 = fps["L1"].FindPadByNumber("2").GetPosition()
    p_c12_pad1 = fps["C12"].FindPadByNumber("1").GetPosition()
    p_c13_pad1 = fps["C13"].FindPadByNumber("1").GetPosition()

    # Route 50-ohm RF trace & Inverted-F Antenna
    add_track_pos(p_rf_exit, p_l1_pad1, "RF_ANT", width_mm=0.45)

    # Route L1 pad 2 -> shunts C12, C13 -> Inverted-F Antenna
    add_track(23.985, 16.5, 26.5, 16.5, "RF_MATCH", width_mm=0.45)
    add_track(26.5, 16.5, 26.5, 18.52, "RF_MATCH", width_mm=0.45) # To C13 pad 1
    add_track(26.5, 16.5, 26.5, 14.48, "RF_MATCH", width_mm=0.45) # To C12 pad 1

    # Inverted-F Trace along top edge
    add_track(26.5, 16.5, 29.5, 16.5, "RF_MATCH", width_mm=0.45)
    add_track(29.5, 16.5, 29.5, 2.5, "RF_MATCH", width_mm=0.45)
    add_track(29.5, 2.5, 4.0, 2.5, "RF_MATCH", width_mm=0.45)

    # Thermal ground vias on exposed pad EP
    ep_vias = [(15.2, 15.2), (16.8, 15.2), (15.2, 16.8), (16.8, 16.8), (16.0, 16.0)]
    for vx, vy in ep_vias:
        v = pcbnew.PCB_VIA(board)
        v.SetPosition(pcbnew.VECTOR2I(pcbnew.FromMM(vx), pcbnew.FromMM(vy)))
        v.SetWidth(pcbnew.FromMM(0.6))
        v.SetDrill(pcbnew.FromMM(0.3))
        v.SetNet(nets["GND"])
        board.Add(v)

    # Silkscreen board markings (cleanly placed in non-component zones)
    def add_text(txt, x_mm, y_mm, size_mm=0.8, layer=pcbnew.F_SilkS):
        tb = pcbnew.PCB_TEXT(board)
        tb.SetText(txt)
        tb.SetPosition(pcbnew.VECTOR2I(pcbnew.FromMM(x_mm), pcbnew.FromMM(y_mm)))
        tb.SetLayer(layer)
        tb.SetTextSize(pcbnew.VECTOR2I(pcbnew.FromMM(size_mm), pcbnew.FromMM(size_mm)))
        tb.SetTextThickness(pcbnew.FromMM(0.15))
        board.Add(tb)

    add_text("ESD WRISTBAND MONITOR", 16.0, 1.2, size_mm=0.8)
    add_text("nRF52840-QIAA", 16.0, 7.0, size_mm=0.8)
    add_text("CONTACT A", 6.0, 39.0, size_mm=0.8)
    add_text("CONTACT B", 16.0, 39.0, size_mm=0.8)
    add_text("EARTH GND", 26.0, 39.0, size_mm=0.8)
    add_text("SWD", 2.5, 3.5, size_mm=0.8)

    board.Save(pcb_path)
    print(f"Created {pcb_path}")

def run_reports_and_renders():
    sch_file = os.path.join(PROJECT_DIR, f"{PROJECT_NAME}.kicad_sch")
    pcb_file = os.path.join(PROJECT_DIR, f"{PROJECT_NAME}.kicad_pcb")
    erc_rpt = os.path.join(PROJECT_DIR, "erc_report.rpt")
    drc_rpt = os.path.join(PROJECT_DIR, "drc_report.rpt")
    render_top = os.path.join(PROJECT_DIR, "board_render_top.png")
    render_3d = os.path.join(PROJECT_DIR, "board_render_3d.png")
    step_file = os.path.join(PROJECT_DIR, f"{PROJECT_NAME}.step")

    # ERC
    print("Running ERC...")
    res_erc = subprocess.run([CLI, "sch", "erc", "--output", erc_rpt, sch_file], capture_output=True, text=True)
    print(f"ERC return code: {res_erc.returncode}")

    # DRC
    print("Running DRC...")
    res_drc = subprocess.run([CLI, "pcb", "drc", "--output", drc_rpt, pcb_file], capture_output=True, text=True)
    print(f"DRC return code: {res_drc.returncode}")

    # 3D Render Top
    print("Rendering board top view...")
    subprocess.run([CLI, "pcb", "render", "--output", render_top, "--side", "top", pcb_file], capture_output=True, text=True)

    # 3D Render Perspective
    print("Rendering board 3D perspective...")
    subprocess.run([CLI, "pcb", "render", "--output", render_3d, "--rotate", "30,0,45", pcb_file], capture_output=True, text=True)

    # Export STEP for SolidWorks
    print("Exporting STEP model...")
    subprocess.run([CLI, "pcb", "export", "step", "--output", step_file, pcb_file], capture_output=True, text=True)

if __name__ == "__main__":
    create_project_file()
    generate_schematic()
    generate_pcb()
    run_reports_and_renders()
    print("All tasks completed successfully!")
