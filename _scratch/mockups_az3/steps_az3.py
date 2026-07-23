# -*- coding: utf-8 -*-
"""AZ Phase 3 - AZD8630 Affinity (CaptureSelect CH1-XL) DSP chromatography.
XStep plan: kind R=reuse existing SMPL/DE1 100, V=reuse-as-variant, N=new.
Only N and V carry mock-up content (form/cols/longtext); R are folder-only + a
compact reuse card in the EBR. Section = original MPR (MABR-0023643 / PN 8010457)."""
def v(x): return f'<span class="v">{x}</span>'
PB="Performed By*"

# Sec 14.9 AZD8630_ProteinA Method Overview - hardcoded in IV_INSTR (conditional
# header), not captured. Inline styles: instructions are injected raw into both
# the mock-up and the EBR card, which don't share a stylesheet.
_OV = [("3 CV","318 L/hr","Equilibration 1"),
       ("Step 9.13 / 9.16 / 9.10","318 L/hr","Load"),
       ("3 CV","318 L/hr","Equilibration 2"),
       ("3 CV","318 L/hr","Wash"),
       ("3 CV","318 L/hr","Equilibration 3"),
       ("N/A","239 L/hr","Elution &mdash; Collection Start: 37.5 mAU / Collection End: 37.5 mAU"),
       ("3 CV","318 L/hr","Strip 1"),
       ("1 CV","318 L/hr","Equilibration 4"),
       ("3 CV","318 L/hr","Strip 2"),
       ("1 CV","318 L/hr","Equilibration 5"),
       ("3 CV","318 L/hr","Strip 3")]
_TD = 'border:1px solid #b9bec4;padding:2px 8px;'
METHOD_OVERVIEW = (
  '<div style="font-weight:bold;margin:9px 0 4px;">AZD8630_ProteinA Method Overview</div>'
  '<table style="border-collapse:collapse;font-size:11px;margin-bottom:4px;width:auto;">'
  f'<tr style="background:#e8ebee;font-weight:bold;text-align:center;"><td style="{_TD}">Volumes</td>'
  f'<td style="{_TD}">Target Flowrate</td><td style="{_TD}">Step</td></tr>'
  + ''.join(f'<tr><td style="{_TD}text-align:center;">{a}</td>'
            f'<td style="{_TD}text-align:center;">{b}</td><td style="{_TD}">{c}</td></tr>'
            for a,b,c in _OV)
  + '</table>')

