# -*- coding: utf-8 -*-
"""Extract the OLD batch-record detailed steps (from the Complete Streamlined Analysis workbook)
and assign each to the NEW XStep that replaces it, so the EBR can show old-vs-new side by side.
Heuristic keyword assignment: unit-op-specific XSteps claim first, then Common blocks, then a
catch-all Instruction & Sign-off. Exposes OLD_BY_FOLDER = {folder: [(num,title,brief),...]}."""
import openpyxl, re

XLSX = r"C:\Users\carlo\Dev\TechSpecs\AZ Phase 3 Complete Streamlined BR Analysis\Complete_Streamlined_Batch_Record_Analysis v3.xlsx"

def _detailed(sheet):
    wb = openpyxl.load_workbook(XLSX, read_only=True, data_only=True)
    ws = wb[sheet]
    out = []
    for r in ws.iter_rows(values_only=True):
        rr = [("" if c is None else str(c).strip()) for c in r] + [""] * 6
        num, title, brief = rr[0], rr[1], rr[2]
        if num and title and num != "Step Num" and title != "Title":
            out.append((num, title, brief))
    return out

# (folder, [keyword regexes])  — tested against "title | brief", case-insensitive, first match wins.
VI_RULES = [
 ("VI - Treatment Vessel Setup", ["treatment vessel setup", "vi treatment vessel", "obtain.*vi treatment", "label vi treatment", "vessel setup"]),
 ("VI - Acid-Base pH Titration Table", ["acid treatment", "neutralization treatment", "titration", "acid addition", "base addition", "acid transfer", "base transfer", "confirm dip tube"]),
 ("VI - Incubation Timing and Sample", ["incubation", "incubated sample"]),
 ("VI - Temperature Decision Tree", ["decision tree", "temperature check", "starting product temperature", "warming", "warm"]),
 ("VI - Store Product and Hold-Time Link", ["store product", "document hold time", "store the", "storage start"]),
]
CDF_RULES = [
 ("CDF - Record CIPDS Skid Cassette Info", ["cipds", "skid information", "cassette", "support plate", "membrane info", "skid/cassette", "record.*skid"]),
 ("CDF - Minimum Membrane Surface Area", ["membrane surface area", "surface area"]),
 ("CDF - Process Input Calculations", ["process input", "capacity", "conc 1", "conc 2", "concentration 1", "concentration 2", "target volume", "target weight", "permeate volume", "process calc"]),
 ("CDF - Operation Monitoring Worksheet", ["operation parameter", "operating parameter", "monitoring", " tmp"]),
 ("CDF - Continued Diafiltration Decision", ["diafiltration", "diavolume"]),
 ("CDF - Recovery Calculations and Execution", ["recovery", "recover"]),
 ("CDF - Dilution Decision and Calculations", ["dilution", "dilute", "pfi conc"]),
 ("CDF - PFI Storage Vessel and Filtration", ["shc filter", "pfi storage", "storage vessel", "filtration", "obtain pfi", "sight glass"]),
 ("CDF - Post-Processing and Sanitization", ["post-use", "sanitization", "naoh", "post-processing", "re-use", "storage buffer"]),
 ("CDF - Run Skid Recipe", ["run df", "run the", "recipe", "df1244", "df_1244", "flush", "equilibration", "download and run", "equil", "start method", "wfi charge", "charge wfi"]),
]
COMMON_RULES = [
 ("Common - Measure pH Conductivity Temperature", ["measure ph", "ph, conductivity", "ph/cond", "conductivity, temperature", "measure final ph", "ph, conductivity, and temperature", "record results", "cond/temp", "permeate ph", "retentate/permeate"]),
 ("Common - Weigh Vessel and Net Weight", ["gross weight", "net weight", "tare weight", "weigh", "tare"]),
 ("Common - Mix Product", ["mix product", "mixing", "agitation", " mix "]),
 ("Common - Sampling Record", ["sample", "aliquot", "dlims", "submit"]),
 ("Common - Material Addition and Goods Issue", ["sap consumption", "bill of materials", "solution batch", "material info", "additional solution", "buffer", "reagent", "record.*batch"]),
 ("Common - Equipment and Instrument ID", ["meter standardization", "thermometer", "calibration", "meter id", "scale id", "equipment id", "record room", "data logger", "verify skid meter", "obtain.*label"]),
 ("Common - Product Recirculation Worksheet", ["recirculation", "recirc"]),
 ("Common - Transfer Tubing and Hosing Info", ["tubing", "hosing", "hose"]),
 ("Common - Hold Time Table", ["hold time"]),
 ("Common - Yield Calculations", ["yield"]),
 ("Common - Product Transfer Between Vessels", ["transfer"]),
 ("Common - Calculation", ["calculate", "calculation", "reverse calc"]),
 ("Common - Comments and Deviations", ["comment"]),
 ("Common - Instruction and Sign-off", [r"."]),  # catch-all
]

def _assign(steps, specific_rules):
    rules = specific_rules + COMMON_RULES
    res = {}
    for num, title, brief in steps:
        hay = (title + " | " + brief).lower()
        for folder, kws in rules:
            if any(re.search(k, hay) for k in kws):
                res.setdefault(folder, []).append((num, title, brief)); break
    return res

def build():
    vi = _detailed("Virus Inactivation")
    cdf = _detailed("Virus Filtration")
    a = _assign(vi, VI_RULES)
    b = _assign(cdf, CDF_RULES)
    out = {}
    for d in (a, b):
        for k, v in d.items(): out.setdefault(k, []).extend(v)
    return out, len(vi), len(cdf)

OLD_BY_FOLDER, N_VI, N_CDF = build()

if __name__ == "__main__":
    tot = 0
    for folder in sorted(OLD_BY_FOLDER):
        rows = OLD_BY_FOLDER[folder]; tot += len(rows)
        print(f"\n### {folder}  ({len(rows)} old steps)")
        for num, title, brief in rows[:60]:
            print(f"   {num:>6}  {title}")
    print(f"\nVI detailed={N_VI}  CDF detailed={N_CDF}  assigned={tot}")
