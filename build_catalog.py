#!/usr/bin/env python3
"""
Fetch astronomical catalogs from VizieR and OpenNGC, normalize them
into a single JSON database for Smart Astro Planner.

Run once:  python3 build_catalog.py
Produces:  catalog.json
"""

import json, csv, io, time, sys, re, math
from urllib.request import urlopen, Request
from urllib.parse import urlencode

OPENNGC_URL = "https://raw.githubusercontent.com/mattiaverga/OpenNGC/master/database_files/NGC.csv"
VIZIER_BASE = "https://vizier.cds.unistra.fr/viz-bin/asu-tsv"
UA = "SmartAstroPlanner-CatalogBuilder/1.0"

# ---------- helpers ----------

def vizier_fetch(source, columns, max_retries=3):
    """Fetch from VizieR classic API. Returns list of dicts with decimal degree coords."""
    cols = "_RAJ2000 _DEJ2000 " + columns
    params = urlencode({
        "-source": source,
        "-out.max": "unlimited",
        "-out": cols,
    })
    url = f"{VIZIER_BASE}?{params}"
    for attempt in range(max_retries):
        try:
            req = Request(url, headers={"User-Agent": UA})
            with urlopen(req, timeout=120) as resp:
                text = resp.read().decode("utf-8")
            lines = text.split("\n")
            data_lines = [l for l in lines if l and not l.startswith("#") and not l.startswith("-")]
            if len(data_lines) < 2:
                print(f"  -> 0 rows (no data)")
                return []
            header = data_lines[0].split("\t")
            # Skip units line (line after header)
            rows = []
            for line in data_lines[2:]:
                vals = line.split("\t")
                if len(vals) >= len(header):
                    rows.append(dict(zip(header, vals)))
            print(f"  -> {len(rows)} rows")
            return rows
        except Exception as e:
            print(f"  retry {attempt+1}/{max_retries}: {e}")
            time.sleep(5 * (attempt + 1))
    print(f"  FAILED after {max_retries} retries")
    return []


def pf(val):
    """Parse float, return None for empty/invalid."""
    if val is None:
        return None
    val = str(val).strip()
    if not val or val in ("None", "null", "NaN"):
        return None
    try:
        v = float(val)
        return v if math.isfinite(v) else None
    except ValueError:
        return None


def hms_to_deg(hms):
    if not hms or not hms.strip():
        return None
    parts = hms.strip().split(":")
    if len(parts) != 3:
        return None
    try:
        h, m, s = float(parts[0]), float(parts[1]), float(parts[2])
        return (h + m / 60 + s / 3600) * 15
    except ValueError:
        return None


def dms_to_deg(dms):
    if not dms or not dms.strip():
        return None
    s = dms.strip()
    sign = -1 if s.startswith("-") else 1
    s = s.lstrip("+-")
    parts = s.split(":")
    if len(parts) != 3:
        return None
    try:
        d, m, sec = float(parts[0]), float(parts[1]), float(parts[2])
        return sign * (d + m / 60 + sec / 3600)
    except ValueError:
        return None


def entry(id, name, aliases, obj_type, ra, dec, maj, mn, pa, catalog):
    e = {"id": id, "type": obj_type, "ra": round(ra, 6), "dec": round(dec, 6), "cat": catalog}
    if name:
        e["name"] = name
    if aliases:
        e["alias"] = aliases
    if maj is not None:
        e["maj"] = maj
    if mn is not None:
        e["min"] = mn
    if pa is not None:
        e["pa"] = pa
    return e


def vizier_entry(row, id_str, obj_type, catalog, maj_key=None, min_key=None, pa_key=None, name=None, aliases=None):
    """Build entry from a VizieR row with _RAJ2000/_DEJ2000."""
    ra = pf(row.get("_RAJ2000"))
    dec = pf(row.get("_DEJ2000"))
    if ra is None or dec is None:
        return None
    maj = pf(row.get(maj_key)) if maj_key else None
    mn = pf(row.get(min_key)) if min_key else None
    pa = pf(row.get(pa_key)) if pa_key else None
    return entry(id_str, name, aliases, obj_type, ra, dec, maj, mn, pa, catalog)


# ---------- OpenNGC ----------