STEPS = [
 # ---------- A. Process Order Information ----------
 dict(folder="Order Header Details", title="Order Header Details", kind="R", section="Header",
   desc="Product/PN, process order numbers, recorded by — standard order header."),
 dict(folder="Signature Table", title="Signature Table", kind="R", section="Personnel ID",
   desc="Personnel identification: print name, signature, initials."),
 dict(folder="Display BOM", title="Display BOM", kind="R", section="Section 4",
   desc="Bill of Materials — equipment (skid PK-4500, meters, scale, mixer) and components/filters/bags."),
 dict(folder="Room and Equipment Assign", title="Room & Equipment Assign", kind="R", section="Section 4",
   desc="Assign room + equipment (AKTA skid, pH/cond meters, thermometer, floor scale, mixer, FIT) with calibration check."),
 dict(folder="Additional Manufacturing Supplies", title="Additional Manufacturing Supplies", kind="V", section="Section 4",
   reuses="SMPL: Additional Assembly (with the Z_PICONS Goods Issue process message)",
   instructions=('If additional materials (filter, bag, assembly, etc.) are used during processing, verify the '
     'material is acceptable per Section 4 and record its information; document the reason for the change in the '
     'Comments Section. Enter the Part No. &mdash; an input validation displays the Material Description. Enter the '
     'Batch No. &mdash; the Exp. Date is auto-populated. Serial No. and Autoclave Assembly ID / Exp. Date are '
     'recorded manually. <b>SAP consumption is posted automatically by the Goods Issue process message (Z_PICONS, '
     'movement type 261) &mdash; no manual "SAP Consumption" field is required.</b>'),
   cols=["MPR Step No.","Part No.","=Material Description","Batch No.","=Exp. Date","Serial No.",
     "Autoclave Assembly ID","Autoclave Exp. Date",PB],
   witness_label="Witnessed By", w=2200),

 dict(folder="Solution Buffer Batch Record", title="Solution / Buffer Batch Record", kind="V", section="Section 5",
   instructions=('Record the batch number and expiration date for each process solution used in the chromatography '
     f'run: Equilibration ({v("8004949")}), Wash ({v("8004950")}), Elution ({v("8010534")}), Strips '
     f'({v("8008812 / 8008813 / 8006409")}) and Column Storage ({v("8004953")}). Enter the Batch No.; the Exp. '
     'Date auto-populates via input validation.'),
   cols=["Solution / Step","Part No.","Batch No.","=Exp. Date",PB], witness_label="Verified By",
   rowdata=[{"Solution / Step":"Equilibration (50 mM Tris, pH 7.4)","Part No.":"8004949"}], w=1700),

 dict(folder="Additional Solution Batches Used", title="Additional Solution Batches Used", kind="V", section="Section 5",
   instructions=('If a solution batch is replaced during processing, record the applicable step, part number, new '
     'batch number and expiration date. Ensure the new solution is the same part number as the one being replaced; '
     'document the change in the Comments Section. Enter the Batch Number; the Exp. Date auto-populates via input '
     'validation.'),
   cols=["Applicable Step No.","Part Number","Batch Number","=Exp. Date",PB], witness_label="Witnessed By", w=1700),

 dict(folder="Process Notes", title="Process Notes", kind="V", section="Section 6", longtext=True,
   signoffs=["Reviewed By"], reuses="Long Text Instructions (DE2 903)",
   instructions=('General process notes for the CaptureSelect CH1-XL chromatography step &mdash; review before '
     'processing:'
     '<ul>'
     '<li>All activities are performed at 15 &ndash; 27&nbsp;&deg;C.</li>'
     '<li>For calculations, assume 1 L = 1 kg and 1 mL = 1 g unless otherwise noted. PK-4500 absorbance is in mAU; '
     'mAU = OD &times; 0.15 &times; 1000.</li>'
     '<li>Target linear velocity is 200 cm/hr (150 cm/hr for Elution). Alert limits &plusmn;5% of target; NOR +10%.</li>'
     '<li>Flow-rate ranges are for steady-state operation and do not consider pump ramping; temporary flowrate '
     'excursions are acceptable.</li>'
     '<li>Verify all solutions, raw materials and standards are within expiration prior to use.</li>'
     '<li>When an equipment ID is written in the MPR, the operator confirms they have visually inspected it and '
     'verified calibration prior to use.</li>'
     '<li>If PAUSE is pressed on the skid HMI the pumps stop &mdash; document the reason in the Comments Section and '
     'press CONTINUE to resume.</li>'
     '<li>During Load, "next breakpoint" may be used to proceed when the load is complete (note it in the MPR); any '
     'other use requires a supervisor/designee signature and a reason in the Comments Section. Does not apply to '
     'Elution.</li>'
     '<li>The process may be run manually if the automated chromatography recipe is not functioning correctly.</li>'
     '<li>Non-routine samples requested by MEMO are recorded in Attachment 2.</li>'
     '<li>All parameters are Targets / Alert Limits unless otherwise noted. When alert limits are exceeded, contact '
     'the Supervisor and Downstream Tech Transfer and document any actions in the Comments Section.</li>'
     '<li>To avoid over-pressurization, flow rates may be lowered manually or as part of the method; record adjusted '
     'flowrates in Attachment 4.</li>'
     '</ul>')),

 # ---------- B. AKTA Kit Install & WFI Charge ----------
 dict(folder="Data Logger Verification", title="Data Logger Verification", kind="R", section="Section 7",
   desc="Verify the data logger is on and the PK-4500 process trend is activated (per day, first cycle)."),
 dict(folder="Record Process Room", title="Record Process Room", kind="R", section="Section 7",
   desc="Record the room number where the process occurs."),

 dict(folder="WFI Container Setup and Charge", title="WFI Container Setup & Charge", kind="N", section="Section 7.4 / 7.6",
   instructions=('Set up the Day 1 / Day 2 WFI collection vessel per SOP-0080854. Inspect the collection vessel, '
     'then record the bag and WFI filter as separate lines in the table below &mdash; select the Item from the '
     'dropdown (Bag / Filter &mdash; a restricted-value CT04 characteristic), enter each Part No. and Batch No. '
     '(the Exp. Date auto-populates via input validation) and sign Performed By per line. Each line is '
     'consumed via the Goods Issue process message (Z_PICONS, mvt 261). Below the table, record the WFI valve ID, '
     f'verify the WFI port is flushed and charge WFI into the vessel; stamp the charge date/time (expiration is '
     f'{v("24 hours")} from charge, auto-calculated).'),
   cols=["%Item","Part No.","Batch No.","=Exp. Date",PB], rowdata=[{"%Item":"Bag"}], witness=False,
   footer_fields=[("WFI Valve ID","r"),("WFI Charge Date & Time","dt"),
     ("WFI Expiration Date & Time (Charge + 24 h)","o"),("Recorded By","r"),("Verified By","r")], w=1700),

 dict(folder="AKTA Kit Install and Component Test", title="AKTA Kit Install & Component Test", kind="V", section="Section 7",
   reuses="SMPL: Filter Integrity Test (+ Skid ID)",
   instructions=('Obtain and install the AKTA Ready kit on skid PK-4500 per SOP-0107212. Select the Kit Required '
     'from the dropdown and enter its Part No. (the Kit Description auto-populates via input validation). Press '
     'Select Buffer to retrieve the buffer part number, then enter the Buffer Batch No. (the Exp. Date '
     f'auto-populates). Run the Flow Kit Installation with Component Test (uses {v("5 L of 8004948")} per attempt); '
     'record each attempt from the Pass / Fail / N-A dropdown and the buffer volume used. The kit and buffer are '
     'consumed via the Goods Issue process message (Z_PICONS, mvt 261).'),
   header_fields=[("Select Buffer","b"),("Buffer Part No.","o"),("Buffer Batch No.","r"),("Buffer Exp. Date","o")],
   cols=["%Kit Required","Part No.","=Kit Description","Test Program","%Test 1","%Test 2 (i/a)","%Test 3 (i/a)",
     "Buffer Volume Used (L)","Skid ID",PB],
   rowdata=[{"%Kit Required":"AKTA High Flow Kit","Skid ID":"PK-4500"}], w=2400),

 # ---------- C. Column & Calculations ----------
 dict(folder="Chromatography Column Information", title="Chromatography Column Information", kind="N", section="Section 8.1",
   instructions=('Obtain the CaptureSelect CH1-XL column and the Column Packing Data Sheet (CPDS, FORM-0064069). '
     'Verify the column was packed with CaptureSelect CH1-XL for AZD8630. Record the Column ID, media name, CPDS '
     'lot/part number, bed volume, inlet/differential pressure and bed height from the CPDS (all entered manually '
     'from the CPDS). Assign the Column Pressure Rating as the Inlet Pressure and the Packing Pressure as the '
     'Differential Pressure. The column is consumed via the Goods Issue process message (Z_PICONS, mvt 261).'),
   form=[("Column ID","r"),("Chromatography Media Name","r"),("CPDS Lot No.","r"),("CPDS Part Number","r"),
     ("Column Bed Volume (L)","r"),("Column Inlet Pressure (bar)","r"),("Column Differential Pressure (barD)","r"),
     ("Column Bed Height (16-22 cm)","r"),("Performed By","r"),("Witnessed By","r")], w=1500),

 dict(folder="Column Pressure and Cycle Calculations", title="Column Pressure & Cycle Calculations", kind="R", section="Section 8.2, 9",
   desc="Calc chain: inlet pressure max (x0.9), total protein, max load (15 g/L/cycle), number of cycles, load volume per cycle."),
 dict(folder="Column and Method Verification", title="Column & Method Verification", kind="R", section="Section 8.3",
   desc="Verify from the column logbook it was sanitized/stored correctly and the AZD8630_ProteinA method was wet-tested & ran as expected."),
 dict(folder="Load Concentration and Volume", title="Load Concentration & Volume", kind="V", section="Section 9.1",
   instructions=('Obtain the protein concentration and net volume of the Conditioned Medium (CM, PN 8010441) for '
     'each bag from the AZD8630 Pod Harvest MPR (MABR-0023642) and record them below with the DLIMS project and '
     'sample numbers (one row per CM bag; values carry forward from Pod Harvest). The CM is consumed via the Goods '
     'Issue process message (Z_PICONS, mvt 261).'),
   cols=["CM Product Net Volume (kg = L)","CM Concentration (g/L)","DLIMS Project Number",
     "DLIMS Sample Number",PB], idx_label="Bag No.", w=2000),

 # ---------- D. Product Collection & Filter Setup ----------
 dict(folder="Estimated VI Product Volume", title="Estimated VI Product Volume", kind="N", section="Section 10.1",
   reuses="new SMPL: 4 Variable Calc (based on SMPL: Three Variable Calc)",
   instructions=('Calculate the estimated Viral Inactivation (VI) product volume &mdash; a 4-variable calculation '
     '(reuses the Three Variable Calc layout, extended to four variables). Column Bed Volume carries from the '
     'Column Information step and Number of Cycles from the Chromatography Calculations; enter 2.3 CV/cycle for '
     'Estimated Product Volume; Estimated VI Additions is the standard 1.10. The result sizes the product '
     'collection vessel.'),
   cols=["Column Bed Volume (L/CV)","@OP:×","Estimated Product Volume (CV/cycle)","@OP:×","Number of Cycles",
     "@OP:×","Estimated VI Additions","@OP:=","=Estimated VI Product Volume (L)",PB],
   rowdata=[{"Estimated VI Additions":"1.10"}], index=False, add_row=False, witness_label="Witnessed By", w=2200),

 dict(folder="Product Collection Vessel Setup", title="Product Collection Vessel Setup", kind="N", section="Section 10.5",
   instructions=('Obtain an appropriately sized product vessel based on the estimated VI product volume. Press Get '
     'Equipment to select the scale/balance &mdash; its ID and Calibration Due Date are retrieved. Record the tare '
     'weight and the collection bag information (enter the Batch No.; the Exp. Date auto-populates). Indicate which '
     'attachments are connected to the LevTech bag during the vessel tare (Mixer Drive / Top Base / Magnetic Clamp; '
     'N/A if no LevTech bag). Label the vessel "AZD8630", "CaptureSelect CH1-XL Product". The collection bag is '
     'consumed via the Goods Issue process message (Z_PICONS, mvt 261).'),
   form=[("Get Equipment","b"),("Scale / Balance ID","o"),("Calibration Due Date","o"),
     ("Tare Weight of Product Vessel (kg)","r"),
     ("Collection Bag Part No.","r"),("Collection Bag Batch No.","r"),("Collection Bag Exp. Date","o"),
     ("Mixer Drive Attached?","d"),("Top Base Attached?","d"),("Magnetic Clamp Attached?","d"),
     ("Recorded By","r"),("Witnessed By","r")], w=1500),
 dict(folder="Product Filter Information", title="Product Filter Information", kind="V", section="Section 10.6",
   reuses="SMPL: Additional Assembly (same as Additional Manufacturing Supplies, without MPR Step No.)",
   instructions=('Record the product filter(s) attached to the collection vessel (one line per filter, Day 1 / '
     'Day 2). Enter the Part No. &mdash; an input validation displays the Material Description. Enter the Batch No. '
     '&mdash; the Exp. Date is auto-populated. Serial No. and Autoclave Assembly ID / Exp. Date are recorded '
     'manually. SAP consumption is posted automatically by the Goods Issue process message (Z_PICONS, movement '
     'type 261).'),
   cols=["Part No.","=Material Description","Batch No.","=Exp. Date","Serial No.","Autoclave Assembly ID",
     "Autoclave Exp. Date",PB], idx_label="Day #", witness_label="Witnessed By", w=2200),
 dict(folder="Depth Filter Sizing Calculation", title="Depth Filter Sizing Calculation", kind="V", section="Section 11.1",
   reuses="SMPL: Three Variable Calc (one instance per day)",
   instructions=('Calculate the C0HC depth-filter surface area needed for the day &mdash; reuses the Three '
     'Variable Calc XStep, run as one instance per day (Day 1 uses Bag 1 volume, Day 2 uses Bag 2): CM Volume per '
     'Day &divide; C0HC Capacity (500 L/m²) = C0HC Surface Area Needed.'),
   cols=["CM Volume per Day (L)","@OP:÷","C0HC Capacity (L/m²)","@OP:=","=C0HC Surface Area Needed (m²)",PB],
   rowdata=[{"C0HC Capacity (L/m²)":"500"}], index=False, add_row=False, witness_label="Witnessed By", w=2000),

 dict(folder="Depth Filter Count Calculation", title="Depth Filter Count Calculation", kind="V", section="Section 11.2",
   reuses="SMPL: Three Variable Calc (one instance per day)",
   instructions=('Calculate the number of C0HC depth-filter units to install for the day (round up to the next '
     'whole number) &mdash; reuses the Three Variable Calc XStep, one instance per day: C0HC Surface Area Needed '
     '(from the Depth Filter Sizing Calculation) &divide; C0HC Filter Area (1.1 m²) = Number of C0HC Filters.'),
   cols=["C0HC Surface Area Needed (m²)","@OP:÷","C0HC Filter Area (m²)","@OP:=","=Number of C0HC Filters (round up)",PB],
   rowdata=[{"C0HC Filter Area (m²)":"1.1"}], index=False, add_row=False, witness_label="Witnessed By", w=2000),

 dict(folder="Depth Filter Material Setup", title="Depth Filter Material Setup", kind="R", section="Section 11.3",
   desc="Record C0HC filters and POD adaptor kits used (Description/Qty/Batch/Exp/Serial + SAP consumption)."),

 dict(folder="Total Surface Area Calculation", title="Total Surface Area Calculation", kind="V", section="Section 11.4",
   reuses="SMPL: Three Variable Calc (one instance per day)",
   instructions=('Calculate the total surface area of the C0HC units &mdash; reuses the Three Variable Calc XStep, '
     'one instance per day: Number of C0HC Filters &times; Surface Area per Unit (1.1 m²) = Total Surface Area of '
     'C0HC Units.'),
   cols=["Number of C0HC Filters","@OP:×","Surface Area per Unit (m²)","@OP:=","=Total Surface Area of C0HC Units (m²)",PB],
   rowdata=[{"Surface Area per Unit (m²)":"1.1"}], index=False, add_row=False, witness_label="Witnessed By", w=2000),

 dict(folder="Depth Filter Flush Flowrate Calculation", title="Depth Filter Flush Flowrate Calculation", kind="V", section="Section 11.5",
   reuses="SMPL: Three Variable Calc (one instance per day)",
   instructions=('Calculate the flowrate range to flush the depth filtration units &mdash; reuses the Three '
     'Variable Calc XStep, one instance per day: Flux &times; Total Surface Area of C0HC Units (Step 11.4) = Flow '
     'Rate Range. Flux is 500 (min) / 600 (target) / 700 (max) LMH (NOR allows below 500 LMH if the equipment '
     'cannot meet the minimum).'),
   cols=["Flux (LMH)","@OP:×","Total Surface Area of C0HC Units (m²)","@OP:=","=Flow Rate Range (L/hr)",PB],
   rowdata=[{"Flux (LMH)":"500 / 600 / 700"}], index=False, add_row=False, witness_label="Witnessed By", w=2000),

 dict(folder="Depth Filter Hold-Up Calculation", title="Depth Filter Hold-Up Calculation", kind="V", section="Section 11.6",
   reuses="SMPL: Three Variable Calc (one instance per day)",
   instructions=('Calculate the hold-up volume of the installed depth filters &mdash; reuses the Three Variable '
     'Calc XStep, one instance per day: Number of C0HC Filters &times; Internal Void Volume per 1.1 m² Filter '
     '(10.3 L) = Hold-Up Volume of Installed Depth Filters.'),
   cols=["Number of C0HC Filters","@OP:×","Internal Void Volume per Filter (L)","@OP:=","=Hold-Up Volume of Installed Filters (L)",PB],
   rowdata=[{"Internal Void Volume per Filter (L)":"10.3"}], index=False, add_row=False, witness_label="Witnessed By", w=2000),

 dict(folder="Minimum WFI Flush Volume Calculation", title="Minimum WFI Flush Volume Calculation", kind="V", section="Section 11.7",
   reuses="SMPL: Three Variable Calc (one instance per day)",
   instructions=('Calculate the minimum volume of WFI to flush the depth filtration units &mdash; reuses the '
     'Three Variable Calc XStep, one instance per day: WFI Min (105 L/m²) &times; Total Surface Area of C0HC Units '
     '(Step 11.4) = Minimum WFI Flush Volume.'),
   cols=["WFI Min (L/m²)","@OP:×","Total Surface Area of C0HC Units (m²)","@OP:=","=Minimum WFI Flush Volume (L)",PB],
   rowdata=[{"WFI Min (L/m²)":"105"}], index=False, add_row=False, witness_label="Witnessed By", w=2000),

 dict(folder="Minimum Buffer Flush Volume Calculation", title="Minimum Buffer Flush Volume Calculation", kind="V", section="Section 11.8",
   reuses="new SMPL: 4 Variable Calc (based on SMPL: Three Variable Calc), one instance per day",
   instructions=('Calculate the minimum volume of Equilibration Buffer (8004949: 50 mM Tris, pH 7.4) to flush the '
     'depth filtration units &mdash; reuses the new 4 Variable Calc XStep (mixed &times; and + operators), one '
     'instance per day: Buffer Min (30 L/m²) &times; Total Surface Area of C0HC Units (Step 11.4) + Hold-Up Volume '
     'of Installed Depth Filters (Step 11.6) = Minimum Buffer Flush Volume.'),
   cols=["Buffer Min (L/m²)","@OP:×","Total Surface Area of C0HC Units (m²)","@OP:+",
     "Hold-Up Volume of Installed Filters (L)","@OP:=","=Minimum Buffer Flush Volume (L)",PB],
   rowdata=[{"Buffer Min (L/m²)":"30"}], index=False, add_row=False, witness_label="Witnessed By", w=2300),

 dict(folder="Record Meter ID", title="Record Meter ID", kind="R", section="Section 11.9",
   reuses="SMPL: Record Text Value (DE1 100)",
   desc="Confirm the pH/conductivity meter is standardized per SOP-0080297; record the Meter ID (Day 1 only). Reuses SMPL: Record Text Value."),
 dict(folder="Record Thermometer ID", title="Record Thermometer ID", kind="R", section="Section 11.10",
   reuses="SMPL: Record Text Value (DE1 100)",
   desc="Confirm the thermometer is within its calibration interval; record the Thermometer ID (Day 1 only). Reuses SMPL: Record Text Value."),

 dict(folder="Pod Holder and Pressure Sensors", title="Pod Holder & Pressure Sensors", kind="N", section="Section 11.11",
   instructions=('Obtain and document the depth-filter Pod Holder ID and the inlet/outlet pressure sensors used '
     '(Day 1 / Day 2). Record the Pod Holder ID above the table; for each pressure sensor select Inlet or Outlet '
     'and record its Part No. and Batch No. (Exp. Date auto-populates), then sign Performed By &mdash; signing a '
     'line triggers the Goods Issue (Z_PICONS, mvt 261) consumption of that sensor. Press Get Pendotech to '
     'retrieve the Pendotech ID and its Calibration Due Date.'),
   header_fields=[("Pod Holder ID","r")],
   cols=["%Inlet / Outlet","Part No.","Batch No.","=Exp. Date",PB],
   rowdata=[{"%Inlet / Outlet":"Inlet"}],
   footer_fields=[("Get Pendotech","b"),("Pendotech ID","o"),("Pendotech Calibration Due Date","o")],
   witness_label="Witnessed By", w=2000),

 dict(folder="Install Depth Filtration Units", title="Install Depth Filtration Units", kind="R", section="Section 11.12",
   reuses="Long Text Instructions (DE2 903)",
   desc="Install the depth filtration units into the skid column position per SOP-0107204 (POD inlet/outlet T's, pressure-sensor connections, bypass line, pinch-clamp flow) and sign off (Day 1 / Day 2). Reuses Long Text Instructions."),

 # ---------- E. Depth Filter Flush & Skid Connections ----------
 dict(folder="Depth Filter Pre-Flush Connections", title="Depth Filter Pre-Flush Connections", kind="R", section="Section 12.1",
   reuses="Long Text Instructions (DE2 903)",
   desc=("Make the depth-filter pre-flush connections per the recipe (Day 1 / Day 2): Inlet 2 to the Equilibration "
     "buffer (8004949: 50 mM Tris, pH 7.4), Inlet 1 to WFI, and Outlet 1 to Waste. Sign off. Reuses Long Text "
     "Instructions."),
   ),
 dict(folder="Depth Filter Flush", title="Depth Filter Pre-Flush / Flush", kind="V", section="Section 12.2 / 12.3",
   reuses="SMPL: Additional Assembly (Equil Flush line carries the Z_PICONS Goods Issue)",
   instructions=('With the pre-flush connections made per Step 12.1 (Inlet 2: 8004949 50 mM Tris; Inlet 1: WFI; '
     'Outlet 1: Waste), flush the depth-filter pods per SOP-0080429 &mdash; bleed the vent valves first. For each '
     'flush, perform a Manual Run on the AKTA skid (flow paths method-driven; Alarm PT111 High 3.4 bar, Delta 1.3 '
     'bar; flow 25% until bled, then target per Step 11.5) labelled "Batch ID: PartNumber BatchNumber '
     'DepthFilterFlush Date", and record the Batch ID and the POD flush volume: the WFI Flush must be '
     f'{v("&ge; Step 11.7")} and the Equilibration Flush {v("&ge; Step 11.8")}. Adjust flow to stay under the '
     'pressure alarms. The Equilibration buffer flush is consumed via the Goods Issue process message (Z_PICONS, '
     'mvt 261). One instance per processing day.'),
   cols=["Flush Step","Batch ID","Flush Volume (L)",PB],
   rowdata=[{"Flush Step":"Depth Filter WFI Flush"}], idx_label="Day #",
   witness_label="Witnessed By", w=1800),

 # ---------- Skid Connections (Section 13) ----------
 dict(folder="Skid pH Probe Standardization", title="Skid pH Probe Standardization", kind="V", section="Section 13.1",
   reuses="SMPL: Additional Assembly (with the Z_PICONS Goods Issue process message)",
   instructions=('Verify the chromatography skid pH probe has been user-standardized per SOP-0107212 and record the '
     'probe information. Enter the Batch No. &mdash; the Exp. Date auto-populates via input validation. The pH probe '
     f'({v("6003953")}) is consumed via the Goods Issue process message (Z_PICONS, mvt 261). One instance per '
     'processing day.'),
   cols=["Part No.","=Material Description","Batch No.","=Exp. Date",PB],
   rowdata=[{"Part No.":"6003953"}], idx_label="Day #", witness_label="Witnessed By", w=1900),

 dict(folder="Skid Buffer Inlet Connections", title="Skid Buffer Inlet Connections", kind="R", section="Section 13.2-13.8",
   reuses="Long Text Instructions (DE2 903)",
   desc=("Connect the process buffers to the chromatography-skid inlets per SOP-0107212 (Inlet 1: Conditioned Medium "
     "8010441 Load; Inlet 2: 8004949 Equilibration 1-5; Inlet 3: 8004950 Wash; Inlet 4: 8010534 Elution; Inlet 5: "
     "8008812 Strip 1; Inlet 6 via Y-connector: 8008813 Strip 2 / 8006409 Strip 3). Set the Inlet 6 Y-leg clamps "
     "(8008813 Open, 8006409 Closed) and, for a 1-day 2-bag process, connect both CM bags to Inlet 1 with a Y. "
     "Day 1 / Day 2 sign-off. Reuses Long Text Instructions."),
   ),

 dict(folder="Column Guard Filter", title="Column Guard Filter", kind="V", section="Section 13.9",
   reuses="SMPL: Additional Assembly (with the Z_PICONS Goods Issue process message)",
   instructions=('Obtain and install the column guard filter (preferred: 30&Prime; SHC filter '
     f'{v("4100987")}; does not need to be autoclaved) &mdash; inlet to the POD outlet T, outlet to the column '
     'tubing inlet; adjust both T pinch-clamps to bypass the POD(s). Enter the Part No. (Material Description '
     'auto-populates) and Batch No. (Exp. Date auto-populates), and record the Serial No. The guard filter is '
     'consumed via the Goods Issue process message (Z_PICONS, mvt 261). One instance per processing day.'),
   cols=["Part No.","=Material Description","Batch No.","=Exp. Date","Serial No.",PB],
   rowdata=[{"Part No.":"4100987"}], idx_label="Day #", witness_label="Witnessed By", w=2000),

 # ---------- F. CaptureSelect Chromatography Run ----------
 dict(folder="Pre-Cycle Setup Verification", title="Pre-Cycle Setup Verification", kind="R", section="Section 14.1",
   desc="Verify CM held ≥12 h at 2-8 °C; column connected; guard-filter vent open, column inlet closed, bleed open, outlet open; product vessel connected (per cycle)."),
 dict(folder="POD Chase Volume Calculation", title="POD Chase Volume Calculation", kind="V", section="Section 14.5",
   reuses="SMPL: Calc Three Columns",
   instructions=('Calculate the POD chase volume &mdash; reuses the SMPL: Calc Three Columns XStep (Value&nbsp;1 '
     '&times; Value&nbsp;2 = Result), run as one instance per processing day: Number of C0HC Filters (Step 11.3) '
     '&times; POD Hold-Up Volume (10.6&nbsp;L) = POD Chase Volume.'),
   cols=["Number of C0HC Filters","@OP:×","POD Hold-Up Volume (L)","@OP:=","=POD Chase Volume (L)",PB],
   rowdata=[{"POD Hold-Up Volume (L)":"10.6"}], index=False, add_row=False, witness_label="Witnessed By", w=2000),

 dict(folder="Meter Standardization", title="Meter Standardization", kind="R", section="Section 14.6-14.7",
   reuses="SMPL: Record Text Value (DE1 100)",
   desc=("Confirm the thermometer is within its calibration interval and record the Thermometer ID; confirm the pH "
     "meter is standardized between pH 4.0 and 10.0 and the conductivity meter is standardized per SOP-0080297, and "
     "record the Meter ID. Reuses SMPL: Record Text Value."),
   ),

 dict(folder="Chromatography Method Parameters", title="Chromatography Method Parameters", kind="N", section="Section 14.9",
   instructions=('Initiate the AZD8630_ProteinA method per SOP-0107212, document the variables below and input them '
     'into the method. Bed Volume and Differential Pressure carry from Step 8.1, Inlet Pressure Max from Step 8.2, '
     f'and Load Volume from Step 9.13 ({v("Day 1 of 2")}) / 9.16 ({v("Day 2 of 2")}) / 9.10 '
     f'({v("both bags in one day")}). If a CPDS value exceeds the skid rating, record the skid maximum instead '
     '(5 bar / 4 barD).'
     + METHOD_OVERVIEW),
   cols=["=Bed Volume (L)","=Inlet Press. Max (bar)","=Diff. Press. (barD)","=Load Volume (L)",PB],
   idx_label="Cycle #", witness_label="Verified By", w=1800),

 dict(folder="Chromatography Method Start", title="Chromatography Method Start", kind="N", section="Section 14.13-14.14",
   instructions=('Start the AZD8630_ProteinA method per SOP-0107212. For each cycle, enter the batch Name ID '
     f'(Format: {v("PartNumber_ProductBatchNumber_Cycle#_AZD8630_ProteinA_Date")}) and stamp the start time. '
     f'Allowed during the run: Flowrate {v("302-334 L/hr")} (Elution {v("226-251 L/hr")}), NOR 0.0-350 L/hr; '
     f'Process CV {v("-0.1 to +1.0 CV")} from target. Verify the flow paths match the recipe &mdash; contact area '
     'management immediately on any discrepancy. Record any lowered flowrate in Attachment 4.'),
   cols=["Cycle Name ID","@STAMP","~Start Date","~Start Time",PB],
   idx_label="Cycle #", witness_label="Witnessed By", w=1800),

 dict(folder="Phase Execution and Sign-off", title="Phase Execution & Sign-off", kind="V", section="Section 14", longtext=True,
   signoffs=["Performed By","Witnessed By"],
   instructions=('Execute the AZD8630_ProteinA method phases per cycle and sign off. Method sequence (Inlet / Flow / '
     'Volume are method-driven):'
     '<ul>'
     '<li>Skid Flush, Column Guard Filter Purge, Column Bleed Line Purge (8004949).</li>'
     '<li>Equilibration 1 (3 CV) &rarr; Load (POD inline) &rarr; Equilibration 2 (3 CV).</li>'
     '<li>Wash (8004950, 3 CV) &rarr; Equilibration 3 (3 CV).</li>'
     '<li>Elution (8010534, collect 37.5&rarr;37.5 mAU) &rarr; Strip 1 (8008812) &rarr; Equilibration 4.</li>'
     '<li>Strip 2 (8008813) &rarr; Equilibration 5 &rarr; Strip 3 (8006409).</li></ul>'
     'Reposition POD clamps inline/bypass when the skid pauses; press CONTINUE. Record any PAUSE / flow-rate change '
     'in the Comments / Adjusted Flowrate attachments.')),

 dict(folder="Equilibration Effluent Results", title="Equilibration Effluent Results", kind="V", section="Section 14.15",
   reuses="SMPL: Solution Summary - Data Recording (range-validated variant)",
   instructions=('Confirm the equilibration effluent is in range using an offline meter and record the pH, '
     'conductivity and temperature for each cycle (after 2 CVs of Equilibration 1). Get the offline meter '
     '&mdash; the Equipment ID and Description auto-populate. Verify the Offline pH is within '
     f'{v("7.2 - 7.6")} (NOR {v("7.0 - 7.8")}) and the Temperature within {v("15 - 25 &deg;C")}; record the '
     'CV at which each reading was taken. <b>Contact the area supervisor/designee if a result is out of '
     'specification.</b> One row per cycle; add rows as needed.'),
   header_fields=[("Get Equipment","b"),("Equipment ID","o"),("Equipment Description","o")],
   # three "UoM" output columns (trailing spaces keep the dict keys distinct; all display "UoM")
   cols=["Offline pH","=UoM","Conductivity","=UoM ","Temperature","=UoM  ","CV Where Taken",PB],
   rowdata=[{"=UoM":"pH","=UoM ":"mS/cm","=UoM  ":"°C"}],
   idx_label="Cycle #", witness_label="Witnessed By", w=1900),
 dict(folder="Column Effluent Sample Date and Time", title="Column Effluent Sample Date & Time", kind="N", section="Section 14.16",
   instructions=('Record the date and time the Affinity Chromatography Column Effluent sample is removed, per '
     'processing day (first cycle of each day only). Press Get Date/Time to stamp the current Date and Time, then '
     'sign Performed By. Add one row per processing day.'),
   cols=["@BTN:Get Date/Time","=Date","=Time",PB],
   idx_label="Day #", witness_label="Witnessed By", w=1400),
 dict(folder="Column Effluent Sampling", title="Column Effluent Sampling", kind="R", section="Section 14.17",
   desc="First cycle of each day: sample Affinity Column Effluent (8010457-20-1 Day 1 / -20-2 Day 2) per Attachment 1, stamp date/time, aliquot, label, submit to DLIMS."),

 dict(folder="Load Recording", title="Load Recording", kind="N", section="Section 14.20",
   instructions=('Load the Conditioned Medium (8010441) onto the column (Inlet 1, 318 L/hr). For each cycle, stamp '
     'the Load start and end times and record the Actual Volume Loaded from the skid totalizer. The total load '
     'volume is summed across all cycles.'),
   cols=["@START","~Load Start Time","@END","~Load End Time","Vol Loaded /Totalizer (L)",PB],
   footer_fields=[("Total Load Volume, All Cycles (L)","o")],
   idx_label="Cycle #", witness_label="Witnessed By", w=1900),

 dict(folder="Elution Collection", title="Elution Collection", kind="N", section="Section 14.29-14.30",
   instructions=('Collect the elution peak into the product vessel (8010534: 25 mM Sodium Acetate, pH 3.5, 239 L/hr). '
     f'Collection begins when the absorbance reaches {v("37.5 mAU")} and the outlet switches to Outlet 4; bleed air '
     f'from the product filter at the start. When the UV returns to {v("37.5 mAU")} the outlet switches back to '
     'Outlet 1. Record the product net weight / volume from the Outlet 4 totalizer (or weigh the eluate if the '
     'totalizer is unavailable) and stamp the Elution End Time, per cycle.'),
   cols=["Net Wt / Vol (kg=L)","@END","~Elution End Time",PB],
   idx_label="Cycle #", witness_label="Witnessed By", w=1900),

 dict(folder="Strip 2 Effluent Results", title="Strip 2 Effluent Results", kind="V", section="Section 14.37-14.38",
   reuses="SMPL: Solution Summary - Data Recording (range-validated variant)",
   instructions=('Per cycle, verify the Strip 2 effluent conductivity is within the NOR of '
     f'{v("2.2 - 3.8 mS/cm")} and the temperature is in range {v("15 - 27 &deg;C")} using an offline meter '
     '(Get Equipment &mdash; the Equipment ID and Description auto-populate). Also record the Inlet 6 totalizer '
     'volume at Strip 2 completion (transcribed to Attachment 5: Buffer Totalizer Volumes). <b>Contact a '
     'supervisor if the conductivity is out of specification.</b> One row per cycle.'),
   header_fields=[("Get Equipment","b"),("Equipment ID","o"),("Equipment Description","o")],
   cols=["Conductivity","=UoM","Temperature","=UoM ","Inlet 6 Totalizer Vol (L)",PB],
   rowdata=[{"=UoM":"mS/cm","=UoM ":"°C"}],
   idx_label="Cycle #", witness_label="Witnessed By", w=1850),
 dict(folder="Strip 3 Effluent Results", title="Strip 3 Effluent Results", kind="V", section="Section 14.43-14.44",
   reuses="SMPL: Solution Summary - Data Recording (range-validated variant)",
   instructions=('Confirm the pH meter has been standardized between pH 2.0 and 7.0 per SOP-0080297 (Get Equipment '
     '&mdash; the Equipment ID/Description auto-populate). Per cycle, verify the Strip 3 effluent pH is '
     f'{v("&le; 2.4")} (NOR {v("&le; 2.5")}) and the temperature is in range {v("15 - 27 &deg;C")} using an '
     'offline meter. <b>Contact a supervisor if the pH is out of specification.</b> One row per cycle.'),
   header_fields=[("Get Equipment","b"),("Equipment ID","o"),("Equipment Description","o")],
   cols=["Offline pH","=UoM","Temperature","=UoM ",PB],
   rowdata=[{"=UoM":"pH","=UoM ":"°C"}],
   idx_label="Cycle #", witness_label="Witnessed By", w=1700),

 # ---------- G. Column Storage ----------
 dict(folder="Column Storage Buffer and Parameters", title="Column Storage Buffer & Parameters", kind="N", section="Section 15.1-15.5",
   instructions=('Record the Column Storage buffer (8004953: 2% (v/v) benzyl alcohol, 100 mM sodium acetate, pH 5.0) '
     '&mdash; enter the Batch No. (the Exp. Date auto-populates via input validation) &mdash; and connect it to '
     'Inlet 6. Initiate the AZD8630 Affinity Storage method per SOP-0107212 and verify the method parameters carried '
     'from Sections 8 and 9 (bed volume, inlet pressure max, differential pressure; flow 318 L/hr, NOR 0.0-350 '
     'L/hr). Record the Name ID and stamp the storage Start Date & Time. The storage buffer is consumed via the '
     'Goods Issue process message (Z_PICONS, mvt 261). One instance per processing day.'),
   form=[("Storage Buffer PN (8004953)","o"),("Storage Buffer Batch No.","r"),("Storage Buffer Exp. Date","o"),
     ("Column Bed Volume (L)","o"),("Inlet Press. Max (bar)","o"),("Diff. Pressure (barD)","o"),
     ("Storage Flow Rate (L/hr)","r"),("Storage Method Name ID","r"),("Storage Start Date & Time","dt"),
     ("Performed By","r"),("Verified By","r")], w=1600),

 dict(folder="Sanitization Hold and Pre-Storage Equilibration", title="Sanitization Hold & Pre-Storage Equilibration", kind="N",
   section="Section 14.48 / 15.6",
   instructions=('After Strip 3 of the final cycle, hold the column for column sanitization with 8006409 (120 mM '
     f'phosphoric acid, 167 mM acetic acid, 2.2% benzyl alcohol), NOR {v("30-120 min")} (target 35). The Hold End '
     'Time is when the pump starts for Pre-Storage Equilibration (8004949: 50 mM Tris, pH 7.4). Stamp the '
     'Sanitization Hold Start Time (Step 14.48) and the Hold End Time; the Hold Duration is calculated '
     '(End &minus; Start). One instance per processing day.'),
   form=[("Sanitization Hold Start Time","t"),("Hold End Time","t"),
     ("Hold Duration (min)","o"),("Performed By","r"),("Witnessed By","r")], w=1600),

 dict(folder="Column Storage Effluent Results", title="Column Storage Effluent Results", kind="V", section="Section 15.9",
   reuses="SMPL: Solution Summary - Data Recording (range-validated variant)",
   instructions=('At the end of Column Storage, verify the effluent is in range using an offline meter (Get '
     'Equipment &mdash; the Equipment ID and Description auto-populate) and record the pH and temperature per '
     f'processing day. Verify the pH is within {v("4.8 - 5.2")} and the temperature within {v("15 - 25 &deg;C")}. '
     '<b>Contact the area supervisor/designee if the pH is out of specification.</b> One row per day.'),
   header_fields=[("Get Equipment","b"),("Equipment ID","o"),("Equipment Description","o")],
   cols=["Offline pH","=UoM","Temperature","=UoM ",PB],
   rowdata=[{"=UoM":"pH","=UoM ":"°C"}],
   idx_label="Day #", witness_label="Witnessed By", w=1700),

 dict(folder="Column Storage Disconnect and Disposition", title="Column Storage Disconnect & Disposition", kind="R", section="Section 15.10-15.15",
   reuses="Long Text Instructions (DE2 903)",
   desc=("After the Storage step completes, store the pH probe in KCl storage solution (end of Day 1, if "
     "applicable) and record the buffer totalizer volumes in Attachment 5. Disconnect the column and dispose of the "
     "column guard filter; disconnect/discard the load tubing (and the AKTA Ready Kit if processing is complete); "
     "close the product-vessel inlet, disconnect it from Outlet 4 and dispose of the product filter. For a 2-day "
     "process, record the Day 1 product interim storage start time/date and temperature (2-8 / 15-25 °C). "
     "Reuses Long Text Instructions."),
   ),

 # ---------- H. Product Sampling & Disposition ----------
 dict(folder="Product Vessel Weigh", title="Product Vessel Weigh", kind="R", section="Section 16.1 / 16.7",
   desc="Weigh the product vessel (scale ID + calibration); gross & net weight (=gross − tare) before and after sampling."),
 dict(folder="Product Mixing", title="Product Mixing", kind="R", section="Section 16.2",
   desc="Mix product ≥15 min (LevTech/Mobius): mixer ID, agitation RPM, start/end time, mixing duration."),
 dict(folder="Product Sampling and DLIMS Submission", title="Product Sampling & DLIMS Submission", kind="R", section="Section 16.3",
   desc="Remove product sample (8009938-30) per Attachment 1, stamp date/time, aliquot, label, submit to DLIMS. Reuses SMPL: Sampling Record."),
 dict(folder="Product pH Conductivity Temperature", title="Product pH / Conductivity / Temperature", kind="V", section="Section 16.4",
   reuses="SMPL: Solution Summary - Data Recording (range-validated variant)",
   instructions=('Place 10 mL of product in a 50 mL conical tube and measure the pH, conductivity and temperature '
     'using an offline meter (Get Equipment &mdash; the Equipment ID and Description auto-populate). Record the '
     'results on the final processing day.'),
   header_fields=[("Get Equipment","b"),("Equipment ID","o"),("Equipment Description","o")],
   cols=["Offline pH","=UoM","Conductivity","=UoM ","Temperature","=UoM  ",PB],
   rowdata=[{"=UoM":"pH","=UoM ":"mS/cm","=UoM  ":"°C"}],
   idx_label="#", witness_label="Witnessed By", w=1850),
 dict(folder="Product Storage and Cross-Record", title="Product Storage & Cross-Record", kind="R", section="Section 16.8",
   desc="Record initial storage condition (2-8 / 15-25 °C) + storage start time/date; cross-write Load Start Time back to the Pod Harvest MPR."),

 # ---------- I. Batch Record Review & Attachments ----------
 dict(folder="Batch Production Record Review", title="Batch Production Record Review", kind="R", section="Review",
   desc="Verify supporting docs attached, net weight in SAP, yield calcs complete, all materials/CPDS consumed into SAP; submit for review."),
 dict(folder="Sampling Record", title="Sampling Record", kind="R", section="Attachment 1",
   desc="DLIMS sample submission chart (GREENFORM): -10 starting / -20 column effluent / -30 product; test names, volumes, tube types, storage temps, sample numbers. Reuses SMPL: Sampling Record / Sample Submission Chart."),
 dict(folder="Non-Routine Sampling Record", title="Non-Routine Sampling Record", kind="R", section="Attachment 2",
   desc="Ad-hoc samples requested by MEMO: process section, contents, container, quantity, designation, DLIMS. Reuses SMPL: Non-Routine Sampling Record."),
 dict(folder="Yield Calculations", title="Yield Calculations", kind="R", section="Attachment 3",
   desc="Load mass (pre-sampling), final product mass (pre/post-sampling), % yield. Reuses calculation XSteps."),

 dict(folder="Adjusted Flowrate Table", title="Adjusted Flowrate Table", kind="N", section="Attachment 4",
   instructions=('If flow rates are lowered to avoid over-pressurization during the run, record the step number, '
     'cycle number, adjusted flow rate achieved, and the reason for the change.'),
   cols=["Step Number","Cycle Number","Adjusted Flow Rate (L/hr)","Reason for Flow Rate Change",PB],
   witness_label="Witnessed By", w=1900),

 dict(folder="Buffer Totalizer Volumes", title="Buffer Totalizer Volumes", kind="N", section="Attachment 5",
   instructions=('Record the buffer totalizer volume consumed per cycle for each buffer/inlet, plus the total. '
     'Buffers: Tris (8004949), Tris/NaCl wash (8004950), Elution (8010534), Strips (8008812 / 8008813 / 8006409) '
     'and Storage (8004953). Buffer consumption is posted via the Goods Issue process message (Z_PICONS, mvt 261).'),
   cols=["Inlet","Buffer","Cycle 1 (L)","Cycle 2 (L)","Cycle 3 (L)","Cycle 4 (L)","Cycle 5 (L)","=Total (L)",PB],
   rowdata=[{"Inlet":"2","Buffer":"50 mM Tris, pH 7.4 (8004949)"}], index=False, witness_label="Verified By", w=2500),

 dict(folder="Comments Section", title="Comments Section", kind="R", section="Attachment 6",
   desc="Record comments, deviations, PAUSE reasons, and corrective actions (step no. + initials/date). Reuses SMPL: Comments."),
]

