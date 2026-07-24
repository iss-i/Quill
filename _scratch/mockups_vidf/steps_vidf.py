# -*- coding: utf-8 -*-
"""AZ Phase 3 (real project) - Virus Inactivation (PN 8012441) + Concentration & Diafiltration
(PN 8012475) XSteps.  Reworked to the field-verified building-block model:
  kind R = reuse an existing DE1 100 block (or a STACK of existing blocks under a hidden Conditional
           Header / collapsed into a table) as-is -> NO bespoke mock-up, rendered as a reuse card.
  kind N = genuinely new / a small variant of a block with no known client match -> bespoke mock-up.
Only 7 steps are N (with mock-ups); everything else is a reference / block-stack. Every `reuses=`
target was confirmed by opening the real DE1 100 block and diffing its fields (shaper_get_version).
Groups: Common (front matter + reusable blocks), VI, CDF. Renderer notation as in build_mockups."""
def v(x): return f'<span class="v">{x}</span>'
PB = "Performed By*"

STEPS = [

# ================= COMMON — Process Order Information / front matter =================
 dict(folder="Common - Order Header Details", title="Order Header Details", kind="R", section="Header",
   reuses="DE1 100: Display Process Order Header Data (AZ Components) / SXS: SIMPL Order Header",
   desc="Product / PN, process order numbers, recorded by — standard SAP order header. Reused as-is."),

 dict(folder="Common - Signature Table", title="Signature Table", kind="R", section="Personnel ID",
   reuses="DE1 100: SMPL Header: Signature Table",
   desc="Personnel identification: print name, signature, initials for everyone executing the record. Reused as-is."),

 dict(folder="Common - Display BOM", title="Display BOM", kind="R", section="§4",
   reuses="DE1 100: Display BOM Material Table",
   desc="Bill of Materials — equipment (VI Treatment Vessel / UF-DF skid, meters, scale, mixer, FIT) and "
     "components / filters / bags with SAP consumption. Reused as-is."),

 dict(folder="Common - Room and Equipment Assign", title="Room & Equipment Assign", kind="R", section="§7 (VI 7.3-7.4 / C&D 7)",
   reuses="DE1 100: SMPL: Room/Equipment Assign + SMPL: Equipment Select (field-verified: has ID + Description + Calibration Due Date)",
   desc="Record the process room and assign every instrument up front (pH/cond meter, thermometer, scale, mixer, "
     "stir plate, pump) with calibration check. Downstream steps retrieve via Get [Type] (SMPL: Equipment Select, "
     "which already carries Calibration Due Date). Reused as-is."),

 dict(folder="Common - Additional Manufacturing Supplies", title="Additional Manufacturing Supplies", kind="N", section="§4",
   reuses="Variant of DE1 100: SMPL: Additional Assembly (adds MPR Step No. / Material Description) — no known client variant",
   instructions=('If additional materials (filter, bag, assembly, etc.) are used during processing, verify the '
     'material is acceptable per Section 4 and record its information; document the reason in the Comments Section. '
     'Enter the Part No. (Material Description auto-fills) and Batch No. (Exp. Date auto-fills). <b>SAP consumption '
     'posts automatically via the Goods Issue process message (Z_PICONS, movement type 261).</b> Built new: a '
     'variant of SMPL: Additional Assembly with an added MPR Step No.'),
   cols=["MPR Step No.","Part No.","=Material Description","Batch No.","=Exp. Date","Serial No.",
     "Autoclave ID","~Autoclave Exp.",PB],
   witness_label="Witnessed By", w=2200),

 dict(folder="Common - Additional Solution Batches", title="Additional Solution Batches (Solution Switch)", kind="N", section="§5",
   reuses="Variant of DE1 100: SMPL: Material Consumption (adds Applicable Step No.; field-verified NOT Solution Summary) — no known client variant",
   instructions=('When a process solution must be replaced with a different batch during processing, record the '
     'switch: indicate the applicable step, confirm the new solution is the same Part No. as the one replaced, and '
     'record Part No. / Batch No. / Exp. Date. Document the reason in the Comments Section. Built new: a variant of '
     'SMPL: Material Consumption (which carries Part No. / Batch / Exp.) with an added Applicable Step No.'),
   cols=["Applicable Step No.","Part Number","Batch Number","=Exp. Date",PB], witness_label="Witnessed By", w=1700),

 dict(folder="Common - Process Notes and Global Limits", title="Process Notes & Global Limits (Acknowledgement)",
   kind="R", section="§6",
   reuses="DE1 100: SXS: Text Instructions with Sign-off (notes authored in IV_INSTR; DE2 903: Long Text Instructions)",
   desc="Global process notes / limits (15-27 °C; 1 L = 1 kg; within-expiry; equipment-ID attests calibration; "
     "Targets/Alert Limits; NaOH corrosive). The operator acknowledges; each limit is enforced at the step that "
     "captures its parameter. Reused as-is (Text Instructions shell, content per MBR)."),

# ================= COMMON — reusable building blocks =================
 dict(folder="Common - Incoming Product Information", title="Incoming Product Information (Weight / Concentration / DLIMS)",
   kind="N", section="VI 7.5 · C&D 7.4-7.6",
   reuses="NEW — no DE1 100 block combines weight + concentration + DLIMS (field-verified: Material Consumption has PN/Batch, Solution Summary has measurement, neither has both)",
   instructions=('Record the incoming / starting product for each vessel or bag: <b>tare + net weight</b> (kg = L), '
     'the <b>SoloVPE protein concentration</b> (g/L, sample per SOP-0107091) and the <b>DLIMS project / sample '
     'numbers</b> it is reported under. Built new — no existing block combines these. <b>Goods issue has no batch '
     'field → consume the upstream Affinity / Pod-Harvest PN/batch.</b>'),
   cols=["Tare Weight (kg=L)","Net Weight / Volume (kg=L)","SoloVPE Concentration (g/L)",
     "DLIMS Project No.","DLIMS Sample No.",PB],
   idx_label="Vessel / Bag #", witness_label="Witnessed By", w=2100),

 dict(folder="Common - Product Vessel Weigh", title="Product Vessel Weigh", kind="R", section="VI §7/8/15 · C&D §9/11/16/17/18",
   reuses="DE1 100: SMPL: Record Scale Weight (Tare Weight / Select Vessel Type & Tare Weight variants)",
   desc="Get Scale / Balance (ID + Calibration Due auto-populate), record gross weight; net computed "
     "(Gross − Tare, 1 kg = 1 L). Reused as-is."),

 dict(folder="Common - Calc Three Columns", title="Calc — Three Columns (Value1 op Value2 = Result)", kind="R",
   section="VI 7.12 / 8.10 / 14.15 · C&D §7/16/17",
   reuses="DE1 100: SMPL: Calc Three Columns (2-input — field-verified: Input Val1 / Input Val2 / Result)",
   desc="Two-operand calc archetype (Value 1 [× ÷ + −] Value 2 = Result) — e.g. VI 7.12 Net = Gross − Tare. Reused as-is."),

 dict(folder="Common - Multi-Variable Calculation", title="Multi-Variable Calculation (3-input / ranged)", kind="R",
   section="C&D §12/16/17",
   reuses="DE1 100: SMPL: Three Variable Calc (3-input) / SMPL: Calc Range Values (ranged min/target/max)",
   desc="Multi-operand calc archetype — 3-input (Three Variable Calc) or ranged result (Calc Range Values). Reused as-is."),

 dict(folder="Common - Product Mixing", title="Product Mixing", kind="R", section="VI §15 · C&D §9/16/17",
   reuses="DE1 100: SMPL: Mixing Time (field-verified: Agitation RPM + Start/End + Duration of Mixing)",
   desc="Get Mixer (ID + Description), record agitation RPM, stamp start/end; duration computed. Reused as-is."),

 dict(folder="Common - Product Sampling and DLIMS Submission", title="Product Sampling & DLIMS Submission", kind="R",
   section="VI §15/Att1 · C&D §8/14/16/17/Att3",
   reuses="DE1 100: SMPL: Sampling Record + SMPL: Sample Submission Chart",
   desc="Remove the sample per Att 1/3 & SOP-0107097; aliquot & label per SOP-0107056; submit to DLIMS per "
     "SOP-0080295; stamp date/time; record DLIMS project / sample numbers. Reused as-is.",
   blocks=[
     dict(bsub="SMPL: Sampling Record — pull & aliquot (SOP-0107097 / label SOP-0107056)",
       fields=[("Sample Designation","r"),("Sampling Date & Time","t"),("Sample Volume","r"),
         ("Intermediate Storage Temp (°C)","r")]),
     dict(head="SMPL: Sample Submission Chart — submit to DLIMS (SOP-0080295)",
       cols=["DLIMS Test Name","DLIMS Project No.","DLIMS Sample No.","Tube / Container Type","Location","%Submitted?",PB],
       idx_label="#", index=True, rowdata=[{"%Submitted?":"Yes"}])],
   w=2100),

 dict(folder="Common - Product pH Conductivity Temperature", title="Product pH / Conductivity / Temperature", kind="R",
   section="VI 7.1/15.5 · C&D 8.12/14.11/17",
   reuses="DE1 100 stack: SMPL: Equipment Select ×2 (pH/Cond Meter + Thermometer) + SMPL: Solution Summary - Data Recording (range-validated; field-verified = Equipment + Min/Max Target + Actual Value + Cond High/Low)",
   desc="Get pH/Cond Meter + Get Thermometer, then record range-validated pH / conductivity / temperature per "
     "reading. Assembled from two Equipment Selects + the Solution Summary results block (collapses per row). "
     "Contact supervisor if out of specification.",
   blocks=[
     dict(bsub="SMPL: Equipment Select — pH / Conductivity Meter",
       fields=[("Get pH / Cond Meter","b"),("pH / Cond Meter ID","o"),("Description","o"),("Calibration Due Date","o")]),
     dict(bsub="SMPL: Equipment Select — Thermometer",
       fields=[("Get Thermometer","b"),("Thermometer ID","o"),("Description","o"),("Calibration Due Date","o")]),
     dict(head="SMPL: Solution Summary - Data Recording — range-validated readings (collapses per row)",
       cols=["Parameter","=Equipment","Min Target","Max Target","Actual Value","%Cond (High / Low)"],
       idx_label="#", index=True, rowdata=[{"Parameter":"pH"}])],
   w=1900),

 dict(folder="Common - Hold Time Table", title="Hold Time Table", kind="N", section="VI §19 (Att3) · C&D §9/§25 (Att5)",
   reuses="NEW — no DE1 100 block carries the RT / 2-8 °C hold DURATIONS + >72 h / >168 h threshold logic (Solution Summary is measurement, Solution Final Storage is a location)",
   instructions=('Track product hold time across storage moves. Per hold: select the storage condition, stamp start '
     'and end; RT and 2-8 °C durations computed separately. Totals computed &mdash; alert if RT total exceeds '
     f'{v("72 h")} or the combined total exceeds {v("168 h")} (contact supervisor). Built new: no block has the '
     'duration + threshold logic.'),
   cols=["Location","%Storage Temp","@STAMP","~Storage Start","@STAMP","~Storage End","=RT Hold (h)","=2-8°C Hold (h)",PB],
   rowdata=[{"%Storage Temp":"2-8 °C"}], idx_label="Hold #",
   footer_fields=[("Total RT Hold (h)","o"),("Total 2-8°C Hold (h)","o"),("Total Combined Hold (h)","o")],
   witness_label="Witnessed By", w=2100),

 dict(folder="Common - Product Recirculation Worksheet", title="Product Recirculation Worksheet", kind="R",
   section="VI Att6 · C&D Att7",
   reuses="DE1 100 stack: SMPL: Record Text Value (Applicable MPR Step / Product Name) + SMPL: Material Consumption (recirculation tubing Part/Batch/Exp/Autoclave) + SMPL: Timer for Start-End Process (field-verified: Start/End Date-Time + Time Difference)",
   desc=f"Record each product recirculation: identify the applicable MPR step & product name, record the recirculation "
     f"tubing information, then stamp mixing start and end; duration computed (target {v('≥ 40 min')}). Assembled from "
     "a Record Text + Material Consumption + the Timer block; was mis-flagged 'new' earlier.",
   blocks=[
     dict(bsub="SMPL: Record Text Value — recirculation context",
       fields=[("Applicable MPR Step","r"),("Product Name","r")]),
     dict(head="SMPL: Material Consumption — recirculation tubing", gi=True,
       cols=["Tubing Part No.","Batch No.","=Exp. Date","Autoclave Cycle No.","~Autoclave Exp.",PB],
       idx_label=None, index=False, add_row=False),
     dict(bsub="SMPL: Timer for Start-End Process — mixing by recirculation (≥ 40 min)",
       fields=[("Mixing Start Time","t"),("Mixing End Time","t"),("Mixing Duration (≥ 40 min)","o")])],
   w=1800),

 dict(folder="Common - Transfer Tubing and Hosing Info", title="Transfer Tubing / Hosing Information", kind="R",
   section="VI Att5 · C&D Att1",
   reuses="DE1 100: SMPL: Material Consumption / SMPL: Additional Assembly (Part/Batch/Exp/Serial/Autoclave)",
   desc="Record each transfer tubing / flex hose: Part No., Batch No. (Exp. auto), autoclave cycle / expiry, "
     "hose serial, cleaning batch / expiry. Reused as-is.",
   blocks=[
     dict(head="SMPL: Material Consumption — transfer tubing (one row per line)", gi=True,
       cols=["Line / Use","Tubing Part No.","Batch No.","=Exp. Date","Autoclave Cycle No.","~Autoclave Exp.",PB],
       idx_label="#", index=True, rowdata=[{"Line / Use":"Feed Line"}]),
     dict(head="SMPL: Additional Assembly — flex hose (one row per line)", gi=True,
       cols=["Line / Use","Hose Part No.","Hose Serial No.","Hose Cleaning Cycle No.","~Hose Cleaning Exp.",PB],
       idx_label="#", index=True, rowdata=[{"Line / Use":"Feed Line"}])],
   w=2100),

 dict(folder="Common - Product Storage and Cross-Record", title="Product Storage & Cross-Record", kind="N",
   section="VI 15.8 · C&D §9/§18",
   reuses="Variant of DE1 100: SMPL: Solution Final Storage (adds storage condition RT/2-8 °C + start date/time + cross-record; block has Storage Location only) — no known client variant",
   instructions=('Record the initial storage condition (RT / 2-8 °C) and stamp the storage start date/time, and '
     'cross-record the storage linkage into the Hold-Time attachment / next MPR. Built new: SMPL: Solution Final '
     'Storage carries a Storage Location but not the storage-condition + start-date/time this record needs.'),
   form=[("Storage Condition (RT / 2-8 °C)","d","2-8 °C"),("Storage Start Date & Time","dt"),
     ("Cross-Record — Step / Value written to next MPR","r"),("Performed By","r"),("Witnessed By","r")], w=1600),

 dict(folder="Common - Instruction and Sign-off", title="Instruction & Sign-off", kind="R", section="VI §8/16/20 · C&D §11/20",
   reuses="DE1 100: SXS: Text Instructions with Sign-off (DE2 903: Long Text Instructions)",
   desc="Reusable instruction-only shell (line/valve connections, dip-tube confirmation, N/A gates, product transfer, "
     "BPR review). Text authored per use in IV_INSTR; operator reads and signs. Reused as-is."),

 dict(folder="Common - Yield Calculations", title="Yield Calculations", kind="R", section="VI Att4 · C&D Att8",
   reuses="DE1 100: SMPL: Yield Calculations",
   desc="% Yield = Final Product Mass ÷ Load Mass × 100 (masses carry from the weigh / concentration steps). Reused as-is."),

 dict(folder="Common - Comments and Deviations", title="Comments / Deviations Section", kind="R", section="VI Att7 · C&D Att9",
   reuses="DE1 100: SXS: Phase Comments (no clean 'SMPL: Comments' — closest confirmed component)",
   desc="Free-text log for comments and documented deviations (step no. + initials/date). Reused as-is."),

 dict(folder="Common - Non-Routine Sampling Record", title="Non-Routine Sampling Record", kind="R", section="VI Att2 · C&D Att4",
   reuses="DE1 100: SMPL: Non-Routine Sampling Record",
   desc="Ad-hoc samples requested by MEMO: process section, contents, container, quantity, designation, DLIMS. Reused as-is."),

# ================= VIRUS INACTIVATION only (PN 8012441) =================
 dict(folder="VI - Treatment Vessel Setup", title="VI Treatment Vessel Setup", kind="N", section="§8",
   reuses="NEW — bespoke single XStep. The Affinity-vessel / Bag / Tank / vent-filter / filters-attached dropdowns DRIVE conditional activation of the sections they gate, and in PI-PCS the activating dropdown must live in the SAME XStep as the sections it activates/deactivates (a dropdown XStep cannot reach down and gate a separate XStep below it). Fields field-verified against SMPL: Select Vessel Type & Tare Weight + SMPL: Material Consumption, but built as one XStep for the branching.",
   instructions=('Set up the VI Treatment Vessel. The <b>selection dropdowns below drive conditional activation</b> — '
     'each gate activates or deactivates the section beneath it, so they are all built into this one XStep. First '
     'decide whether the incoming Affinity product vessel is reused as the VI Treatment Vessel (if so, all of Section '
     '8 is N/A). Otherwise obtain &amp; label the vessel (AZD0543 / “VI Treatment Vessel” / Batch / Part / Initials / '
     'Date), complete the Bag <i>or</i> Tank section, record the vent + product filters, and capture the tare weight '
     'with the filters-attached confirmation. <b>Filters post via Goods Issue (Z_PICONS 261).</b>'),
   blocks=[
     dict(gate=("Use Affinity Product Vessel as VI Treatment Vessel?","No"),
       note="Yes → all of Section 8 is N/A and every section below deactivates (continue at Section 9/10). "
         "No → obtain & label the vessel and complete the applicable sections below."),
     dict(gate=("Bag Required?","No"), head="Bag Information (activated when Bag Required = Yes)", gi=True,
       cols=["Bag Part No.","Batch No.","=Exp. Date","Serial No.",PB], idx_label=None, index=False, add_row=False),
     dict(fields=[("Mixer Drive attached?","d","Yes / No"),("Top Base attached?","d","Yes / No"),
       ("Magnetic Clamp attached?","d","Yes / No")]),
     dict(gate=("Tank Required","No"), head="Tank Information (activated when Tank Required = Yes)",
       cols=["Tank ID","CIP Batch ID","=CIP Exp. Date/Time","Pressure Test ID","@BTN:Get Pressure Date/Time",
         "~Pressure Test Date","~Pressure Test Time","SIP Batch ID"],
       idx_label=None, index=False, add_row=False),
     dict(gate=("Vent Filter Required","No"),
       head="Vent Filter Information (see Section 4; bold PNs require autoclaving)", gi=True,
       cols=["Filter Position","Part No.","Batch No.","=Exp. Date","Serial No.","Autoclave Cycle No.","~Autoclave Exp.",PB],
       idx_label=None, index=False, add_row=False, rowdata=[{"Filter Position":"Vent Filter (if applicable)"}]),
     dict(head="Product Filter Information (see Section 4; bold PNs require autoclaving)", gi=True,
       cols=["Filter Position","Part No.","Batch No.","=Exp. Date","Serial No.","Autoclave Cycle No.","~Autoclave Exp.",PB],
       idx_label="#", index=True, rowdata=[{"Filter Position":"Product Filter 1"}]),
     dict(fields=[("Get Scale / Balance","b"),("Scale / Balance ID","o"),("Scale / Balance Calibration Due Date","o"),
       ("Tare Weight of VI Treatment Vessel (kg = L)","r"),
       ("Product Filter attached when tare obtained?","d","Yes / No"),
       ("Vent Filter attached when tare obtained?","d","Yes / No"),
       ("No filters — vessel is a bag?","d","Yes / No")],
       witness="Recorded By / Date")],
   w=2400),

 dict(folder="VI - Acid-Base pH Titration Table", title="Iterative pH Titration Table (Acid / Base)", kind="N", section="§10 / 12 / 14",
   reuses="NEW — iterative per-addition titration with running totals; no library block. Header uses SMPL: Equipment Select ×3",
   instructions=('Iterative pH adjustment by incremental buffer addition. Record initial pH / conductivity / '
     f'temperature and start time. Per addition: gross weight before &amp; after (net + running total computed), '
     f'stamp the pH-sample time and record adjusted pH. Target &mdash; acid {v("pH 3.5 (NOR 3.4-3.6)")}, '
     f'neutralization {v("pH 7.2-7.6")}. Re-standardize the pH meter (4.0/10.0) once pH &ge; 4.0. Buffer '
     'consumption posts via Goods Issue (Z_PICONS 261) on the total net weight. Built new — bespoke titration table; '
     'the Get Scale / Get pH-Cond Meter / Get Thermometer headers are SMPL: Equipment Select.'),
   header_fields=[("Get Scale / Balance","b"),("Scale / Balance ID","o"),("Scale / Balance Description","o"),
     ("Scale / Balance Cal Due","o"),
     ("Get pH / Cond Meter","b"),("pH / Cond Meter ID","o"),("pH / Cond Meter Description","o"),("pH / Cond Meter Cal Due","o"),
     ("Get Thermometer","b"),("Thermometer ID","o"),("Thermometer Description","o"),("Thermometer Cal Due","o"),
     ("Initial pH","r"),("Initial Conductivity","r"),("Initial Temperature (°C)","r")],
   cols=["Gross Wt Before (kg)","Gross Wt After (kg)","=Net Added (kg)","=Total Net (kg)","@STAMP","~pH Sample Time","Adjusted pH","~Sample Temp (°C)",PB],
   idx_label="Addition #",
   footer_fields=[("Final pH Confirmed Time","t"),("Final pH","o"),("Final Conductivity","r"),
     ("Final Temperature (°C)","r"),("Incubation Start Time","t")],
   witness_label="Witnessed By", w=2300),

 dict(folder="VI - Incubation Timing and Sample", title="Incubation Timing & Incubated Sample (block stack)", kind="R", section="§11 / 13",
   reuses="DE1 100 stack: SMPL: Timer for Start-End Process (incubation start/end/duration) + SMPL: Record Text Value (mid-incubation sample time) + SMPL: Equipment Select ×2 (thermometer + pH/Cond meter) + SMPL: Solution Summary - Data Recording (incubated pH/cond/temp) + Dynamic Dropdown (§13 in-range → neutralize / out → extend incubation) + SMPL: Record Text Value (supervisor contacted on extension)",
   desc=f"Time the low-pH incubation (start carries from the titration; target {v('75 min (NOR 60-240)')}), stamp the "
     "mid-incubation sample time, take a mid-incubation temperature check and an incubated pH/cond/temp sample, then "
     "make the §13 decision — in-range proceed to neutralization, out-of-range extend incubation and contact the "
     "supervisor. Assembled from the Timer block + a Record Text (sample time) + two Equipment Selects + the Solution "
     "Summary results block + a Dynamic Dropdown (drives conditional activation) + a Record Text (supervisor). No "
     "bespoke XStep.",
   blocks=[
     dict(bsub="SMPL: Timer for Start-End Process — low-pH incubation (target 75 min, NOR 60–240)",
       fields=[("Incubation Start Time (carries from titration)","o"),("Incubation End Time","t"),
         ("Incubation Duration","o")]),
     dict(bsub="SMPL: Record Text Value — mid-incubation sample time", fields=[("Mid-Incubation Sample Time","t")]),
     dict(bsub="SMPL: Equipment Select — Thermometer",
       fields=[("Get Thermometer","b"),("Thermometer ID","o"),("Calibration Due Date","o")]),
     dict(bsub="SMPL: Equipment Select — pH / Conductivity Meter",
       fields=[("Get pH / Cond Meter","b"),("pH / Cond Meter ID","o"),("Calibration Due Date","o")]),
     dict(head="SMPL: Solution Summary - Data Recording — incubated pH / conductivity / temperature",
       cols=["Parameter","=Equipment","Min Target","Max Target","Actual Value","%Cond (High / Low)"],
       idx_label="#", index=True, rowdata=[{"Parameter":"Incubated pH"}]),
     dict(gate=("§13 Decision — pH in range?","In-range"),
       note="In-range → proceed to neutralization. Out-of-range → extend incubation (re-time) and contact supervisor."),
     dict(bsub="SMPL: Record Text Value — supervisor contacted (only if incubation extended)",
       fields=[("Supervisor Contacted","r")])],
   w=2000),

 dict(folder="VI - Temperature Decision Tree", title="Starting / Transfer Temperature Check (block stack)", kind="R", section="§7.14 / 9",
   reuses="DE1 100 stack: SMPL: Equipment Select (thermometer) + SMPL: Record Numeric Value (product temperature, Min/Max 18–25 °C). No decision dropdown — the Record Numeric Value's Min/Max validation function module enforces the range and fires the configured error handling on out-of-range (warm if low / supervisor if high).",
   desc="Measure product temperature and record it. No Dynamic Dropdown is needed: the Record Numeric Value XStep "
     "carries Min/Max targets (18–25 °C) and its min/max validation function module enforces the range — an in-range "
     "value proceeds to acid addition, an out-of-range value triggers the configured error handling (warm the product "
     "if below range / contact supervisor if above). Assembled from Equipment Select + Record Numeric Value. No "
     "bespoke XStep.",
   blocks=[
     dict(bsub="SMPL: Equipment Select — Thermometer",
       fields=[("Get Thermometer","b"),("Thermometer ID","o"),("Calibration Due Date","o")]),
     dict(bsub="SMPL: Record Numeric Value — product temperature (IV_MIN/IV_MAX = 18–25 °C set on the step; Min/Max validation FM enforces the range + error messaging)",
       fields=[("Product Temperature (°C)","r")]),
     dict(note="No decision dropdown: the Min/Max validation function module on the Record Numeric Value flags "
       "out-of-range and runs the configured error handling (below range → warm the product, Section 9; above range "
       "→ contact supervisor); an in-range value proceeds to acid addition (Section 10).")],
   w=1700),

 dict(folder="VI - Store Product and Hold-Time Link", title="Store VI Product & Hold-Time Link (block stack)", kind="R", section="§15.8",
   reuses="Stack of this record's steps: Common - Product Storage & Cross-Record + Common - Hold Time Table, instantiated for §15.8",
   desc="Store the neutralized VI product and map values into Attachment 3. This is simply the Product Storage & "
     "Cross-Record step + the Hold Time Table, instantiated here — no separate XStep.",
   blocks=[
     dict(bsub="Common - Product Storage & Cross-Record (instantiated for §15.8)",
       fields=[("Storage Condition (RT / 2-8 °C)","d","2-8 °C"),("Storage Start Date & Time","dt"),
         ("Cross-Record — value written to Attachment 3","r")]),
     dict(head="Common - Hold Time Table (instantiated for §15.8)",
       cols=["Location","%Storage Temp","~Storage Start","~Storage End","=RT Hold (h)","=2-8°C Hold (h)",PB],
       idx_label="Hold #", index=True, rowdata=[{"%Storage Temp":"2-8 °C"}])],
   w=2000),

# ================= CONCENTRATION & DIAFILTRATION only (PN 8012475) =================
 dict(folder="CDF - Record CIPDS Skid Cassette Info", title="Record CIPDS / Skid / Cassette Information (block stack)", kind="R", section="§7.2 / §11 / Att6",
   reuses="DE1 100 stack: SMPL: Record Text Value ×n (Skid ID / CIPDS Batch / Cassette Lot / Support Plate / sight-glass / valve labels) + SMPL: Material Consumption (cassette / CIPDS / Retentate Vessel vent filter) + SMPL: Select Vessel Type & Tare Weight (Retentate Vessel: Tank ID + cleaning Batch/Exp + sterilization Batch/Exp + pressure-test date + volume) + SMPL: Equipment Select (scale) + SMPL: Record Scale Weight (retentate tare before & after attachment, Scale ID/Cal Due) + SMPL: Record Numeric Value (hold-up volume / total surface area)",
   desc="Record the UF/DF skid & membrane identity (Skid ID, CIPDS batch, cassette lot/part, support plate, hold-up "
     "volume, surface area), confirm the ≤30-day storage window, set up and label the Retentate Vessel — Tank ID, "
     "cleaning & sterilization batch/expiry, pressure-test date, vessel volume, vent filter — and capture the "
     "retentate tare before and after attachment. Assembled from Record Text Value ×n (collapse to a table) + "
     "Material Consumption + Select Vessel Type & Tare Weight (the vessel-setup block) + Equipment Select + Record "
     "Scale Weight + Record Numeric Value. No bespoke XStep.",
   blocks=[
     dict(bsub="SMPL: Record Text Value ×n — skid & membrane identity (collapse to one table)",
       fields=[("UF/DF Skid ID","r"),("CIPDS Batch No.","r"),("Cassette Install Date","r"),("No. of Cassettes","r")]),
     dict(head="SMPL: Material Consumption — cassette / support plate / Retentate vent filter", gi=True,
       cols=["Component","Part No.","Batch No.","=Exp. Date","Serial No.",PB],
       idx_label="#", index=True, rowdata=[{"Component":"Membrane Cassette"}]),
     dict(bsub="SMPL: Record Numeric Value — hold-up volume & total surface area",
       fields=[("Hold-Up Volume (L)","r"),("Total Membrane Surface Area (m²)","r")]),
     dict(gate=("Cassette storage ≤ 30 days?","Yes"),
       note="Confirm the ≤30-day cassette storage window before use."),
     dict(bsub="SMPL: Select Vessel Type & Tare Weight — Retentate Vessel set-up (§11)",
       fields=[("Tank ID","r"),("Cleaning Batch / Exp.","r"),("Sterilization Batch / Exp.","r"),
         ("Pressure Test Date","r"),("Vessel Volume (L)","r")]),
     dict(bsub="SMPL: Equipment Select — Scale / Balance",
       fields=[("Get Scale / Balance","b"),("Scale / Balance ID","o"),("Calibration Due Date","o")]),
     dict(bsub="SMPL: Record Scale Weight — Retentate tare (before & after attachment)",
       fields=[("Tare Weight before attachment (kg)","r"),("Tare Weight after attachment (kg)","r")])],
   w=2200),

 dict(folder="CDF - Run Skid Recipe", title="Run Skid Recipe (block stack)", kind="R", section="§8/10/13/15/19",
   reuses="DE1 100 stack: SMPL: Record Text Value (Batch ID + recipe setpoints TMP/crossflow/flush-vol) + SMPL: Record Numeric Value (membrane-area setpoint, permeate/retentate totalizers) + SMPL: Timer for Start-End Process (recipe start + ≥5-min recirculation start/end/duration) + SMPL: Record Scale Weight (retentate weights + Scale ID/Cal Due) + SMPL: Solution Summary - Data Recording (retentate/permeate conductivity & temperature results) + CDF - Operation Monitoring Worksheet (in-process TMP/pressure/flow/UV log) + Dynamic Dropdown (WFI re-flush / conductivity in-range decision) + SMPL: Component Goods Issue (8012555 buffer / WFI / NaOH per phase); §8/§19 add WFI set-up: SMPL: Record Text Value (Bag / WFI Valve-Tank ID + Charge Date/Time) + SMPL: Calc Three Columns (Expiration = Charge + 24 h)",
   desc="Download and run the named skid recipe per phase (Prep-WFI Flush, Equilibration, Conc 1, Diafiltration, "
     "Conc 2, Recovery, Clean-WFI Flush, Sanitization): record the Batch ID and recipe setpoints, stamp recipe start "
     "and any ≥5-min recirculation (Timer), record retentate weights (Record Scale Weight) and permeate/retentate "
     "totalizers, capture the retentate/permeate conductivity & temperature sample results (Solution Summary), log "
     "in-process parameters (Operation Monitoring Worksheet) and take the conductivity in-range / re-flush decision "
     "(Dynamic Dropdown). WFI-flush phases (§8/§19) first set up WFI — record Bag / Valve / Tank ID and Charge "
     "Date/Time and compute the 24-h expiry. Buffer / WFI / NaOH consumed post via Goods Issue (Z_PICONS 261). No "
     "bespoke XStep — every field maps to an existing block.",
   blocks=[
     dict(gate=("WFI-flush phase? (§8 / §19)","No"),
       note="WFI-flush phases (§8/§19) first set up WFI below; other phases skip to the recipe."),
     dict(bsub="SMPL: Record Text Value — WFI set-up (WFI-flush phases only)",
       fields=[("Bag / WFI Valve-Tank ID","r"),("WFI Charge Date & Time","t")]),
     dict(head="SMPL: Calc Three Columns — WFI Expiration = Charge + 24 h",
       cols=["Value 1","@OP:+","Value 2","@OP:=","Result"], idx_label=None, index=False,
       rowdata=[{"Value 1":"WFI Charge Date/Time","Value 2":"24 h","Result":"WFI Expiration Date/Time"}]),
     dict(bsub="SMPL: Record Text Value — recipe batch & setpoints",
       fields=[("Recipe / Batch ID","r"),("Setpoints (TMP / Crossflow / Flush Vol)","r")]),
     dict(bsub="SMPL: Timer for Start-End Process — recipe start & ≥5-min recirculation",
       fields=[("Recipe Start Time","t"),("Recirculation Start","t"),("Recirculation End","t"),
         ("Recirculation Duration (≥ 5 min)","o")]),
     dict(bsub="SMPL: Record Numeric Value — membrane-area setpoint & totalizers",
       fields=[("Membrane Area Setpoint (m²)","r"),("Permeate Totalizer (L)","r"),("Retentate Totalizer (L)","r")]),
     dict(bsub="SMPL: Record Scale Weight — retentate weight",
       fields=[("Get Scale / Balance","b"),("Scale ID","o"),("Calibration Due Date","o"),("Retentate Weight (kg)","r")]),
     dict(head="SMPL: Solution Summary - Data Recording — retentate / permeate conductivity & temperature",
       cols=["Stream / Parameter","=Equipment","Min Target","Max Target","Actual Value","%Cond (High/Low)"],
       idx_label="#", index=True, rowdata=[{"Stream / Parameter":"Permeate Conductivity"}]),
     dict(bsub="CDF - Operation Monitoring Worksheet — in-process TMP / pressures / flow / UV log (its own Att-2 card)"),
     dict(gate=("Conductivity in range? / WFI re-flush?","In-range"),
       note="In-range → proceed. Out-of-range → re-flush and re-sample."),
     dict(head="SMPL: Component Goods Issue — buffer / WFI / NaOH consumed this phase", gi=True,
       cols=["Component","Batch No.","Amount Used (L)",PB],
       idx_label="#", index=True, rowdata=[{"Component":"Buffer 8012555"}])],
   w=2400),

 dict(folder="CDF - Minimum Membrane Surface Area", title="Minimum Membrane Surface Area (block stack)", kind="R", section="§7.7",
   reuses="DE1 100 stack: SMPL: Calc Three Columns (Total Grams ÷ Max Loading = Min Area) + SMPL: Record Numeric Value (installed area) + Dynamic Dropdown (installed ≥ minimum?)",
   desc="Total Grams Product ÷ Max Loading (g/m²) = Minimum Membrane Area; confirm installed area ≥ minimum. "
     "Assembled from a 2-input Calc Three Columns + Record Numeric Value + a Dynamic Dropdown. No bespoke XStep.",
   blocks=[
     dict(head="SMPL: Calc Three Columns — Minimum Area = Total Grams ÷ Max Loading",
       cols=["Value 1","@OP:÷","Value 2","@OP:=","Result"], idx_label=None, index=False,
       rowdata=[{"Value 1":"Total Grams Product","Value 2":"Max Loading (g/m²)","Result":"Minimum Membrane Area (m²)"}]),
     dict(bsub="SMPL: Record Numeric Value — installed membrane area",
       fields=[("Installed Membrane Area (m²)","r")]),
     dict(gate=("Installed area ≥ minimum?","Yes"),
       note="Confirm the installed membrane area ≥ calculated minimum before proceeding.")],
   w=1900),

 dict(folder="CDF - Process Input Calculations", title="Process Input Calculations (calc-block stack)", kind="R", section="§12",
   reuses="DE1 100 stack: SMPL: Calc Three Columns / Three Variable Calc / Calc Range Values (×~9 setpoint calcs — 80%/40% capacity, Conc 1/2 volumes & weights, DF permeate range)",
   desc="Compute the process setpoints from the load (capacity 80%/40%, Conc 1 & 2 target volumes/weights, DF "
     "permeate range). A stack of ~9 reusable calc blocks (2-input Calc Three Columns, 3-input Three Variable Calc, "
     "and Calc Range Values for the ranges). No bespoke XStep.",
   blocks=[
     dict(head="SMPL: Calc stack (~9) — 80%/40% capacity, Conc 1 & 2 volumes/weights, DF permeate range",
       cols=["Calculation","Value 1","@OP:×","Value 2","@OP:=","Result (Min / Target / Max)"],
       idx_label="#", index=True,
       rowdata=[{"Calculation":"Vessel charge @ 40% capacity","Value 1":"Vessel Volume","Value 2":"0.40",
         "Result (Min / Target / Max)":"Charge Volume / Weight"}])],
   w=2200),

 dict(folder="CDF - Operation Monitoring Worksheet", title="UF/DF Operation Monitoring Worksheet (Att 2)", kind="N", section="Att2 (§13-15)",
   reuses="NEW — wide interval log (TMP / 3 pressures / permeate flow / conductivity / vessel weight); no library block (Timer-table too narrow, generic parameterized table is a demo). Get Conductivity Meter = SMPL: Equipment Select",
   instructions=('Log operating parameters during Concentration 1 / Diafiltration / Concentration 2 using the same '
     'conductivity meter as set-up (Step 8.2), including temperature compensation. Per reading record the three '
     'transducer pressures (Feed PT-101 / Retentate PT-301 / Permeate PT-201) and computed &Delta;P, the retentate '
     'back-pressure valve opening (BPRV-301) and pump speed (P-101), crossflow flux, TMP (TMP-100), permeate flow '
     '(FT-201), permeate flux, total permeate volume (FQI-201), permeate UV (AIT-201), offline permeate conductivity '
     '&amp; pH, retentate agitator setting and product weight; the max feed pressure alarm (&le; 60 psig) must not be '
     'exceeded. Built new — no library block covers this wide interval log.'),
   header_fields=[("Get Conductivity Meter","b"),("Conductivity Meter ID","o"),("Conductivity Meter Description","o"),
     ("Conductivity Meter Cal Due","o")],
   cols=["@STAMP","~Time","PFeed (psig) PT-101","PRetentate (psig) PT-301","PPermeate (psig) PT-201","=ΔP (psid)",
     "Retentate Open (%) BPRV-301","Pump Speed (RPM) P-101","Crossflow (L/min/ft²)","TMP (psid) TMP-100",
     "Permeate Flow (L/min) FT-201","Permeate Flux (LMH)","Total Permeate Vol (L) FQI-201","Permeate UV (OD) AIT-201",
     "Permeate Cond. (mS/cm)*","Permeate pH*","Agitator Setting","Product Wt (kg)",PB],
   idx_label="#", witness_label="Witnessed By", w=3600),

 dict(folder="CDF - Continued Diafiltration Decision", title="Conditional Continued Diafiltration (block stack)", kind="R", section="§14",
   reuses="DE1 100 stack: CDF - Run Skid Recipe (DF1244_Diafiltration batch ID / start / setpoints) + CDF - Operation Monitoring Worksheet (in-process log) + SMPL: Record Scale Weight (net weight after DF + Scale ID/Cal Due) + SMPL: Calc Three Columns (product volume = net wt ÷ density) + SMPL: Equipment Select (pH/Cond meter) + SMPL: Solution Summary - Data Recording (permeate/retentate pH/cond/temp) + Dynamic Dropdown (Continue?) + SMPL: Record Numeric Value (additional diavolumes / permeate totalizer) + SMPL: Record Text Value (supervisor contacted on out-of-range)",
   desc="Run the diafiltration recipe and log parameters, record the net weight and compute product volume, then "
     "sample the permeate/retentate (pH/cond/temp); if in range proceed, else contact the supervisor, run additional "
     "diavolumes and re-sample. Additional 8012555 buffer posts via Goods Issue (Z_PICONS 261). Assembled from the "
     "Run Skid Recipe stack + Operation Monitoring + Record Scale Weight + Calc + Equipment Select + Solution Summary "
     "+ a Dynamic Dropdown + Record Numeric + Record Text. (The decision was published to the PI Sheet Sandbox as a "
     "flat form — that stays a representation.) No bespoke XStep.",
   blocks=[
     dict(bsub="CDF - Run Skid Recipe — DF1244_Diafiltration (batch ID / start / setpoints) — see Run Skid Recipe card"),
     dict(bsub="CDF - Operation Monitoring Worksheet — in-process log (its own Att-2 card)"),
     dict(bsub="SMPL: Record Scale Weight — net weight after Diafiltration",
       fields=[("Get Scale / Balance","b"),("Scale ID","o"),("Calibration Due Date","o"),
         ("Net Weight after DF (kg)","r")]),
     dict(head="SMPL: Calc Three Columns — Product Volume = Net Weight ÷ Density",
       cols=["Value 1","@OP:÷","Value 2","@OP:=","Result"], idx_label=None, index=False,
       rowdata=[{"Value 1":"Net Weight after DF","Value 2":"Density","Result":"Product Volume (L)"}]),
     dict(bsub="SMPL: Equipment Select — pH / Conductivity Meter",
       fields=[("Get pH / Cond Meter","b"),("pH / Cond Meter ID","o"),("Calibration Due Date","o")]),
     dict(head="SMPL: Solution Summary - Data Recording — permeate / retentate pH / cond / temp",
       cols=["Stream / Parameter","=Equipment","Min Target","Max Target","Actual Value","%Cond (High/Low)"],
       idx_label="#", index=True, rowdata=[{"Stream / Parameter":"Permeate pH"}]),
     dict(gate=("Continue Diafiltration? (pH in range?)","In-range"),
       note="In-range → proceed to Concentration 2. Out-of-range → contact supervisor, run additional diavolumes and re-sample."),
     dict(bsub="SMPL: Record Numeric Value — additional diavolumes / permeate totalizer",
       fields=[("Additional Diavolumes","r"),("Permeate Totalizer (L)","r")]),
     dict(bsub="SMPL: Record Text Value — supervisor contacted (out-of-range)",
       fields=[("Supervisor Contacted","r")])],
   w=2200),

 dict(folder="CDF - Recovery Calculations and Execution", title="Recovery Calculations & Execution (block stack)", kind="R", section="§16",
   reuses="DE1 100 stack: SMPL: Calc Three Columns / Three Variable Calc / Calc Range Values (recovery volume/weight range, buffer amount, net/volume after transfer) + SMPL: Equipment Select (mixer + scale) + SMPL: Material Consumption (recovery buffer + Dilution Vessel bag) + Dynamic Dropdown (method manual/recipe + 'Mixer Drive attached at tare?' Yes/No + dilution-required?) + CDF - Run Skid Recipe (recipe-control path) + Common - Transfer Tubing and Hosing Info (transfer line + Hose Cleaning) + SMPL: Timer for Start-End Process (transfer end) + SMPL: Mixing Time (Dilution Vessel mix ≥20 min) + SMPL: Sampling Record + SMPL: Sample Submission Chart (8012475-20) + SMPL: Record Scale Weight (gross/tare/net + Scale ID/Cal Due) + SMPL: Record Numeric Value + SMPL: Record Text Value (supervisor contacted)",
   desc="Compute the recovery target, choose method (manual/recipe), recover product to the Dilution Vessel, then "
     "transfer & mix the recovered product: record the transfer tubing (with hose-cleaning info) and the 'Mixer "
     "Drive attached at tare?' flag, stamp transfer end, mix ≥20 min, pull the 8012475-20 sample, weigh the vessel "
     "(gross/tare/net) and record concentration + DLIMS, then decide whether dilution is required. Label the PFI "
     "mixing bag (SOP-0107056). Recovery buffer posts via Goods Issue (Z_PICONS 261). Assembled from calc blocks + "
     "Equipment Select + Material Consumption + Dynamic Dropdown(s) + Run Skid Recipe + Transfer Tubing + Timer + "
     "Mixing Time + Sampling + Record Scale Weight + Record Numeric/Text. No bespoke XStep.",
   blocks=[
     dict(head="SMPL: Calc stack — recovery volume/weight range, buffer amount, net/volume after transfer",
       cols=["Calculation","Value 1","@OP:×","Value 2","@OP:=","Result (range)"],
       idx_label="#", index=True, rowdata=[{"Calculation":"Recovery Product Volume Range"}]),
     dict(gate=("Recovery Method?","By recipe control"),
       note="Manual → skip the recipe fields. By recipe control → run the recovery recipe below."),
     dict(bsub="CDF - Run Skid Recipe — recovery recipe (recipe-control path; see Run Skid Recipe card)"),
     dict(bsub="SMPL: Equipment Select — mixer + scale",
       fields=[("Get Mixer","b"),("Mixer ID","o"),("Get Scale / Balance","b"),("Scale ID","o"),
         ("Calibration Due Date","o")]),
     dict(head="SMPL: Material Consumption — recovery buffer + Dilution Vessel bag", gi=True,
       cols=["Component","Part No.","Batch No.","=Exp. Date",PB],
       idx_label="#", index=True, rowdata=[{"Component":"Recovery Buffer 8012555"}]),
     dict(fields=[("Mixer Drive attached at tare?","d","Yes / No")]),
     dict(bsub="Common - Transfer Tubing and Hosing Info — transfer line + hose cleaning (see Transfer Tubing card)"),
     dict(bsub="SMPL: Timer + SMPL: Mixing Time — transfer end & Dilution Vessel mix (≥ 20 min)",
       fields=[("Transfer End Time","t"),("Mixing Start","t"),("Mixing End","t"),("Mixing Duration (≥ 20 min)","o")]),
     dict(bsub="SMPL: Sampling Record + Sample Submission Chart — 8012475-20",
       fields=[("Sample Designation","o","8012475-20"),("Sampling Date & Time","t"),("DLIMS Project / Sample No.","r")]),
     dict(bsub="SMPL: Record Scale Weight — Dilution Vessel gross / tare / net",
       fields=[("Gross Weight (kg)","r"),("Tare Weight (kg)","o"),("Net Weight (kg)","o")]),
     dict(bsub="SMPL: Record Numeric Value — recovered product concentration + DLIMS",
       fields=[("Concentration (g/L)","r"),("DLIMS Project ID","r"),("DLIMS Sample ID","r")]),
     dict(gate=("Dilution Required?","No"),
       note="Based on the 8012475-20 concentration → dilution required (Section 17) or not."),
     dict(bsub="SMPL: Record Text Value — supervisor contacted (if applicable)",
       fields=[("Supervisor Contacted","r")])],
   w=2400),

 dict(folder="CDF - Dilution Decision and Calculations", title="Dilution Decision & Calculations (block stack)", kind="R", section="§17",
   reuses="DE1 100 stack: Dynamic Dropdown (dilution required? + dilution method + 'was there dilution?') + SMPL: Calc Three Columns / Calc Range Values (grams, PFI volume/weight range, buffer weight & volume, net/volume after sampling) + SMPL: Equipment Select ×3 (pump / stir plate / scale) + SMPL: Material Consumption (dilution buffer + Intermediate Vessel) + Common - Transfer Tubing and Hosing Info (buffer transfer line) + SMPL: Record Scale Weight (net buffer added, gross after attachments + Scale ID/Cal Due) + SMPL: Mixing Time ×2 (mix ≥20 min then ≥15 min) + SMPL: Sampling Record + SMPL: Sample Submission Chart (8012475-30 / -40) + SMPL: Solution Summary - Data Recording (pH/conductivity/temperature) + SMPL: Record Numeric Value (PFI concentration result) + SMPL: Record Text Value (supervisor contacted)",
   desc=f"Decide whether dilution is required (target {v('~180 g/L PFI')}); if so compute the dilution buffer amount, "
     "obtain the Intermediate Vessel & transfer tubing, add buffer to target weight (Goods Issue Z_PICONS 261), mix "
     "(≥20 min then ≥15 min), pull the -30/-40 samples and record pH/conductivity/temperature, weigh and compute PFI "
     "net weight/volume; label the Intermediate Vessel (SOP-0107056). Assembled from Dynamic Dropdown(s) + calc "
     "blocks + three Equipment Selects + Material Consumption + Transfer Tubing + Record Scale Weight + Mixing Time "
     "×2 + Sampling + Solution Summary + Record Numeric/Text. No bespoke XStep.",
   blocks=[
     dict(gate=("Dilution Required?","No"),
       note="Based on recovered-product concentration. No → N/A the dilution steps. Yes → perform dilution below."),
     dict(head="SMPL: Calc stack — grams, PFI volume/weight range, buffer weight & volume",
       cols=["Calculation","Value 1","@OP:×","Value 2","@OP:=","Result (range)"],
       idx_label="#", index=True, rowdata=[{"Calculation":"Weight of Dilution Buffer to Add"}]),
     dict(gate=("Dilution Method?","Connect buffer to vessel"),
       note="Pipette / cylinder / carboy → use an Intermediate Vessel. Direct → connect buffer to the Dilution Vessel."),
     dict(bsub="SMPL: Equipment Select ×3 — pump / stir plate / scale",
       fields=[("Get Pump","b"),("Pump ID","o"),("Get Stir Plate","b"),("Stir Plate ID","o"),
         ("Get Scale / Balance","b"),("Scale ID","o"),("Calibration Due Date","o")]),
     dict(head="SMPL: Material Consumption — dilution buffer + Intermediate Vessel", gi=True,
       cols=["Component","Part No.","Batch No.","=Exp. Date",PB],
       idx_label="#", index=True, rowdata=[{"Component":"Dilution Buffer 8012555"}]),
     dict(bsub="Common - Transfer Tubing and Hosing Info — buffer transfer line (see Transfer Tubing card)"),
     dict(bsub="SMPL: Record Scale Weight — buffer added / gross after attachments",
       fields=[("Net Buffer Added (kg)","r"),("Gross after attachments (kg)","r"),("Scale ID","o"),
         ("Calibration Due Date","o")]),
     dict(bsub="SMPL: Mixing Time ×2 — mix ≥ 20 min then ≥ 15 min",
       fields=[("Mix 1 Duration (≥ 20 min)","o"),("Mix 2 Duration (≥ 15 min)","o")]),
     dict(bsub="SMPL: Sampling Record + Sample Submission Chart — 8012475-30 / -40",
       fields=[("Sample Designation","o","8012475-30 / -40"),("Sampling Date & Time","t"),
         ("DLIMS Project / Sample No.","r")]),
     dict(head="SMPL: Solution Summary - Data Recording — pH / conductivity / temperature",
       cols=["Parameter","=Equipment","Min Target","Max Target","Actual Value","%Cond (High/Low)"],
       idx_label="#", index=True, rowdata=[{"Parameter":"pH"}]),
     dict(bsub="SMPL: Record Numeric Value — PFI concentration result", fields=[("PFI Concentration (g/L)","r")]),
     dict(bsub="SMPL: Record Text Value — supervisor contacted (if out of range)",
       fields=[("Supervisor Contacted","r")])],
   w=2400),

 dict(folder="CDF - PFI Storage Vessel and Filtration", title="PFI Storage Vessel, SHC Filter & Store (block stack)", kind="R", section="§18",
   reuses="DE1 100 stack: SMPL: Storage Vessel and Filter Inform (storage vessel + air/vent filter — field-verified) + SMPL: Additional Assembly (glass-bottle autoclave cycle/exp, if bottle) + SMPL: Material Consumption (SHC filter) + Common - Transfer Tubing and Hosing Info (transfer line + Hose Cleaning) + SMPL: Equipment Select (scale) + SMPL: Record Scale Weight (tare + gross after transfer) + SMPL: Timer for Start-End Process (transfer end) + SMPL: Calc Three Columns (net = gross − tare; volume = net ÷ density) + SMPL: Record Numeric Value (net weight) + SMPL: Solution Final Storage + Common - Hold Time Table (Att5 cross-record)",
   desc="Obtain & label the PFI storage vessel (bag or autoclaved glass bottle) and SHC filter, connect the transfer "
     "tubing, transfer the diluted product through the filter, stamp transfer end, weigh (tare + gross) and compute "
     "net weight/volume, then label and store and cross-record hold times into Attachment 5. Assembled from Storage "
     "Vessel and Filter Inform + Additional Assembly (bottle) + Material Consumption + Transfer Tubing + Equipment "
     "Select + Record Scale Weight + Timer + Calc + Record Numeric + Solution Final Storage + Hold Time Table. No "
     "bespoke XStep.",
   blocks=[
     dict(bsub="SMPL: Storage Vessel and Filter Inform — PFI storage vessel + air/vent filter",
       fields=[("Storage Vessel (Bag / Bottle) Part / Batch / Exp.","r"),("Air / Vent Filter Part / Batch / Exp.","r")]),
     dict(gate=("Glass bottle used?","No"),
       note="If a glass bottle, record its autoclave cycle / expiry below (SMPL: Additional Assembly)."),
     dict(bsub="SMPL: Additional Assembly — glass-bottle autoclave (if bottle)",
       fields=[("Glass Bottle Autoclave Cycle No.","r"),("Autoclave Exp. Date","r")]),
     dict(head="SMPL: Material Consumption — SHC product filter", gi=True,
       cols=["Filter","Part No.","Batch No.","=Exp. Date","Autoclave Cycle No.","~Autoclave Exp.",PB],
       idx_label=None, index=False, add_row=False, rowdata=[{"Filter":"PFI Product Filter (SHC)"}]),
     dict(bsub="Common - Transfer Tubing and Hosing Info — transfer line + hose cleaning (see Transfer Tubing card)"),
     dict(bsub="SMPL: Equipment Select + Record Scale Weight — tare & gross after transfer",
       fields=[("Get Scale / Balance","b"),("Scale ID","o"),("Calibration Due Date","o"),
         ("Tare Weight (kg)","r"),("Gross after transfer (kg)","r")]),
     dict(bsub="SMPL: Timer for Start-End Process — transfer end", fields=[("Transfer End Time","t")]),
     dict(head="SMPL: Calc Three Columns — net = gross − tare; volume = net ÷ density",
       cols=["Value 1","@OP:-","Value 2","@OP:=","Result"], idx_label="#", index=True,
       rowdata=[{"Value 1":"Gross Weight","Value 2":"Tare Weight","Result":"Net Weight (kg)"}]),
     dict(bsub="SMPL: Solution Final Storage — store PFI",
       fields=[("Storage Location","r"),("Storage Start Date & Time","dt")]),
     dict(bsub="Common - Hold Time Table — cross-record to Attachment 5 (see Hold Time card)")],
   w=2200),

 dict(folder="CDF - Post-Processing and Sanitization", title="Post-Processing: Cassette Re-use & Sanitization (block stack)", kind="R", section="§19 / §20",
   reuses="DE1 100 stack: SMPL: Record Text Value (WFI Bag / Valve-Tank ID + Charge Date/Time) + SMPL: Calc Three Columns (WFI Expiration = Charge + 24 h) + SMPL: Equipment Select (conductivity meter) + SMPL: Record Numeric Value (membrane-area setpoint, permeate/retentate flush setpoints, totalizer amount used) + CDF - Run Skid Recipe (DF1244_Flush batch ID / start) + Dynamic Dropdown (cassette re-use vs discard) + SMPL: Material Consumption (NaOH sanitization / storage buffer) + SMPL: Record Text Value (logbook / CIPDS batch + sanitization/NWP/storage dates + buffer batch) + SMPL: Timer for Start-End Process (start) + SXS: Text Instructions with Sign-off",
   desc="Set up WFI (Bag / Valve / Tank ID + Charge Date/Time, 24-h expiry computed), confirm the conductivity meter, "
     "enter the membrane surface-area setpoint, run the post-use DF1244_Flush (Clean-WFI), then decide cassette "
     "re-use vs discard and run the NaOH sanitization / storage recipe (NaOH via Goods Issue Z_PICONS 261), recording "
     "logbook/CIPDS batch, action dates and the buffer batch & amount used (totalizer sum). Assembled from Record "
     "Text + Calc + Equipment Select + Record Numeric + Run Skid Recipe + Dynamic Dropdown + Material Consumption + "
     "Timer + Text Instructions. No bespoke XStep.",
   blocks=[
     dict(bsub="SMPL: Record Text Value — WFI set-up",
       fields=[("Bag / WFI Valve-Tank ID","r"),("WFI Charge Date & Time","t")]),
     dict(head="SMPL: Calc Three Columns — WFI Expiration = Charge + 24 h",
       cols=["Value 1","@OP:+","Value 2","@OP:=","Result"], idx_label=None, index=False,
       rowdata=[{"Value 1":"WFI Charge Date/Time","Value 2":"24 h","Result":"WFI Expiration Date/Time"}]),
     dict(bsub="SMPL: Equipment Select — conductivity meter",
       fields=[("Get Conductivity Meter","b"),("Meter ID","o"),("Calibration Due Date","o")]),
     dict(bsub="SMPL: Record Numeric Value — membrane-area & flush setpoints",
       fields=[("Membrane Area Setpoint (m²)","r"),("Permeate Flush Setpoint (L)","r"),
         ("Retentate Flush Setpoint (L)","r")]),
     dict(bsub="CDF - Run Skid Recipe — DF1244_Flush (Clean-WFI) batch ID / start (see Run Skid Recipe card)"),
     dict(gate=("Cassettes re-used?","Discard"),
       note="Discard → NWP not required; clean & store the skid. Re-use → clean, WFI flush, NWP and store."),
     dict(head="SMPL: Material Consumption — NaOH sanitization / storage buffer", gi=True,
       cols=["Buffer","Batch No.","Amount Used (L)",PB],
       idx_label="#", index=True, rowdata=[{"Buffer":"0.5 N NaOH (Sanitization)"}]),
     dict(bsub="SMPL: Record Text Value — logbook / CIPDS batch + action dates",
       fields=[("Logbook No.","r"),("CIPDS Batch No.","r"),("Sanitization / NWP / Storage Dates","r")]),
     dict(bsub="SMPL: Timer for Start-End Process — start", fields=[("Start Time","t")]),
     dict(bsub="SXS: Text Instructions with Sign-off — BPR review / post-processing (§20)")],
   w=2200),
]