def fetch_openngc():
    print("Fetching OpenNGC...")
    req = Request(OPENNGC_URL, headers={"User-Agent": UA})
    with urlopen(req, timeout=120) as resp:
        text = resp.read().decode("utf-8")
    reader = csv.DictReader(io.StringIO(text), delimiter=";")
    rows = list(reader)
    print(f"  -> {len(rows)} rows")

    type_map = {
        "G": "galaxy", "GGroup": "galaxy", "GPair": "galaxy", "GTrpl": "galaxy",
        "PN": "planetary_nebula",
        "OCl": "open_cluster", "Cl+N": "open_cluster",
        "GCl": "globular_cluster",
        "Neb": "emission_nebula", "HII": "emission_nebula", "EmN": "emission_nebula",
        "RfN": "reflection_nebula",
        "SNR": "snr",
    }

    entries = []
    for row in rows:
        obj_type = type_map.get(row.get("Type", "").strip())
        if obj_type is None:
            continue
        ra = hms_to_deg(row.get("RA", ""))
        dec = dms_to_deg(row.get("Dec", ""))
        if ra is None or dec is None:
            continue
        obj_id = row.get("Name", "").strip()
        if not obj_id:
            continue

        m = re.match(r"(NGC|IC)(\d+)", obj_id)
        nice_id = f"{m.group(1)} {int(m.group(2))}" if m else obj_id

        aliases = []
        messier = row.get("M", "").strip()
        if messier:
            aliases.append(f"M {messier}")
        idents = row.get("Identifiers", "")
        if idents:
            for alt in idents.split(","):
                alt = alt.strip()
                if alt and alt not in aliases:
                    aliases.append(alt)

        name = row.get("Common names", "").strip()

        entries.append(entry(
            nice_id, name, aliases or None, obj_type,
            ra, dec, pf(row.get("MajAx")), pf(row.get("MinAx")), pf(row.get("PosAng")),
            "OpenNGC"
        ))
    return entries


# ---------- VizieR catalogs ----------

def fetch_sharpless():
    print("Fetching Sharpless (VII/20)...")
    rows = vizier_fetch("VII/20/catalog", "Sh2 Diam")
    return [e for r in rows if (e := vizier_entry(
        r, f"Sh2-{r.get('Sh2','').strip()}", "emission_nebula", "Sharpless", "Diam"
    ))]


def fetch_vdb():
    print("Fetching van den Bergh (VII/21)...")
    rows = vizier_fetch("VII/21/catalog", "VdB BRadMax RRadMax")
    entries = []
    for r in rows:
        ra = pf(r.get("_RAJ2000"))
        dec = pf(r.get("_DEJ2000"))
        if ra is None or dec is None:
            continue
        # Use larger of blue/red radius as diameter
        br = pf(r.get("BRadMax"))
        rr = pf(r.get("RRadMax"))
        diam = None
        if br or rr:
            diam = max(br or 0, rr or 0) * 2  # radius -> diameter, already arcmin
        entries.append(entry(
            f"vdB {r.get('VdB','').strip()}", None, None,
            "reflection_nebula", ra, dec, diam, None, None, "vdB"
        ))
    return entries


def fetch_cederblad():
    print("Fetching Cederblad (VII/231)...")
    rows = vizier_fetch("VII/231/catalog", "Ced Dim1 Dim2 Name")
    entries = []
    for r in rows:
        e = vizier_entry(r, f"Ced {r.get('Ced','').strip()}", "reflection_nebula", "Ced", "Dim1", "Dim2")
        if e:
            n = r.get("Name", "").strip()
            if n:
                e["alias"] = [n]
            entries.append(e)
    return entries


def fetch_rcw():
    print("Fetching RCW (VII/216)...")
    rows = vizier_fetch("VII/216/rcw", "RCW MajAxis MinAxis IDs")
    entries = []
    for r in rows:
        e = vizier_entry(r, f"RCW {r.get('RCW','').strip()}", "emission_nebula", "RCW", "MajAxis", "MinAxis")
        if e:
            ids = r.get("IDs", "").strip()
            if ids:
                e["alias"] = [a.strip() for a in ids.split(",") if a.strip()]
            entries.append(e)
    return entries


