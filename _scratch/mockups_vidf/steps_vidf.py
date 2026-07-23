# -*- coding: utf-8 -*-
"""AZ Phase 3 (real project) - Virus Inactivation (PN 8012441) + Concentration & Diafiltration
(PN 8012475) XSteps. Reworked onto the POC (AZD8630 Affinity) model:
  kind R = reuse an existing SMPL / DE1 100 library XStep as-is (folder-only + a reuse card in the
           EBR, no new mock-up), V = reuse-as-variant (new mock-up + names the reused XStep),
           N = genuinely new (new mock-up). Only N and V carry form/cols/longtext content.
Groups: Common (shared reusable blocks + front/back matter), VI, CDF.
Renderer notation (build_mockups): plain col = entry; '='=computed/read-only; '%'=dropdown (CT04);
'~'=FM-stamped read-only; '@STAMP/@START/@END'=stamp button; '@BTN:x'=named button; '@OP:x'=calc
operator; form types: b=button o=output r=required entry d=dropdown t=time dt=date&time. PB=Performed By."""
def v(x): return f'<span class="v">{x}</span>'
PB = "Performed By*"

STEPS = [

# ================= COMMON — Process Order Information / front matter =================
 dict(folder="Common - Order Header Details", title="Order Header Details", kind="R", section="Header",
   reuses="DE1 100: Display Process Order Header Data (AZ Components) / SXS: SIMPL Order Header",
   desc="Product / PN, process order numbers, recorded by — standard SAP order header."),

 dict(folder="Common - Signature Table", title="Signature Table", kind="R", section="Personnel ID",
   reuses="DE1 100: SMPL Header: Signature Table",
   desc="Personnel identification: print name, signature, initials for everyone executing the record."),

 dict(folder="Common - Display BOM", title="Display BOM", kind="R", section="§4",
   reuses="DE1 100: Display BOM Material Table (AZ Components) / SMPL Header: Review BOM Details",
   desc=("Bill of Materials — equipment (VI Treatment Vessel / UF-DF skid, meters, scale, mixer, FIT) and "
     "components / filters / bags with SAP consumption. Reuses the standard BOM display XStep.")),

 dict(folder="Common - Room and Equipment Assign", title="Room & Equipment Assign", kind="R", section="§7 (VI 7.3-7.4 / C&D 7)",
   reuses="DE1 100: SMPL: Room/Equipment Assign + SMPL: Record Text Value",
   desc=("Record the process room and <b>assign, up front, every instrument / equipment used in the record</b> — "
     "pH / conductivity meter, thermometer, floor scale / balance, mixer, stir plate, pump — with a "
     "calibration-interval check (writing an equipment ID attests visual inspection + calibration). Downstream "
     "steps then pull from this assignment via a <b>Get [Type]</b> button (Get Scale / Balance, Get pH / Cond "
     "Meter, Get Thermometer, Get Mixer, Get Stir Plate, Get Pump) that populates that type's ID / Description "
     "(+ Cal Due for calibrated instruments). Reuses SMPL: Room/Equipment Assign + SMPL: Record Text Value.")),

 dict(folder="Common - Additional Manufacturing Supplies", title="Additional Manufacturing Supplies", kind="V", section="§4",
   reuses="SMPL: Additional Assembly + SMPL: Material Consumption (Z_PICONS Goods Issue)",
   instructions=('If additional materials (filter, bag, assembly, etc.) are used during processing, verify the '
     'material is acceptable per Section 4 and record its information; document the reason for the change in the '
     'Comments Section. Enter the Part No. &mdash; input validation displays the Material Description. Enter the '
     'Batch No. &mdash; the Exp. Date auto-populates. Serial No. / Autoclave ID / Exp. are recorded manually. '
     '<b>SAP consumption posts automatically via the Goods Issue process message (Z_PICONS, movement type 261).</b>'),
   cols=["MPR Step No.","Part No.","=Material Description","Batch No.","=Exp. Date","Serial No.",
     "Autoclave ID","~Autoclave Exp.",PB],
   witness_label="Witnessed By", w=2200),

 dict(folder="Common - Additional Solution Batches", title="Additional Solution Batches (Solution Switch)", kind="V", section="§5",
   reuses="SMPL: Solution Summary - Data Recording",
   instructions=('When a process solution must be replaced with a different batch during processing, record the '
     'switch: indicate the applicable step, confirm the new solution is the same Part No. as the one replaced, and '
     'record Part No. / Batch No. (and/or process order) / Exp. Date. Document the reason in the Comments Section. '
     'Enter the Batch No.; the Exp. Date auto-populates.'),
   cols=["Applicable Step No.","Part Number","Batch Number","=Exp. Date",PB], witness_label="Witnessed By", w=1700),

 dict(folder="Common - Process Notes and Global Limits", title="Process Notes & Global Limits (Acknowledgement)",
   kind="V", section="§6", longtext=True, signoffs=["Reviewed By"],
   reuses="DE1 100: SXS: Text Instructions with Sign-off (DE2 903: Long Text Instructions)",
   instructions=('Global process notes and limits that apply throughout the record, e.g.: all activities at '
     f'{v("15-27 °C")}; assume {v("1 L = 1 kg, 1 mL = 1 g")} unless otherwise noted; verify all solutions / raw '
     'materials / standards are within expiration before use; writing an equipment ID attests visual inspection '
     'and calibration check; all parameters are Targets / Alert Limits unless otherwise noted (contact '
     'supervisor / initiate deviation when alert limits are exceeded); NaOH is corrosive &mdash; wear a face '
     'shield (C&amp;D). The operator acknowledges these notes; each individual limit is enforced at the step '
     'where its parameter is captured.')),

# ================= COMMON — reusable building blocks =================
 dict(folder="Common - Product Vessel Weigh", title="Product Vessel Weigh", kind="R", section="VI §7/8/15 · C&D §9/11/16/17/18",
   reuses="DE1 100: SMPL: Record Scale Weight (Tare Weight / Select Vessel Type & Tare Weight variants)",
   desc=("Weigh a product vessel: press <b>Get Scale / Balance</b> to retrieve the scale assigned in Room & "
     "Equipment Assign — Scale / Balance ID + Description + Calibration Due Date auto-populate — then record gross "
     "weight; net weight computed (Gross − Tare, 1 kg = 1 L). Reuses the standard weight-pattern XStep.")),

 dict(folder="Common - Incoming Product Information", title="Incoming Product Information (Weight / Concentration / DLIMS)",
   kind="V", section="VI 7.5 · C&D 7.4-7.6", reuses="SMPL: Solution Summary - Data Recording",
   instructions=('Record the incoming / starting product characterization for each vessel or bag: <b>tare weight</b> '
     'and <b>net weight / volume</b> (kg = L), the <b>SoloVPE protein concentration</b> result (g/L, sample tested '
     'per SOP-0107091) with the DLIMS project / sample numbers it is reported under. Values carry from the upstream '
     'MPR where applicable. One row per vessel / bag. (Covers VI 7.5 Affinity Product Information and C&amp;D 7.4 '
     'Record VF Product Information.)'),
   cols=["Tare Weight (kg=L)","Net Weight / Volume (kg=L)","SoloVPE Concentration (g/L)",
     "DLIMS Project No.","DLIMS Sample No.",PB],
   idx_label="Vessel / Bag #", witness_label="Witnessed By", w=2100),

 dict(folder="Common - Calc Three Columns", title="Calc — Three Columns (Value1 op Value2 = Result)", kind="R",
   section="VI 7.12 / 8.10 / 14.15 · C&D §7/16/17",
   reuses="DE1 100: SMPL: Calc Three Columns",
   desc=("Two-operand calculation archetype (Value 1 [× ÷ + −] Value 2 = Result). Reused wherever a single "
     "two-input calc is needed — e.g. VI 7.12 Net Weight of Affinity product = Gross − Tare, membrane / volume "
     "calcs. Reuses SMPL: Calc Three Columns.")),

 dict(folder="Common - Multi-Variable Calculation", title="Multi-Variable Calculation (3-4 operand)", kind="V",
   section="C&D §12/16/17", reuses="SMPL: Three Variable Calc (extended to 4 variables)",
   instructions=('Multi-operand calculation archetype (mixed &times; &divide; + &minus; operators). Enter the '
     'measured operands; carried-forward and constant values are read-only; the result is computed. Used for the '
     'process-input, recovery and dilution calc chains. Shown: a three-operand example.'),
   cols=["Value 1","@OP:×","Value 2","@OP:+","Value 3","@OP:=","=Result",PB],
   index=False, add_row=False, witness_label="Verified By", w=2100),

 dict(folder="Common - Product Mixing", title="Product Mixing", kind="R", section="VI §15 · C&D §9/16/17",
   reuses="DE1 100: SMPL: Mixing Time (or SIMPL: Record Mixing and Agitation)",
   desc=("Mix product for the required duration (e.g. ≥ 15 min) per the applicable SOP (LevTech / MagMix / tank): "
     "press <b>Get Mixer</b> to retrieve the assigned mixer (Mixer ID + Description auto-populate), record agitation "
     "RPM, start/end time, computed duration. Reuses the weight+timer pattern XStep.")),

 dict(folder="Common - Product Sampling and DLIMS Submission", title="Product Sampling & DLIMS Submission", kind="R",
   section="VI §15/Att1 · C&D §8/14/16/17/Att3",
   reuses="DE1 100: SMPL: Sampling Record + SMPL: Sample Submission Chart",
   desc=("Remove the sample per Attachment 1/3 and SOP-0107097; aliquot & label per SOP-0107056; submit to the "
     "DLIMS storage location per SOP-0080295; stamp sampling date/time; record DLIMS project / sample numbers. "
     "Reuses SMPL: Sampling Record + SMPL: Sample Submission Chart.")),

 dict(folder="Common - Product pH Conductivity Temperature", title="Product pH / Conductivity / Temperature", kind="V",
   section="VI 7.1/15.5 · C&D 8.12/14.11/17", reuses="SMPL: Solution Summary - Data Recording (range-validated variant)",
   instructions=('Measure pH, conductivity and temperature of the product / effluent using the assigned offline '
     'instruments (per SOP-0080297 / SOP-0107117). Press <b>Get pH / Cond Meter</b> and <b>Get Thermometer</b> to '
     'retrieve the instruments assigned in Room &amp; Equipment Assign — each ID / Description / Calibration Due '
     'Date auto-populates. Each result is range-validated against the step limits (carried from the recipe); the '
     'UoM shows beside each value. <b>Contact the supervisor/designee if a result is out of specification.</b>'),
   header_fields=[("Get pH / Cond Meter","b"),("pH / Cond Meter ID","o"),("pH / Cond Meter Description","o"),
     ("pH / Cond Meter Cal Due","o"),
     ("Get Thermometer","b"),("Thermometer ID","o"),("Thermometer Description","o"),("Thermometer Cal Due","o")],
   cols=["Offline pH","=UoM","Conductivity","=UoM ","Temperature","=UoM  ",PB],
   rowdata=[{"=UoM":"pH","=UoM ":"mS/cm","=UoM  ":"°C"}], idx_label="#", witness_label="Witnessed By", w=1850),

 dict(folder="Common - Hold Time Table", title="Hold Time Table", kind="V", section="VI §19 (Att3) · C&D §9/§25 (Att5)",
   reuses="SMPL: Solution Summary - Data Recording (hold-time variant)",
   instructions=('Track product hold time across storage moves. For each hold, select the storage condition, '
     'stamp storage start and end; RT and 2-8 °C durations are computed separately. Totals are computed &mdash; '
     f'alert if RT total exceeds {v("72 h")} or the combined total exceeds {v("168 h")} (contact supervisor).'),
   cols=["Location","%Storage Temp","@STAMP","~Storage Start","@STAMP","~Storage End","=RT Hold (h)","=2-8°C Hold (h)",PB],
   rowdata=[{"%Storage Temp":"2-8 °C"}], idx_label="Hold #",
   footer_fields=[("Total RT Hold (h)","o"),("Total 2-8°C Hold (h)","o"),("Total Combined Hold (h)","o")],
   witness_label="Witnessed By", w=2100),

 dict(folder="Common - Product Recirculation Worksheet", title="Product Recirculation Worksheet", kind="N",
   section="VI Att6 · C&D Att7",
   instructions=('Record each product recirculation used to mix the product when a mixer is not used (referenced '
     'from the mixing step). Stamp the start and end times per recirculation; the duration is computed. '
     '<b>No existing DE1 100 XStep matched a search for &ldquo;recirculation&rdquo; &mdash; built new</b> (a '
     'start/end/duration timer worksheet; closest relative is the SMPL: Mixing Time timer pattern).'),
   cols=["Recirculation Step","@START","~Start Time","@END","~End Time","=Duration (min)",PB],
   idx_label="#", witness_label="Witnessed By", w=1900),

 dict(folder="Common - Transfer Tubing and Hosing Info", title="Transfer Tubing / Hosing Information", kind="R",
   section="VI Att5 · C&D Att1",
   reuses="DE1 100: SMPL: Material Consumption / SMPL: Additional Assembly",
   desc=("Record each transfer tubing / flex hose used: Part No., Batch No. (Exp. auto), autoclave cycle / expiry, "
     "hose serial no., cleaning batch ID / expiry. Reuses SMPL: Material Consumption / SMPL: Additional Assembly.")),

 dict(folder="Common - Product Storage and Cross-Record", title="Product Storage & Cross-Record", kind="R",
   section="VI 15.8 · C&D §9/§18",
   reuses="DE1 100: SMPL: Solution Final Storage (cross-record write-back authored in MBR)",
   desc=("Record the initial storage condition (RT / 2-8 °C) and storage start date/time, and map values into the "
     "Hold-Time attachment / cross-record the storage linkage to the next MPR. Reuses the storage-record pattern.")),

 dict(folder="Common - Instruction and Sign-off", title="Instruction & Sign-off", kind="R", section="VI §8/16/20 · C&D §11/20",
   reuses="DE1 100: SXS: Text Instructions with Sign-off (DE2 903: Long Text Instructions)",
   desc=("Reusable instruction-only / set-up shell (line & valve connections, dip-tube confirmation, N/A gates, "
     "product transfer between vessels, BPR review). The instruction text is authored per use in IV_INSTR; the "
     "operator reads it and signs. No data captured. Reuses Long Text Instructions (DE2 903).")),

 dict(folder="Common - Yield Calculations", title="Yield Calculations", kind="R", section="VI Att4 · C&D Att8",
   reuses="DE1 100: SMPL: Yield Calculations",
   desc=("Compute batch yield: % Yield = Final Product Mass ÷ Load Mass × 100 (masses carry from the weigh / "
     "concentration steps). Reuses SMPL: Yield Calculations.")),

 dict(folder="Common - Comments and Deviations", title="Comments / Deviations Section", kind="R", section="VI Att7 · C&D Att9",
   reuses="DE1 100: SXS: Phase Comments (no clean 'SMPL: Comments' — closest confirmed component)",
   desc=("Free-text log for comments and documented deviations (step no. + initials/date). Reuses SXS: Phase Comments.")),

 dict(folder="Common - Non-Routine Sampling Record", title="Non-Routine Sampling Record", kind="R", section="VI Att2 · C&D Att4",
   reuses="DE1 100: SMPL: Non-Routine Sampling Record",
   desc=("Ad-hoc samples requested by MEMO: process section, contents, container, quantity, designation, DLIMS. "
     "Reuses SMPL: Non-Routine Sampling Record.")),

# ================= VIRUS INACTIVATION only (PN 8012441) =================
 dict(folder="VI - Treatment Vessel Setup", title="VI Treatment Vessel Setup (Comprehensive)", kind="N", section="§8.4",
   instructions=('Set up the VI Treatment Vessel. The vessel is either a single-use <b>bag</b> or a <b>tank</b>, '
     'plus (optionally) a vent filter and a required set of product filters. Use each <b>Required?</b> dropdown to '
     'activate only the sections that apply &mdash; a section set to <i>No</i> is deactivated and its fields are '
     'N/A. Component consumption posts via the Goods Issue process message (Z_PICONS, movement type 261) on the '
     'marked tables (per line). <b>Label</b> the vessel per SOP-0107056 (&ldquo;AZD0543&rdquo;, &ldquo;VI Treatment '
     'Vessel&rdquo;, batch/part no., initials, date).'),
   blocks=[
     dict(gate=("Bag Required?", "Yes / No"), head="Bag Information (if applicable)", gi=True,
       cols=["Part No.", "Batch No.", "=Exp. Date", "Performed By*"], idx_label="Bag #", add_row=True),
     dict(head="Mixer Bag Attachments (at vessel tare weight)",
       fields=[("Mixer Drive Attached?", "d", "Yes / No"), ("Top Base Attached?", "d", "Yes / No"),
               ("Magnetic Clamp Attached?", "d", "Yes / No")]),
     dict(gate=("Tank Required?", "Yes / No"), head="Tank Information (if applicable)",
       fields=[("Tank ID", "r"), ("CIP Batch ID", "r"), ("CIP Exp. Date & Time", "dt"), ("Pressure Test ID", "r"),
               ("Pressure Test Date", "r"), ("SIP Batch ID", "r")]),
     dict(gate=("Vent Filter Required?", "Yes / No"), head="Vent Filter Information (if applicable)", gi=True,
       cols=["Part No.", "Batch No.", "=Exp. Date"], index=False, add_row=False),
     dict(head="Product Filter Information (required)", gi=True,
       cols=["Part No.", "Batch No.", "=Exp. Date", "Autoclave Cycle No.", "~Autoclave Exp.", "Performed By*"],
       idx_label="Filter #", add_row=True),
     dict(head="Tare Weight Information",
       note="If the collection vessel is a bag, the tare weight is obtained prior to attaching the product filter.",
       fields=[("Get Scale / Balance", "b"), ("Scale / Balance ID", "o"), ("Scale / Balance Description", "o"),
               ("Scale / Balance Cal Due", "o"), ("Tare Weight of VI Treatment Vessel (kg)", "r"),
               ("Filters attached when tare obtained", "d", "Product filter / Vent filter / No filters (bag)"),
               ("Recorded By", "r"), ("Witnessed By", "r")]),
   ], w=2000),

 dict(folder="VI - Acid-Base pH Titration Table", title="Iterative pH Titration Table (Acid / Base)", kind="N", section="§10 / 12 / 14",
   instructions=('Iterative pH adjustment by incremental buffer addition. Record initial pH / conductivity / '
     f'temperature and start time. Per addition: gross weight before &amp; after (net added and running total '
     f'computed), stamp the pH-sample time and record adjusted pH. Target per step &mdash; acid {v("pH 3.5 (NOR 3.4-3.6)")}, '
     f'neutralization {v("pH 7.2-7.6")}. <b>Base variant:</b> re-standardize the pH meter (pH 4.0/10.0) once pH '
     '&ge; 4.0. Buffer consumption posts via Goods Issue (Z_PICONS, 261) on the total net weight added.'),
   header_fields=[("Get Scale / Balance","b"),("Scale / Balance ID","o"),("Scale / Balance Description","o"),
     ("Scale / Balance Cal Due","o"),
     ("Get pH / Cond Meter","b"),("pH / Cond Meter ID","o"),("pH / Cond Meter Description","o"),("pH / Cond Meter Cal Due","o"),
     ("Get Thermometer","b"),("Thermometer ID","o"),("Thermometer Description","o"),("Thermometer Cal Due","o"),
     ("Initial pH","r"),("Initial Conductivity","r"),("Initial Temperature (°C)","r")],
   cols=["Gross Wt Before (kg)","Gross Wt After (kg)","=Net Added (kg)","=Total Net (kg)","@STAMP","~pH Sample Time","Adjusted pH",PB],
   idx_label="Addition #",
   footer_fields=[("Final pH Confirmed Time","t"),("Final pH","o"),("Final Conductivity","r"),
     ("Final Temperature (°C)","r"),("Incubation Start Time","t")],
   witness_label="Witnessed By", w=2300),

 dict(folder="VI - Incubation Timing and Sample", title="Incubation Timing & Incubated Sample", kind="N", section="§11 / 13",
   instructions=('Time the low-pH incubation. The start time carries from the acid titration. Take a mid-incubation '
     'temperature check (bag) and an incubated sample (pH / conductivity / temperature); stamp the end time. '
     f'Incubation duration is computed &mdash; target {v("75 min (NOR 60-240)")}.'),
   form=[("Incubation Start Time (from titration)","o"),
     ("Get Thermometer","b"),("Thermometer ID","o"),("Thermometer Description","o"),("Thermometer Cal Due","o"),
     ("Mid-Incubation Temperature (°C)","r"),
     ("Get pH / Cond Meter","b"),("pH / Cond Meter ID","o"),("pH / Cond Meter Description","o"),("pH / Cond Meter Cal Due","o"),
     ("Incubated pH","r"),("Incubated Conductivity","r"),
     ("Incubated Temperature (°C)","r"),("Incubation End Time","t"),("Incubation Duration (min)","o"),
     ("Performed By","r"),("Witnessed By","r")], w=1600),

 dict(folder="VI - Temperature Decision Tree", title="Starting / Transfer Temperature Decision", kind="N", section="§7.14 / 9",
   instructions=('Conditional temperature check. Measure the product temperature and select the outcome: '
     f'{v("18-25 °C")} &rarr; proceed to acid addition; {v("< 18 °C")} &rarr; start warming (mixing section); '
     f'{v("> 25 °C")} &rarr; contact the supervisor. The selected branch drives which downstream sections are '
     'active.'),
   form=[("Measured Temperature (°C)","r"),("Decision (18-25 proceed / <18 warm / >25 supervisor)","d","Select"),
     ("Performed By","r"),("Witnessed By","r")], w=1600),

 dict(folder="VI - Store Product and Hold-Time Link", title="Store VI Product & Hold-Time Link", kind="N", section="§15.8",
   instructions=('Store the neutralized VI product and document storage information. Select the storage '
     'condition, stamp the storage start date/time, and map the values into Attachment 3 (Hold Times via the '
     'reusable Hold Time Table).'),
   form=[("Storage Condition (RT / 2-8 °C)","d","2-8 °C"),("Storage Start Date & Time","dt"),
     ("Performed By","r"),("Witnessed By","r")], w=1600),

# ================= CONCENTRATION & DIAFILTRATION only (PN 8012475) =================
 dict(folder="CDF - Record CIPDS Skid Cassette Info", title="Record CIPDS / Skid / Cassette Information", kind="N", section="§7.2 / §11",
   instructions=('Record the UF/DF skid and membrane identity: Skid ID (DF-1244), CIPDS batch, Pellicon '
     'cassette lot / part, support-plate ID. Confirm the skid is within its post-sanitization storage window '
     f'({v("&le; 30 days")}) &mdash; if exceeded, re-sanitize before use. <b>Label</b> the Retentate Vessel '
     '(&ldquo;Retentate Vessel&rdquo;) and its manual valves (A&ndash;I) per SOP-0107056. Cassette / CIPDS '
     'component consumption posts via Goods Issue (Z_PICONS, 261).'),
   form=[("Skid ID","r"),("CIPDS Batch","r"),("Cassette Lot / Part No.","r"),("Support Plate ID","r"),
     ("Skid Storage &le; 30 days?","d","Yes / No"),
     ("Get Scale / Balance","b"),("Scale / Balance ID","o"),("Scale / Balance Description","o"),("Scale / Balance Cal Due","o"),
     ("Retentate Vessel Tare — Before Attach (kg)","r"),("Retentate Vessel Tare — After Attach (kg)","r"),
     ("Performed By","r"),("Witnessed By","r")], w=1600),

 dict(folder="CDF - Run Skid Recipe", title="Run Skid Recipe (Batch ID, Start, Setpoints)", kind="N", section="§8/10/13/15/19",
   instructions=('Download and run the named skid recipe per SOP-0107111 (Prep-WFI Flush, Equilibration, '
     'Concentration 1, Diafiltration, Concentration 2, Recovery, Clean-WFI Flush, Sanitization). Enter the batch '
     f'Name ID &mdash; format {v("MPR PartNumber_Phase_BatchNumber_Date")} &mdash; and stamp the start time. '
     'Verify flow paths / setpoints match the recipe; contact area management on any discrepancy. One row per '
     'recipe run. Buffer (PN 8012555 equilibration / DF buffer), WFI and NaOH consumed by the recipe phases '
     'post via Goods Issue (Z_PICONS, movement type 261).'),
   cols=["Recipe / Phase","Batch Name ID","@STAMP","~Start Date","~Start Time",PB],
   idx_label="Run #", witness_label="Witnessed By", w=2000),

 dict(folder="CDF - Minimum Membrane Surface Area", title="Calculate Minimum Membrane Surface Area", kind="V", section="§7.7",
   reuses="SMPL: Calc Three Columns / Three Variable Calc",
   instructions=('Calculate the minimum membrane surface area required for the load and verify the installed area '
     'meets it: Total Grams Product &divide; Max Loading (g/m²) = Minimum Membrane Area (m²). Confirm installed '
     'area &ge; minimum. (Section 7 also records VF product information and the CIPDS/skid material consumption, '
     'which posts via Goods Issue (Z_PICONS, 261).)'),
   cols=["=Total Grams Product (g)","@OP:÷","Max Loading (g/m²)","@OP:=","=Min Membrane Area (m²)",PB],
   index=False, add_row=False,
   footer_fields=[("Installed Membrane Area (m²)","r"),("Installed &ge; Minimum?","o")],
   witness_label="Verified By", w=2200),

 dict(folder="CDF - Process Input Calculations", title="Process Input Calculations", kind="N", section="§12",
   instructions=('Compute the process setpoints from the load: system capacity at 80 % / 40 %, Concentration 1 '
     'and Concentration 2 target volumes &amp; weights, and the diafiltration permeate volume range. Inputs '
     'carry from the product-info and membrane steps; densities are step-specific constants; results are '
     'read-only. (Individual calcs reuse the Multi-Variable Calculation archetype.)'),
   form=[("Starting Product Volume / Grams (from Step 7)","o"),("Target Conc 1 (g/L)","o"),
     ("Conc 1 Target Volume (L)","o"),("Conc 1 Target Weight (kg)","o"),("Diafiltration Volumes (DV)","r"),
     ("DF Permeate Volume Range (L)","o"),("Target Conc 2 (g/L)","o"),("Conc 2 Target Volume (L)","o"),
     ("Conc 2 Target Weight (kg)","o"),("Performed By","r"),("Verified By","r")], w=1700),

 dict(folder="CDF - Operation Monitoring Worksheet", title="UF/DF Operation Monitoring Worksheet (Att 2)", kind="N", section="Att2 (§13-15)",
   instructions=('Log operating parameters during Concentration 1 / Diafiltration / Concentration 2 at intervals '
     '(approx. every 20 min) using the same conductivity meter as set-up. Record TMP, feed / retentate / permeate '
     'pressures, permeate flow, conductivity and vessel weight; the max-pressure alarm must not be exceeded. Press '
     '<b>Get Conductivity Meter</b> to retrieve the meter — <b>it must match the meter used at set-up (Step 8.2)</b>.'),
   header_fields=[("Get Conductivity Meter","b"),("Conductivity Meter ID","o"),("Conductivity Meter Description","o"),
     ("Conductivity Meter Cal Due","o")],
   cols=["@STAMP","~Time","TMP (bar)","Feed Press. (bar)","Retentate Press. (bar)","Permeate Flow (LMH)",
     "Conductivity (mS/cm)","Vessel Weight (kg)",PB],
   idx_label="#", witness_label="Witnessed By", w=2300),

 dict(folder="CDF - Continued Diafiltration Decision", title="Conditional Continued Diafiltration", kind="N", section="§14",
   instructions=('At the end of the planned diafiltration, sample the permeate (pH / conductivity). If in range, '
     'proceed; if not, run additional diavolumes and re-sample. Repeat until in specification. Additional '
     'diafiltration buffer (PN 8012555) consumed posts via Goods Issue (Z_PICONS, 261).'),
   form=[("Get pH / Cond Meter","b"),("pH / Cond Meter ID","o"),("pH / Cond Meter Description","o"),("pH / Cond Meter Cal Due","o"),
     ("Permeate pH","r"),("Permeate Conductivity (mS/cm)","r"),
     ("Continue Diafiltration?","d","Yes / No"),("Additional Diavolumes (DV)","r"),
     ("Performed By","r"),("Witnessed By","r")], w=1600),

 dict(folder="CDF - Recovery Calculations and Execution", title="Recovery Calculations & Execution", kind="N", section="§16",
   instructions=('Compute the recovery target and recover product to the Dilution Vessel. Choose the recovery '
     'method (manual flush vs recipe). Buffer used in recovery posts via Goods Issue (Z_PICONS, 261). Obtain and '
     '<b>label</b> the PFI mixing bag per SOP-0107056. Record the recovered volume / weight. (Volume/weight calcs '
     'reuse the Multi-Variable Calculation archetype.)'),
   form=[("Target Recovery Volume (L)","o"),("Recovery Method (Manual / Recipe)","d","Select"),
     ("Get Mixer","b"),("Mixer ID","o"),("Mixer Description","o"),
     ("Get Scale / Balance","b"),("Scale / Balance ID","o"),("Scale / Balance Description","o"),("Scale / Balance Cal Due","o"),
     ("Recovered Weight (kg)","r"),("Recovered Volume / Concentration","o"),
     ("Performed By","r"),("Witnessed By","r")], w=1700),

 dict(folder="CDF - Dilution Decision and Calculations", title="Dilution Decision & Calculations", kind="N", section="§17",
   instructions=('Based on the recovered concentration vs the PFI target range, decide whether dilution is '
     f'required (target {v("~180 g/L PFI")}). If required, compute the dilution buffer amount; add buffer (Goods '
     'Issue, Z_PICONS 261), mix and sample. Obtain and <b>label</b> the &ldquo;Intermediate Vessel&rdquo; per '
     'SOP-0107056.'),
   form=[("Recovered Concentration (g/L)","o"),("Dilution Required? (Yes / No / Out-of-Range)","d","Select"),
     ("Target PFI Concentration (g/L)","o"),("Dilution Buffer Amount (kg)","o"),
     ("Addition Method (Pump / Gravity)","d","Select"),
     ("Get Pump","b"),("Pump ID","o"),("Pump Description","o"),
     ("Get Stir Plate","b"),("Stir Plate ID","o"),("Stir Plate Description","o"),
     ("Get Scale / Balance","b"),("Scale / Balance ID","o"),("Scale / Balance Description","o"),("Scale / Balance Cal Due","o"),
     ("Final Concentration (g/L)","r"),
     ("Performed By","r"),("Verified By","r")], w=1700),

 dict(folder="CDF - PFI Storage Vessel and Filtration", title="PFI Storage Vessel, SHC Filter & Store", kind="N", section="§18",
   instructions=('Obtain and label the PFI storage vessel and the SHC filter (record IDs / batch / expiry; '
     'consumption via Goods Issue, Z_PICONS 261). Transfer the diluted product through the SHC filter into the '
     'storage vessel, weigh, label and store; document hold times (Attachment 5).'),
   form=[("PFI Storage Vessel ID","r"),("SHC Filter Part / Batch / Exp.","r"),
     ("Get Scale / Balance","b"),("Scale / Balance ID","o"),("Scale / Balance Description","o"),("Scale / Balance Cal Due","o"),
     ("Net Weight / Volume (kg = L)","o"),("Storage Condition","d","2-8 °C"),("Storage Start Date & Time","dt"),
     ("Performed By","r"),("Witnessed By","r")], w=1700),

 dict(folder="CDF - Post-Processing and Sanitization", title="Post-Processing: Cassette Re-use & Sanitization", kind="N", section="§19 / §20",
   instructions=('After processing, decide whether the cassette is re-used or discarded, then run the post-use '
     'Clean-WFI flush and NaOH sanitization / storage recipe (NaOH consumption via Goods Issue, Z_PICONS 261). '
     'Record the storage batch and start time.'),
   form=[("Cassette Disposition (Re-use / Discard)","d","Select"),("NaOH Sanitization Batch","r"),
     ("Storage Batch","r"),("Sanitization / Storage Start Time","t"),
     ("Performed By","r"),("Witnessed By","r")], w=1700),
]

