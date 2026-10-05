import re
from pathlib import Path

SOURCE = Path("Follese/233-jacob-andersen.md")
TARGET = Path("Follese/233-jacob-andersen.ged")
TEXT = SOURCE.read_text(encoding="utf-8")

pages = {
    int(m.group(1)): m.group(2)
    for m in re.finditer(r"^## Page (\d+)\n(.*?)(?=^## Page |\Z)", TEXT, re.M | re.S)
    if 10 <= int(m.group(1)) <= 117
}

number = re.compile(r"(?<!\d)(\d{4})(?!\d)")
date = re.compile(r"(?<!\d)(\d{1,2})[./](\d{1,2})[./](\d{2,4})(?!\d)")
year = re.compile(r"(?<!\d)(1[5-9]\d{2}|20\d{2})(?!\d)")
months = [None, "JAN", "FEB", "MAR", "APR", "MAY", "JUN", "JUL", "AUG", "SEP", "OCT", "NOV", "DEC"]

def clean(s):
    return re.sub(r"\s+", " ", s.replace("|", "I").replace("—", " ")).strip(" -")

def dates(s):
    found, occupied = [], []
    for m in date.finditer(s):
        d, mo, y = map(int, m.groups())
        y += 1900 if y < 30 else 2000 if y < 100 else 0
        found.append((m.start(), m.end(), d, mo, y))
        occupied.append((m.start(), m.end()))
    for m in year.finditer(s):
        if not any(a <= m.start() < b for a, b in occupied):
            found.append((m.start(), m.end(), None, None, int(m.group(1))))
    return sorted(found)

def ged_date(item, approx=False):
    if not item:
        return None
    _, _, d, mo, y = item
    if mo is not None and not 1 <= mo <= 12:
        return None
    prefix = "ABT " if approx else ""
    return f"{prefix}{d:02d} {months[mo]} {y}" if d and mo else f"{prefix}{y}"

def leading(line):
    s, tokens, pos = line.strip(), [], 0
    while pos < len(s):
        rest = s[pos:]
        m = re.match(r"^(\d{4})(?:[A-Za-z])?(?:\s+|$)", rest)
        if m:
            tokens.append(m.group(1)); pos += m.end(); continue
        m = re.match(r"^(?:[abc]\)|adp\.?|ekb\.?|fob\.?|bnr\.?|Ekb\.fob\.|—)\s*", rest, re.I)
        if m:
            pos += m.end(); continue
        m = re.match(r"^(\d{4})[.\-](?=\d{4})", rest)
        if m:
            tokens.append(m.group(1)); pos += m.end() - 1; continue
        break
    return tokens, s[pos:].strip()

def name_part(s):
    ds = dates(s)
    before = s[:ds[0][0]] if ds else s
    return clean(re.sub(r"^(?:[abc]\)|adp\.?|ekb\.?|fob\.?|bnr\.?|Fos\.|brn\.?|Ekb\.fob\.)\s*", "", before, flags=re.I))

people, order, spouses = {}, [], []
current_aner, family_prefix, last_key = [], [], None

for page, body in pages.items():
    first = True
    for raw in body.splitlines():
        line = clean(raw)
        low = line.lower()
        if low.startswith("aner"):
            current_aner = number.findall(line)
            family_prefix = []
            last_key = None
            first = True
            continue
        if not line or line.startswith(("Slektsnummer", "Slektsregister", "Slektsledd", "«Bakkenslekt")):
            continue
        nums, rest = leading(line)
        ds = dates(line)
        if not nums and not ds:
            continue
        if nums:
            if first:
                parts = current_aner[:] if current_aner and nums == [current_aner[-1]] else current_aner + nums
                family_prefix, first = parts[:-1], False
            elif len(nums) > 1:
                parts = current_aner + nums
                family_prefix = parts[:-1]
            else:
                parts = family_prefix + nums
            key = "_".join(parts)
            body_for_name = rest
        else:
            if not last_key:
                continue
            key = f"S{page}_{len(people) + len(spouses) + 1}"
            body_for_name = line
        name = name_part(body_for_name)
        if len(name) < 2 or name.lower() in {"ukjent", "i"}:
            continue
        birth = ged_date(ds[0], "ca" in body_for_name[:ds[0][0]].lower()) if ds else None
        death = ged_date(ds[1], "ca" in body_for_name[ds[0][1]:ds[1][0]].lower()) if len(ds) > 1 else None
        raw_note = line.replace("@", "(at)")[:220]
        if key.startswith("S"):
            spouses.append({"id": key, "name": name, "birth": birth, "death": death, "for": last_key, "page": page, "raw": raw_note})
        else:
            if key not in people:
                people[key] = {"name": name, "birth": birth, "death": death, "page": page, "raw": raw_note, "parts": parts}
                order.append(key)
            else:
                p = people[key]
                p["birth"] = p["birth"] or birth
                p["death"] = p["death"] or death
            last_key = key

def iid(key):
    return "@P" + re.sub(r"[^A-Za-z0-9_]", "", key) + "@"

unique_spouses = {}
for s in spouses:
    unique_spouses.setdefault((s["for"], s["name"], s["birth"]), s)

families, children = {}, {}
for key, p in people.items():
    parts = p["parts"]
    families.setdefault(key, "@F" + re.sub(r"[^A-Za-z0-9_]", "", key) + "@")
    if len(parts) > 1:
        parent = "_".join(parts[:-1])
        families.setdefault(parent, "@F" + re.sub(r"[^A-Za-z0-9_]", "", parent) + "@")
        children.setdefault(parent, []).append(key)

out = [
    "0 HEAD", "1 SOUR Direct-text import from Follese/233 - Slekta etter Jacob Andersen og Anna Olsdatter.pdf",
    "1 GEDC", "2 VERS 5.5.1", "2 FORM LINEAGE-LINKED", "1 CHAR UTF-8", "1 LANG nor"
]
for key in order:
    p = people[key]
    out += [f"0 {iid(key)} INDI", f"1 NAME {p['name']}"]
    if p["birth"]: out += ["1 BIRT", f"2 DATE {p['birth']}"]
    if p["death"]: out += ["1 DEAT", f"2 DATE {p['death']}"]
    if len(p["parts"]) > 1:
        out += [f"1 FAMC {families['_'.join(p['parts'][:-1])]}"]
    out += [f"1 NOTE Imported from register page {p['page']}.", f"2 CONT {p['raw']}", f"1 NOTE Lineage number: {key}"]
for s in unique_spouses.values():
    out += [f"0 {iid(s['id'])} INDI", f"1 NAME {s['name']}"]
    if s["birth"]: out += ["1 BIRT", f"2 DATE {s['birth']}"]
    if s["death"]: out += ["1 DEAT", f"2 DATE {s['death']}"]
    out += [f"1 NOTE Unnumbered spouse/partner from register page {s['page']}.", f"2 CONT {s['raw']}"]
for parent, fid in families.items():
    if parent not in people and parent not in children:
        continue
    out += [f"0 {fid} FAM"]
    if parent in people:
        out += [f"1 HUSB {iid(parent)}"]
    for s in unique_spouses.values():
        if s["for"] == parent:
            out += [f"1 WIFE {iid(s['id'])}"]
    for child in children.get(parent, []):
        out += [f"1 CHIL {iid(child)}"]
out.append("0 TRLR")
TARGET.write_text("\n".join(out) + "\n", encoding="utf-8")
print(f"pages={len(pages)} numbered_people={len(people)} spouses={len(unique_spouses)} families={len(families)}")