# EBR phase plan (folder order per phase)
PHASES = [
 ("Process Order Information",
   ["Order Header Details","Signature Table","Display BOM","Room and Equipment Assign",
    "Additional Manufacturing Supplies","Solution Buffer Batch Record","Additional Solution Batches Used",
    "Process Notes"]),
 ("Phase 1 — AKTA Kit Install & WFI Charge",
   ["Data Logger Verification","Record Process Room","WFI Container Setup and Charge",
    "AKTA Kit Install and Component Test"]),
 ("Phase 2 — Column & Calculations",
   ["Chromatography Column Information","Column Pressure and Cycle Calculations",
    "Column and Method Verification","Load Concentration and Volume"]),
 ("Phase 3 — Product Collection & Filter Setup",
   ["Estimated VI Product Volume","Product Collection Vessel Setup","Product Filter Information",
    "Depth Filter Sizing Calculation","Depth Filter Count Calculation","Depth Filter Material Setup",
    "Total Surface Area Calculation","Depth Filter Flush Flowrate Calculation","Depth Filter Hold-Up Calculation",
    "Minimum WFI Flush Volume Calculation","Minimum Buffer Flush Volume Calculation",
    "Record Meter ID","Record Thermometer ID","Pod Holder and Pressure Sensors",
    "Install Depth Filtration Units"]),
 ("Phase 4 — Depth Filter Flush & Skid Connections",
   ["Depth Filter Pre-Flush Connections","Depth Filter Flush","Skid pH Probe Standardization",
    "Skid Buffer Inlet Connections","Column Guard Filter"]),
 ("Phase 5 — CaptureSelect Chromatography Run",
   ["Pre-Cycle Setup Verification","POD Chase Volume Calculation","Meter Standardization",
    "Chromatography Method Parameters","Chromatography Method Start","Phase Execution and Sign-off",
    "Equilibration Effluent Results","Column Effluent Sample Date and Time","Column Effluent Sampling",
    "Load Recording","Elution Collection",
    "Strip 2 Effluent Results","Strip 3 Effluent Results"]),
 ("Phase 6 — Column Storage",
   ["Column Storage Buffer and Parameters","Sanitization Hold and Pre-Storage Equilibration",
    "Column Storage Effluent Results","Column Storage Disconnect and Disposition"]),
 ("Phase 7 — Product Sampling & Disposition",
   ["Product Vessel Weigh","Product Mixing","Product Sampling and DLIMS Submission",
    "Product pH Conductivity Temperature","Product Storage and Cross-Record"]),
 ("Phase 8 — Batch Record Review & Attachments",
   ["Batch Production Record Review","Sampling Record","Non-Routine Sampling Record","Yield Calculations",
    "Adjusted Flowrate Table","Buffer Totalizer Volumes","Comments Section"]),
]