# ---- EBR phase plan (each XStep listed once, in execution order) ----
def _f(pred): return [s['folder'] for s in STEPS if pred(s['folder'])]
PHASES = [
 ("Process Order Information & Front Matter",
   ["Common - Order Header Details","Common - Signature Table","Common - Display BOM",
    "Common - Room and Equipment Assign","Common - Additional Manufacturing Supplies",
    "Common - Additional Solution Batches","Common - Process Notes and Global Limits"]),
 ("Reusable Building Blocks (instantiated across BOTH records)",
   ["Common - Incoming Product Information","Common - Product Vessel Weigh","Common - Calc Three Columns",
    "Common - Multi-Variable Calculation","Common - Product Mixing","Common - Product Sampling and DLIMS Submission",
    "Common - Product pH Conductivity Temperature","Common - Hold Time Table",
    "Common - Product Recirculation Worksheet","Common - Transfer Tubing and Hosing Info",
    "Common - Product Storage and Cross-Record","Common - Instruction and Sign-off",
    "Common - Yield Calculations","Common - Comments and Deviations","Common - Non-Routine Sampling Record"]),
 ("Virus Inactivation — PN 8012441 (Low pH, 2000 L)",
   _f(lambda f: f.startswith("VI -"))),
 ("Concentration & Diafiltration — PN 8012475 (Large Skid UF/DF, 2000 L)",
   _f(lambda f: f.startswith("CDF -"))),
]

