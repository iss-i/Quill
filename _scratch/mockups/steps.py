# -*- coding: utf-8 -*-
def v(x): return f'<span class="v">{x}</span>'
PB="Performed By*"

# Cell-role prefixes on table columns:
#   @START / @END / @STAMP -> ▶ button (button + stamped field beside it)
#   ~Col  -> FM time/date stamp: read-only, filled by the adjacent button (clock)
#   =Col  -> computed read-only output (greyed, no clock)
# A column listed in a step's `rowdata` row-dict is a read-only PRE-FILLED default
# (a standard/constant value the process fixes, e.g. a setpoint or standard amount).

STEPS = [
 # ---------- Vessel / Setup ----------
 dict(folder="Virus Seed Identification", title="Virus Seed Identification",
   instructions=(f'Record the Master Seed identification and Last Testing Date below, then record each seed batch '
     f'used with its Working Seed identification, passage, volume and titer (up to three batches). Max passage '
     f'of seed is {v("X+6")}.'),
   header_fields=[("Master Seed Identification","r"),("Last Testing Date","r")],
   cols=["Seed Batch","Seed Identification","Passage","Volume (mL)","Titer",PB], rows=3, w=1900),

 dict(folder="Cell Identification", title="Cell Identification",
   instructions=(f'Record the Master Cell Stock and Production Stock Cell identification. '
     f'Max passage of cells must not exceed {v("X+30")}. Record cell bioreactor number and testing dates.'),
   form=[("Master Cell Stock Batch #","r"),("Last Testing Date","r"),("Production Stock Cell ID","r"),
     ("Batch #","r"),("Batch Date","r"),("Cell Bioreactor #","r"),("Performed By","r"),("Check By","r")]),

 dict(folder="Vessel and Single-Use Bag Setup", title="Vessel & Single-Use Bag Setup",
   instructions=('Install the single-use bag in the 2000L SUB per SOP XX-XXX-X. '
     f'NOTE: Close {v("2 of the 4")} SUB exhaust filters to prevent pressure accumulation (SUB is not designed '
     'for any pressure load); verify vent filters are not kinked. Record vessel and bag details.'),
   form=[("Vessel Number","r"),("Vessel Type","o","2000L SUB"),("Single Use Bag Lot #","r"),
     ("Expiration Date","r"),("Performed By","r"),("Check By","r")]),

 dict(folder="Probe Identification", title="Probe Identification",
   instructions=('Record the probe number and sleeve serial number for each probe installed: '
     'DO probes, TruFluor DO, pH probes and TruFluor pH.'),
   cols=["Probe Type","Probe No.","Sleeve Serial No.",PB], rows=5),

 dict(folder="Equipment Sterilization Verification", title="Equipment Sterilization Verification",
   instructions=('Attach probe/equipment sterilization sticker to this MD. Attaching the sterilization sticker '
     'verifies that all packed sterilized equipment has been checked for integrity and is acceptable for use. '
     'Record sterilization run and expiry per phase (Media Prep / Inoculation / Harvest / Inactivation / Dispense).'),
   cols=["Process Phase","Equipment ID","Sterilization Cycle / Run #","Sterilization Exp. Date",PB], rows=5),

 dict(folder="Assembly and Line Connections", title="Assembly & Line Connections", longtext=True,
   signoffs=["Performed By","Check By"],
   instructions=('Complete the following bioreactor connections per SOP XX-XXX-X, then sign off:'
     '<ul>'
     '<li>Clamp off all lines to the bag except exhaust, overlay, the hollow spargers and probe lines.</li>'
     '<li>Connect overlay (Air Flow-1) and pressure sensor to the controller.</li>'
     '<li>Connect sparger 1 from the controller to the hollow sparger at the bottom of the bag.</li>'
     '<li>Insert DO and pH probes into the bag and connect their respective cables.</li>'
     '<li>Insert the temperature probe into the bag.</li></ul>')),

 dict(folder="pH Probe Calibration", title="pH Probe Calibration",
   instructions=(f'Calibrate a bench-top pH meter per SOP XX-XXX. Adjust the bioreactor pH probe offset so it '
     f'matches the offline reading. Verify the pH controller is in {v("manual mode")} (no need to monitor pH for '
     f'this process). Record the final pH at plant.'),
   form=[("pH Probe No.","r"),("Offline pH","r"),("Probe Offset","r"),("Final pH at Plant","r"),
     ("Date & Time","dt"),("Performed By","r"),("Check By","r")]),

 dict(folder="DO Probe Calibration", title="DO Probe Calibration",
   instructions=('Once the vessel has reached the temperature set point, set the 0% and 100% calibration points '
     'for both electrochemical DO probes per SOP XX-XXX-X. Then set DO control to xx% on Auto, reduce stirrer to '
     'xx RPM, and zero the O2 totalizer. Enter the calibration values and stamp the completion time.'),
   cols=["DO Probe No.","Zero (nA)","Slope / Span (nA)","@STAMP","~Date","~Time",PB], rows=2),

 dict(folder="Controller Setpoint and Alarm Configuration", title="Controller Setpoint & Alarm Configuration",
   instructions=('Turn on the TCU connected to the SUB and set the controller setpoints per SOP XX-XXX-X. '
     'The standard set points are pre-filled below; record the actual value read back from the controller. '
     f'Load the appropriate alarm file ({v("Batch#_Alarms_ON")} at inoculation / '
     f'{v("Vessel_Process_Alarms_Off")} before harvest) as required.'),
   cols=["Parameter","Set Point","Actual",PB],
   rowdata=[{"Parameter":"Temperature","Set Point":"2x°C"},
            {"Parameter":"Agitator","Set Point":"5x RPM"},
            {"Parameter":"Vent Heater 1&2","Set Point":"3x°C"}]),

 # ---------- Media Prep ----------
 dict(folder="Component Addition", title="Component Addition",
   instructions=('Add components per the Inoculation Component Table. The component, manufacturer and standard '
     'planned amount are pre-filled; record the batch number, expiry date and amount added, then perform the SAP '
     'goods issue. Amounts are calculated per planned final volume.'),
   cols=["Component","Manufacturer","Amount","Batch Number","Exp. Date","Amount Added (L)","SAP",PB],
   rowdata=[{"Component":"Excell Media","Manufacturer":"In House","Amount":"QS to 2000L"},
            {"Component":"Insect Cell Suspension","Manufacturer":"In House","Amount":"1.0×10⁶ cells/mL"},
            {"Component":"200mM L-Glutamine","Manufacturer":"In House","Amount":"20 mL/L"},
            {"Component":"Gentamycin","Manufacturer":"In House","Amount":"0.1 mL/L"},
            {"Component":"Antifoam","Manufacturer":"In House","Amount":"<0.2 mL/L"}], w=1900),

 dict(folder="Fill Volume Calculation", title="Fill Volume Calculation",
   instructions=(f'Calculate the volume to fill the reactor before seed addition: '
     f'{v("Planned Final Volume")} &minus; {v("Seed Volume")} = {v("Fill Volume")}. '
     'Record the calculation.'),
   form=[("Standard Final Volume (L)","o","2000"),("Planned Final Volume (kg)","r"),("Seed Volume (kg)","r"),
     ("Fill Volume (kg)","o"),("Performed By","r"),("Check By","r")]),

 dict(folder="Antifoam Addition", title="Antifoam Addition", longtext=True,
   signoffs=["Performed By","Check By"],
   instructions=('Aseptically, in a sterile vessel, add the appropriate amount of xxx mM L-Glutamine, '
     'Gentamycin, and antifoam according to the component table.')),

 dict(folder="LAF Sanitization", title="LAF Sanitization",
   instructions=('Sanitize the LAF with the standard disinfectant. Record the room, LAF, disinfectant batch '
     'and expiry date.'),
   form=[("Disinfectant","o","X% H₂O₂"),("Room #","r"),("LAF #","r"),("Disinfectant Batch #","r"),
     ("Exp. Date","r"),("Performed By","r")]),

 dict(folder="Medium Addition", title="Medium Addition",
   instructions=(f'Transfer {v("1100+/-55 kg")} of medium (PN: {v("8006775")}) into the bioreactor per '
     f'SOP-0080692 or SOP-0080241. Specification for transfer amount is ({v("1045 – 1155 kg")}). '
     f'Post Addition Expiry Date is {v("5 days")} after medium charge (auto-calculated).'),
   cols=["@START","~Transfer Start Date","~Transfer Start Time","@END","~Transfer End Date","~Transfer End Time",
     "Amount Added","UoM","=Post Addition Exp. Date",PB], rowdata=[{"UoM":"kg"}], w=2000),

 # ---------- Infection ----------
 dict(folder="Cell Receipt and Transfer", title="Cell Receipt & Transfer",
   instructions=(f'Receive cells from the cell prep lab and attach the cell prep information to this MD. '
     f'Ensure the media is at {v("2x°C")} before transferring cells (up to 10 lb air pressure may be applied). '
     f'Stamp the receipt and transfer times; record cell tank and sterilization expiry.'),
   cols=["@STAMP","~Date Received","~Time Received","Cell Tank #","Sterilization Exp. Date","@STAMP",
     "~Transfer Time",PB], w=1900),

 dict(folder="Weighted-Average Titer", title="Weighted-Average Titer",
   instructions=('If multiple seed batches are used, calculate the weighted-average titer (refer to the Virus '
     'Seed Identification step). For each batch, record the Inv. Log of Titer and Seed Volume; the '
     f'{v("Weighted Log")} = Inv. Log of Titer &times; Seed Volume. The Final Inv. Log of Titer = '
     '(Total Weighted Log) &divide; (Total Volume) and is carried into the MOI Calculation.'),
   cols=["Seed Batch #","Inv. Log of Titer","Seed Volume (mL)","=Weighted Log",PB], rows=3),

 dict(folder="MOI Calculation", title="MOI Calculation",
   instructions=('Calculate the amount of virus seed needed using the planned conditions for infection: '
     f'({v("Reactor Fill Volume")} &times; {v("Cell Density")} &times; {v("MOI")}) &divide; '
     f'{v("Inv. Log Titer")} = Amount Seed Needed. Use the Final Inv. Log of Titer from the '
     'Weighted-Average Titer step if multiple seed batches were used.'),
   form=[("Reactor Fill Volume (mL)","r"),("Cell Density (cells/mL)","o","1.0×10⁶"),("MOI","o","0.2×"),
     ("Inv. Log Titer","r"),("Amount Seed Needed (mL)","o"),("Performed By","r"),("Check By","r")]),

 dict(folder="Actual MOI", title="Actual MOI",
   instructions=('After inoculation, calculate the Actual Plant MOI using the actual amount of seed added: '
     f'({v("Actual Amount Seed Used")} &times; {v("Inv. Log Titer")}) &divide; '
     f'({v("Cell Density")} &times; {v("Reactor Fill Volume")}) = Actual Plant MOI. Cell Density is the '
     'cell count at time of infection (carried from the Daily Observations / infection sample).'),
   form=[("Actual Amount Seed Used (mL)","r"),("Inv. Log Titer","r"),("Cell Density (cells/mL)","r"),
     ("Reactor Fill Volume (mL)","r"),("Actual Plant MOI","o"),("Performed By","r"),("Check By","r")]),

 dict(folder="Virus Seed Inoculation", title="Virus Seed Inoculation",
   instructions=('When the SUB reaches a cell density of approximately '
     f'{v("1.0×10⁶ cells/mL")}, aseptically add the thawed virus seed to the bioreactor. '
     'Record the cell count and stamp the start and finish times of the addition.'),
   cols=["Cell Count (×10⁶ cells/mL)","@START","~Start Time","@END","~End Time",PB], rows=1),

 dict(folder="Thaw and Add Virus Seed", title="Thaw & Add Virus Seed", longtext=True,
   signoffs=["Performed By","Check By"],
   instructions=('Thaw the required amount of virus seed in a bath of disinfectant (the bath should be no '
     f'warmer than {v("2x°C")}). Add the thawed seed to the bioreactor.')),

 dict(folder="Inoculation Finish Time and SUB Label", title="Inoculation Finish Time & SUB Label",
   instructions=('Stamp the inoculation finish time and label the SUB as: Virus code / serial # / date.'),
   form=[("Inoculation Finish Time","t"),("SUB Label (Virus code / serial # / date)","r"),
     ("Performed By","r"),("Check By","r")]),

 dict(folder="Waste Inactivation", title="Waste Inactivation",
   instructions=(f'Kill any remaining cells and seed with Hypochlor (per VSM 800.56) at {v("100 mL/L")} and discard. '
     f'A minimum of {v("10 minutes")} disinfectant contact time is required before discard. Stamp the start/end '
     'times and record volumes and disinfectant.'),
   cols=["@START","~Start Time","Vol. Seed Discarded (mL)","Vol. Cells Discarded (mL)","@END","~End Time",
     "Disinfectant Batch #","Exp. Date",PB], rows=1, w=2000),

 # ---------- Culture / Harvest ----------
 dict(folder="Daily Observations", title="Daily Observations",
   instructions=('Sample the reactor daily and record bioreactor conditions in the Daily Observations table; '
     'stamp the sample date/time each day. '
     f'Ensure parameters are in range (Temp {v("25–29°C")}, DO {v("20–100%")}, RPM {v("55")}). '
     'If out of range, contact the Supervisor and comment on any corrective action taken.'),
   cols=["@STAMP","~Date","~Time","Temp (°C)","RPM","pH / Probe","External pH","DO% / Probe","O2 Consumption (L)",
     "CPE %","Cell Count Live","Cell Count Dead",PB], rows=3, w=2160),

 dict(folder="Sample Submission", title="Sample Submission",
   instructions=('Pull samples during processing and submit to QC. Record sample type, quantity/volume, storage '
     'condition and stamp the submission date. E.g. Retention {rt} freeze (-70°C); Bacteria {bc} '
     'store (4°C); Sterility / Densitometry as required.').format(rt=v("4×3mL"), bc=v("1×3mL")),
   cols=["Sample Type","Qty × Volume","Storage Condition","@STAMP","~Date Submitted",PB], rows=4),

 dict(folder="Harvest - Unifuge Centrifugation", title="Harvest (Unifuge Centrifugation)",
   instructions=(f'Connect the Unifuge to the harvest port. Harvest the antigen by passing {v("100%")} of the '
     f'bioreactor volume through the Unifuge at a target {v("3 L/min")}, {v("3000 G")}. Record PBS used '
     f'(SAP write-off), harvest tank weight, and stamp the start/finish times.'),
   cols=["@START","~Start Time","Unifuge #","Module Lot / S/N","Harvest Tank #","Harvest Tank Steril. Exp.",
     "SUB Vol. at Start (L)","PBS Batch #","PBS Exp. Date","PBS Amount (L)","SAP","@END","~End Time",
     "Harvest Tank Weight (kg)",PB], rows=1, w=2600),

 dict(folder="Cold Storage", title="Cold Storage",
   instructions=(f'Seal carboys/pools with white tape and transfer to the freezer per SOP XX-XXX-X. '
     f'First at {v("&le; -20°C")} then at {v("&le; -40°C")}. Stamp the date/time and record freezer and temperature.'),
   cols=["Container","Freezer #","Temp (°C)","@STAMP","~Date","~Time",PB], rows=2),

 dict(folder="Filter Integrity Test", title="Filter Integrity Test",
   instructions=('Perform filter integrity testing on the SUB filters per SOP XX-XXX-X using the Millipore '
     'Integritest 5 instrument. Press Get Filter to populate the Filter ID and Filter Description. Attach '
     'integrity test results for each filter tested and record the result.'),
   cols=["@BTN:Get Filter","=Filter ID","=Filter Description","Test Type","Result (Pass/Fail)","@STAMP","~Date",PB],
   rows=1, w=2000),

 dict(folder="SUB Filter Decontamination", title="SUB Filter Decontamination",
   instructions=('Decontaminate the SUB filters by autoclave. Stamp the date and record the autoclave number and cycle number.'),
   form=[("Date","t"),("Autoclave #","r"),("Cycle #","r"),("Performed By","r")]),

 # ---------- Inactivation / Downstream ----------
 dict(folder="BEI Cyclization", title="BEI Cyclization",
   instructions=(f'Calculate volume of BEI needed: {v("Antigen Volume &divide; 9")} = Volume of BEI. The component '
     'and standard amount/mL are pre-filled; measure each component, combine BEA powder with WFI then add NaOH '
     'solution and adjust to final formulation volume with WFI. (Cyclization stir time and temperature are '
     'recorded in the BEI Cyclization Hold step; post-cyclization pH in the pH Adjustment step.) CAUTION: BEI is '
     'a potential mutagen — work in a ventilation hood / PAPR.'),
   cols=["Component","Manufacturer / Batch #","Exp. Date","Amount / mL","Volume to Add (mL)","SAP",PB],
   rowdata=[{"Component":"BEA","Amount / mL":"0.0205 g"},
            {"Component":"NaOH Pellets","Amount / mL":"0.007 g"},
            {"Component":"Sterile WFI","Manufacturer / Batch #":"In House","Amount / mL":"1 mL"}]),

 dict(folder="BEI Cyclization Hold", title="BEI Cyclization Hold",
   instructions=(f'Stir the solution at {v("3x°C &plusmn;1°C")} for {v("1 hour")} to complete cyclization. Stamp '
     'the cyclization start and stop times and record the temperature at each. Use the BEI solution within x '
     'hours of the stop time.'),
   cols=["@START","~Start Date","~Start Time","Start Temp (°C)","@END","~End Time","Stop Temp (°C)",PB], w=1700),

 dict(folder="Viral Inactivation", title="Viral Inactivation",
   instructions=(f'Install the SUM bag in the reservoir tank; transfer the pre-warmed virus fluid and record the '
     f'volume (scale value). Set Temperature {v("XX°C")}, Agitator {v("XXX rpm")}. Add BEI solution through a '
     f'{v("0.xx μm")} filter while mixing. Transfer to a second SUM bag, set parameters and enable alarms. '
     f'Mix slowly at {v("3x°C &plusmn;2°C")} for ~xx hr; stamp the inactivation start/stop times.'),
   cols=["@START","~Start Time","Start Temp (°C)","SUM / Tank #","Bag Serial #","Steril. Exp. Date",
     "Vol. Virus Fluid (mL)","Vol. BEI Added (mL)","@END","~Stop Time","Stop Temp (°C)","=New Antigen Vol. (mL)",PB],
   rows=1, w=2500),

 dict(folder="pH Adjustment", title="pH Adjustment",
   instructions=(f'Record the pH of the virus fluids and adjust to target ({v("7.x &plusmn; 0.3")}) using HCl or NaOH '
     'as necessary. Record acid/base batch, expiry and amount added.'),
   form=[("Initial pH","r"),("Final pH","r"),("HCl Batch #","r"),("HCl Exp. Date","r"),
     ("NaOH Batch #","r"),("NaOH Exp. Date","r"),("Amount Added (mL)","r"),("Performed By","r"),
     ("Check By","r")]),

 dict(folder="Neutralization", title="Neutralization",
   instructions=(f'At the end of inactivation, add {v("1 mL of 3M Sodium Thiosulfate")} per {v("XXX mL")} of '
     f'inactivated virus fluids to yield a final concentration of {v("30 mM")}: Vol. of 3M Na-thio = Antigen '
     f'Volume {v("&divide; 100")}; New Antigen Volume = Antigen Volume + Vol. 3M Na-thio. Record the component '
     'in the Neutralization Component Table.'),
   cols=["=Component","Batch Number","Exp. Date","Antigen Volume (mL)","=Vol. 3M Na-Thio (mL)",
     "=New Antigen Vol. (mL)","SAP",PB], w=2000),

 dict(folder="Neutralization Hold", title="Neutralization Hold",
   instructions=(f'Allow the antigen to neutralize for {v("1 to 4 hours")}, mixing slowly at {v("XXX rpm")}. '
     'Stamp the start and stop times and record the temperature at each.'),
   cols=["@START","~Start Time","Start Temp (°C)","@END","~End Time","Stop Temp (°C)",PB], w=1600),

 dict(folder="Formulation", title="Formulation",
   instructions=(f'Add Gentamycin (final {v("0.000X mL/mL")}) and 10% Thimerosal (final {v("1:10,000")}). '
     'The component and standard final concentration are pre-filled. Pull pre- and post-Thimerosal samples and '
     'record each component addition and the resulting antigen volume. NOTE: samples must specify whether they '
     'contain Thimerosal.'),
   cols=["Component","Batch #","Exp. Date","Final Concentration","Volume Added (mL)","=New Antigen Vol. (mL)","SAP",PB],
   rowdata=[{"Component":"Gentamycin","Final Concentration":"0.000X mL/mL"},
            {"Component":"10% Thimerosal","Final Concentration":"1:10,000"}]),

 dict(folder="Bulk Dispense and Disposition", title="Bulk Dispense & Disposition",
   instructions=(f'Dispense the antigen into pools and store at {v("&le; -20°C")}. Label each pool with material #, '
     'batch #, pool #, pool volume and dispensing date. Record the bulk disposition and bottles used.'),
   cols=["Pool Number","Volume / Pool (mL)","=Total Volume (mL)","Freezer #","Temp (°C)","Bottles Batch #",
     "Bottles Used (ea)",PB], rows=3, w=2000),

 dict(folder="Label Control and Reconciliation", title="Label Control & Reconciliation",
   instructions=('Record labels applied to carboys, pools and bottles (material #, batch #, pool #, volume, date). '
     'Verify all pools for label accuracy before sending to storage, and reconcile bottle/label usage.'),
   cols=["Item Labeled","Material #","Batch #","Quantity",PB], rows=3, witness_label="Verified By"),

 dict(folder="Comments", title="Comments",
   instructions=('Record any comments, deviations, or corrective actions taken during the process. '
     'When proceeding with comments, the supervisor/designee is responsible for contacting the appropriate personnel.'),
   cols=["Comment / Deviation","Corrective Action",PB], rows=3),

 # ---------- Gap-closing XSteps ----------
 dict(folder="Transfer Line Clip-Off", title="Transfer Line Clip-Off", longtext=True,
   signoffs=["Performed By","Check By"],
   instructions=('Clipster off the lines used to transfer components, cells, and seed to the reactor, then '
     'sign off.')),

 dict(folder="Harvest Controller Shutdown", title="Harvest Controller Shutdown", longtext=True,
   signoffs=["Performed By","Check By"],
   instructions=(f'After harvesting approximately {v("60%")} of the SUB volume (~1200L for a 2000L batch), '
     'turn off the vent heaters, agitator, DO, and temperature control, then sign off.')),

 dict(folder="BEI Waste Neutralization", title="BEI Waste Neutralization",
   instructions=('Neutralize the remaining BEI using 3M Na-thiosulfate: run it into the first SUM bag/tank '
     'through the drain tube, then place the bag in a yellow barrel and label it as Hazardous waste (if '
     'applicable). Record the BEI reconciliation and disinfectant details.'),
   form=[("3M Na-Thiosulfate Batch #","r"),("Exp. Date","r"),("Volume of BEI Formulated (mL)","r"),
     ("Volume of BEI Added (mL)","r"),("Volume of BEI Discarded (mL)","r"),("Vol. 3M Na-Thio Added (mL)","r"),
     ("Performed By","r")]),

 dict(folder="Controller and Gas Flow Verification", title="Controller & Gas Flow Verification", longtext=True,
   signoffs=["Performed By","Check By"],
   instructions=('From the controller&rsquo;s main screen, verify the following per SOP XX-XXX-X, then sign off:'
     '<ul>'
     f'<li>{v("Air Flow-1")} is flowing to the overlay.</li>'
     f'<li>{v("Air Flow-2, N2, CO2, O2 Flow-1 and O2 Flow-2")} are flowing to the hollow sparger.</li>'
     '<li>Visually inspect the bottom of the bag for wrinkles.</li></ul>')),

 dict(folder="Pre-Inactivation Thaw", title="Pre-Inactivation / Thaw",
   instructions=(f'Pull the harvest carboys from the freezer with ample time to thaw and warm to {v("3x°C")}. '
     f'Pre-warm Sterile WFI for BEA/BEI cyclization to {v("3x°C")} the night before inactivation. '
     'Stamp the thaw/warm-up date/time; the target temperature is pre-filled.'),
   cols=["Item (Carboys / WFI)","@STAMP","~Date","~Time","Target Temp (°C)",PB],
   rowdata=[{"Item (Carboys / WFI)":"Harvest Carboys","Target Temp (°C)":"3x°C"},
            {"Item (Carboys / WFI)":"Sterile WFI","Target Temp (°C)":"3x°C"}]),

 dict(folder="Vessel Transfer", title="Vessel Transfer",
   instructions=('Aseptically transfer fluid between vessels (e.g., carboys to the inactivation bag/tank, or '
     'neutralized antigen to the dispense tank). Verify the scale reads zero before transfer where applicable. '
     'Record source, destination, volume transferred and stamp the start/end times.'),
   cols=["@START","~Start Time","Source Vessel","Destination Vessel","Dest. Steril. Exp.","Volume Transferred (mL)",
     "@END","~End Time",PB], rows=1, w=2040),

 dict(folder="SAP and Excel Transaction Record", title="SAP & Excel Transaction Record",
   instructions=('Record completion of the batch SAP and Excel transactions (goods issues, write-offs, dispense '
     'postings). Record the reference and performer, and stamp the date for each system.'),
   cols=["Transaction System","Transaction / Reference","@STAMP","~Date",PB],
   rowdata=[{"Transaction System":"SAP"},{"Transaction System":"Excel"}]),
]

import re, math
def _plain(t): return re.sub(r'<[^>]+>','',t)
for s in STEPS:
    s.setdefault('rows',1)
    w=s.get('w',1740)
    cpl=max(120,int(w/8.6))
    instr_html=s.get('instructions','')
    lines=max(1, math.ceil(len(_plain(instr_html))/cpl), instr_html.count('<li>')+1)
    if 'form' in s: n=sum(3 if (len(it)>1 and it[1]=='dt') else 1 for it in s['form'])
    elif 'longtext' in s: n=len(s.get('signoffs',[]))
    elif s.get('rowdata'): n=len(s['rowdata'])
    else: n=s['rows']
    n += len(s.get('header_fields',[]))
    s['h']=300 + n*40 + lines*26 + 80