# Real DE1 100 XStep behind each reuse/variant (verified against the AZ Phase 2 / AZP2-Bioreactor
# library, 2026-07-13). Blank = candidate not yet confirmed in DE1 100.
REUSES = {
 "Signature Table":"SMPL Header: Signature Table",
 "Room and Equipment Assign":"SMPL: Room/Equipment Assign",
 "Solution Buffer Batch Record":"SMPL: Solution Summary - Data Recording",
 "Additional Solution Batches Used":"SMPL: Solution Summary - Data Recording",
 "Additional Manufacturing Supplies":"SMPL: Additional Assembly + SMPL: Material Consumption",
 "Column Pressure and Cycle Calculations":"SMPL: Three Variable Calc (calc chain)",
 "Load Concentration and Volume":"SMPL: Solution Summary - Data Recording",
 "Yield Calculations":"SMPL: Yield Calculations",
 "Sampling Record":"SMPL: Sampling Record + SMPL: Sample Submission Chart",
 "Non-Routine Sampling Record":"SMPL: Non-Routine Sampling Record",
 "Column Effluent Sampling":"SMPL: Sampling Record",
 "Product Sampling and DLIMS Submission":"SMPL: Sampling Record",
 "Equilibration Effluent Results":"SMPL: Solution Summary - Data Recording",
 "Product pH Conductivity Temperature":"SMPL: Solution Summary - Data Recording",
 "AKTA Kit Install and Component Test":"SMPL: Filter Integrity Test (variant)",
 "Product Vessel Weigh":"SMPL: Bag Replacement Weight (weight pattern)",
 "Product Mixing":"SMPL: Bag Replacement Weight / weight+timer pattern",
 "Depth Filter Material Setup":"SMPL: Material Consumption",
 "Product Filter Information":"SMPL: Material Consumption / SMPL: Additional Assembly",
 # Long Text Instructions shell (DE2 903) — all instruction-only / sign-off steps reuse it
 "Data Logger Verification":"Long Text Instructions (DE2 903)",
 "Column and Method Verification":"Long Text Instructions (DE2 903)",
 "Pre-Cycle Setup Verification":"Long Text Instructions (DE2 903)",
 "Phase Execution and Sign-off":"Long Text Instructions (DE2 903)",
}
for _s in STEPS:
    if _s['folder'] in REUSES and 'reuses' not in _s: _s['reuses']=REUSES[_s['folder']]

BYF = {s['folder']: s for s in STEPS}
OLDREF = {s['folder']: s.get('section','') for s in STEPS}

import re, math
def _plain(t): return re.sub(r'<[^>]+>','',t)
for s in STEPS:
    s.setdefault('rows',1)
    w=s.get('w',1740); cpl=max(120,int(w/8.6))
    instr=s.get('instructions','')
    # a table in the instructions lays out as one line per <tr> (+ title/margins),
    # so measure it by row count and the prose around it by length
    prose=re.sub(r'<table.*?</table>','',instr,flags=re.S)
    trs=instr.count('<tr>')
    lines=max(1, math.ceil(len(_plain(prose))/cpl), prose.count('<li>')+1) if instr else 1
    if trs: lines += trs+4
    if 'form' in s: n=sum(3 if (len(it)>1 and it[1]=='dt') else 1 for it in s['form'])
    elif 'longtext' in s: n=len(s.get('signoffs',[]))
    elif s.get('rowdata'): n=len(s['rowdata'])
    else: n=s['rows']
    n += len(s.get('header_fields',[]))
    n += sum(3 if (len(it)>1 and it[1]=='dt') else 1 for it in s.get('footer_fields',[]))
    s['h']=300 + n*40 + lines*26 + 80