def fetch_barnard():
    print("Fetching Barnard (VII/220A)...")
    rows = vizier_fetch("VII/220A/barnard", "Barn Diam")
    return [e for r in rows if (e := vizier_entry(
        r, f"B {r.get('Barn','').strip()}", "dark_nebula", "Barnard", "Diam"
    ))]


def fetch_ldn():
    print("Fetching LDN (VII/7A)...")
    rows = vizier_fetch("VII/7A/ldn", "LDN Area")
    entries = []
    for r in rows:
        ra = pf(r.get("_RAJ2000"))
        dec = pf(r.get("_DEJ2000"))
        if ra is None or dec is None:
            continue
        area = pf(r.get("Area"))
        diam = round(math.sqrt(area) * 60, 2) if area and area > 0 else None
        entries.append(entry(
            f"LDN {r.get('LDN','').strip()}", None, None,
            "dark_nebula", ra, dec, diam, None, None, "LDN"
        ))
    return entries


def fetch_lbn():
    print("Fetching LBN (VII/9)...")
    rows = vizier_fetch("VII/9/lbn", "Seq Area Diam1 Diam2 Name")
    if not rows:
        # Try alternate table name
        rows = vizier_fetch("VII/9/catalog", "Seq Area Diam1 Diam2 Name")
    entries = []
    for r in rows:
        ra = pf(r.get("_RAJ2000"))
        dec = pf(r.get("_DEJ2000"))
        if ra is None or dec is None:
            continue
        seq = r.get("Seq", r.get("LBN", "")).strip()
        d1 = pf(r.get("Diam1"))
        d2 = pf(r.get("Diam2"))
        area = pf(r.get("Area"))
        maj = d1
        mn = d2
        if maj is None and area and area > 0:
            maj = round(math.sqrt(area) * 60, 2)
        name = r.get("Name", "").strip()
        entries.append(entry(
            f"LBN {seq}", None, [name] if name else None,
            "emission_nebula", ra, dec, maj, mn, None, "LBN"
        ))
    return entries


def fetch_green_snr():
    print("Fetching Green SNR (VII/297)...")
    # This one had RAJ2000/DEJ2000 natively in TAP, try VizieR classic
    rows = vizier_fetch("VII/297/snrs", "SNR MajDiam MinDiam Names")
    return [e for r in rows if (e := vizier_entry(
        r, f"SNR {r.get('SNR','').strip()}", "snr", "Green", "MajDiam", "MinDiam",
        aliases=[a.strip() for a in r.get("Names","").split(",") if a.strip()] or None
    ))]


def fetch_planetary():
    print("Fetching Planetary Nebulae (V/84)...")
    rows = vizier_fetch("V/84/main", "PNG Name Idents")
    # Diameters are in a separate table; fetch them
    print("  Fetching PN diameters (V/84/diam)...")
    diam_rows = vizier_fetch("V/84/diam", "PNG oDiam rDiam")
    diam_map = {}
    for dr in diam_rows:
        png = dr.get("PNG", "").strip()
        od = pf(dr.get("oDiam"))
        rd = pf(dr.get("rDiam"))
        d = max(filter(None, [od, rd]), default=None)
        if png and d is not None and d > 0:
            if png not in diam_map or d > diam_map[png]:
                diam_map[png] = d

    entries = []
    for r in rows:
        ra = pf(r.get("_RAJ2000"))
        dec = pf(r.get("_DEJ2000"))
        if ra is None or dec is None:
            continue
        png = r.get("PNG", "").strip()
        name = r.get("Name", "").strip()
        idents = r.get("Idents", "").strip()
        aliases = []
        if name:
            aliases.append(name)
        if idents:
            for a in idents.split(","):
                a = a.strip()
                if a and a not in aliases:
                    aliases.append(a)
        # Diameter in arcsec -> arcmin
        diam = diam_map.get(png)
        if diam is not None:
            diam = round(diam / 60, 2)
        entries.append(entry(
            f"PN G{png}", None, aliases or None,
            "planetary_nebula", ra, dec, diam, None, None, "SECGPN"
        ))
    return entries