# ---- EBR phase plan (each XStep listed once, in execution order) ----
def _f(pred): return [s['folder'] for s in STEPS if pred(s['folder'])]
PHASES = [
 ("Process Order Information & Front Matter",
   ["Common - Order Header Details","Common - Signature Table","Common - Display BOM",
    "Common - Room and Equipment Assign","Common - Additional Manufacturing Supplies",
    "Common - Additional Solution Batches","Common - Process Notes and Global Limits"]),
 ("Reusable Building Blocks (instantiated across BOTH records)",
   ["Common - Incoming Product Information","Common - Product Vessel Weigh","Common - Calc Three Columns","Common - Multi-Variable Calculation",
    "Common - Product Mixing","Common - Product Sampling and DLIMS Submission",
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
            n += 1 if b.get('note') else 0
            if 'fields' in b: n += sum(3 if (len(it) > 1 and it[1] == 'dt') else 1 for it in b['fields'])
            elif 'cols' in b: n += 2 + (1 if b.get('add_row', True) else 0)  # header + row (+ add row)
    elif 'form' in s: n = sum(3 if (len(it) > 1 and it[1] == 'dt') else 1 for it in s['form'])
    elif 'longtext' in s: n = len(s.get('signoffs', []))
    elif s.get('rowdata'): n = len(s['rowdata'])
    else: n = s['rows']
    n += len(s.get('header_fields', []))
    n += sum(3 if (len(it) > 1 and it[1] == 'dt') else 1 for it in s.get('footer_fields', []))
    s['h'] = 300 + n * 40 + lines * 26 + 80