BYF = {s['folder']: s for s in STEPS}
OLDREF = {s['folder']: s.get('section', '') for s in STEPS}

# ---- auto height (mirrors POC build) ----
import re, math
def _plain(t): return re.sub(r'<[^>]+>', '', t)
for s in STEPS:
    s.setdefault('rows', 1)
    w = s.get('w', 1740); cpl = max(120, int(w / 8.6))
    instr = s.get('instructions', '')
    prose = re.sub(r'<table.*?</table>', '', instr, flags=re.S)
    trs = instr.count('<tr>')
    lines = max(1, math.ceil(len(_plain(prose)) / cpl), prose.count('<li>') + 1) if instr else 1
    if trs: lines += trs + 4
    if 'blocks' in s:
        n = 0
        for b in s['blocks']:
            n += 1 if b.get('gate') else 0
            n += 1 if b.get('head') else 0
            n += 1 if b.get('bsub') else 0
            n += 1 if b.get('note') else 0
            n += 1 if b.get('witness') else 0
            if 'fields' in b: n += sum(3 if (len(it) > 1 and it[1] == 'dt') else 1 for it in b['fields'])
            elif 'cols' in b: n += 2 + (1 if b.get('add_row', True) else 0)
    elif 'form' in s: n = sum(3 if (len(it) > 1 and it[1] == 'dt') else 1 for it in s['form'])
    elif 'longtext' in s: n = len(s.get('signoffs', []))
    elif s.get('rowdata'): n = len(s['rowdata'])
    else: n = s['rows']
    n += len(s.get('header_fields', []))
    n += sum(3 if (len(it) > 1 and it[1] == 'dt') else 1 for it in s.get('footer_fields', []))
    s['h'] = 300 + n * 40 + lines * 26 + 80