def fetch_open_clusters():
    print("Fetching Open Clusters (B/ocl)...")
    rows = vizier_fetch("B/ocl/clusters", "Cluster Diam")
    return [e for r in rows if (e := vizier_entry(
        r, r.get("Cluster","").strip(), "open_cluster", "DAML02", "Diam"
    ))]


# ---------- Hardcoded: IFN (Mandel-Wilson) ----------

IFN_OBJECTS = [
    {"id": "MW 1", "ra": 56.0, "dec": 19.5, "maj": 180},
    {"id": "MW 2", "ra": 170.0, "dec": 73.0, "maj": 120},
    {"id": "MW 3", "ra": 208.0, "dec": 40.0, "maj": 150},
    {"id": "MW 4", "ra": 231.5, "dec": 44.0, "maj": 90},
    {"id": "MW 5", "ra": 188.0, "dec": 29.0, "maj": 60},
    {"id": "MW 6", "ra": 151.5, "dec": 70.5, "maj": 120},
    {"id": "MW 7", "ra": 142.0, "dec": 67.0, "maj": 90},
    {"id": "MW 8", "ra": 135.0, "dec": 65.0, "maj": 90},
    {"id": "MW 9", "ra": 210.0, "dec": 53.0, "maj": 120},
]

def make_ifn():
    print("Adding IFN (Mandel-Wilson MW1-9)...")
    entries = [entry(o["id"], None, None, "ifn", o["ra"], o["dec"], o["maj"], None, None, "Mandel") for o in IFN_OBJECTS]
    print(f"  -> {len(entries)} rows")
    return entries


# ---------- Deduplication ----------

def deduplicate(all_entries):
    print("Deduplicating...")
    ngc_index = {}
    for e in all_entries:
        if e["cat"] == "OpenNGC":
            ngc_index[e["id"].upper().replace(" ", "")] = e

    result = []
    merged = 0
    for e in all_entries:
        if e["cat"] == "OpenNGC":
            result.append(e)
            continue

        found_ngc = None
        check_names = [e["id"]] + (e.get("alias") or [])
        for name in check_names:
            key = name.upper().replace(" ", "").replace("-", "")
            for prefix in ("NGC", "IC"):
                if key.startswith(prefix) and key in ngc_index:
                    found_ngc = ngc_index[key]
                    break
            if found_ngc:
                break

        if found_ngc:
            if "alias" not in found_ngc or found_ngc["alias"] is None:
                found_ngc["alias"] = []
            if e["id"] not in found_ngc["alias"]:
                found_ngc["alias"].append(e["id"])
            if found_ngc.get("maj") is None and e.get("maj") is not None:
                found_ngc["maj"] = e["maj"]
            if found_ngc.get("min") is None and e.get("min") is not None:
                found_ngc["min"] = e["min"]
            merged += 1
        else:
            result.append(e)

    print(f"  -> {merged} merged into OpenNGC, {len(result)} unique entries")
    return result


# ---------- Main ----------

def main():
    print("=== Smart Astro Planner — Catalog Builder ===\n")

    all_entries = []
    all_entries.extend(fetch_openngc())

    fetchers = [
        fetch_sharpless, fetch_vdb, fetch_cederblad, fetch_rcw,
        fetch_barnard, fetch_ldn, fetch_lbn,
        fetch_green_snr, fetch_planetary, fetch_open_clusters,
        make_ifn,
    ]
    for fetcher in fetchers:
        print()
        all_entries.extend(fetcher())

    print(f"\nTotal before dedup: {len(all_entries)}")
    result = deduplicate(all_entries)

    result.sort(key=lambda e: e["ra"])
    for e in result:
        del e["cat"]

    outfile = "catalog.json"
    with open(outfile, "w") as f:
        json.dump(result, f, separators=(",", ":"))

    size_mb = len(json.dumps(result, separators=(",", ":"))) / (1024 * 1024)
    print(f"\nWrote {outfile}: {len(result)} objects, {size_mb:.1f} MB")

    types = {}
    for e in result:
        types[e["type"]] = types.get(e["type"], 0) + 1
    print("\nBy type:")
    for t, n in sorted(types.items(), key=lambda x: -x[1]):
        print(f"  {t}: {n}")


if __name__ == "__main__":
    main()
