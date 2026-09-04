#!/usr/bin/env python3
"""
Validate a batch of generated plant records and merge them into index.html.

    python3 tools/merge_plants.py --names            write tools/existing-names.txt
    python3 tools/merge_plants.py batch.json --check  validate only, change nothing
    python3 tools/merge_plants.py batch.json          validate, then merge

The merge appends one GENERATED block to index.html which pushes each record
into SPECIES / LORE / EXTRA / PICTO_OF at load time. The block is rewritten
whole on every run, so re-running with the full set of batches is idempotent
and never double-adds. See tools/plant-data-spec.md for the record format.
"""
import json, re, sys, os

ROOT  = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HTML  = os.path.join(ROOT, "index.html")
BEGIN = "/* ==== GENERATED: added plants — see tools/plant-data-spec.md. Do not edit by hand. ==== */"
END   = "/* ==== END GENERATED ==== */"
ANCHOR = "\n})();\nconst pictoId="

# tags the app derives from the numbers — supplying them is redundant
DERIVED = {"toxic", "safe", "sun", "lowlight", "drought", "thirsty", "humid"}

# a plant with no icon of its own gets its category's, rather than nothing.
# "broadleaf" is the app's own fallback id and is a plain leaf.
# Plain words are the expected input; the indexes are an implementation detail.
LIGHT_WORDS = {
    "full sun": 0, "sun": 0, "direct sun": 0,
    "bright direct": 1, "bright some direct": 1, "bright with some direct": 1,
    "bright indirect": 2, "bright": 2, "indirect": 2, "bright shade": 2,
    "medium": 3, "part shade": 3, "partial shade": 3,
    "low": 4, "shade": 4, "deep shade": 4,
}
HUM_WORDS = {
    "dry": 0, "dry air is fine": 0, "low": 0, "arid": 0,
    "average": 1, "normal": 1, "moderate": 1, "medium": 1,
    "humid": 2, "likes humidity": 2, "high": 2, "very humid": 2,
}

CATEGORY_ICON = {
    "Aroids & foliage":     "oval",
    "Trees & large plants": "ficus",
    "Palms & ferns":        "fern",
    "Succulents & cacti":   "rosette",
    "Herbs & edibles":      "herb",
    "Flowering":            "bloom",
    "Carnivorous":          "pitcher",
}

# ---- the toxicity gate ----
# The one field where a wrong answer hurts something with a pulse, and the one
# the spec cannot enforce by asking nicely: a generator that is confident and
# wrong looks exactly like a generator that is confident and right. So the
# settled cases live here as data, and a batch that contradicts them is
# refused rather than warned about.
#
# Keys are matched case-insensitively against the start of `name` and against
# the whole of it, so "Adiantum" catches "Adiantum raddianum 'Fragrans'" and
# "maidenhair fern" catches the common name. Values are the ASPCA position for
# cats and dogs: 0 non-toxic, 1 toxic.
#
# Only genera whose status is actually settled belong here. A plant absent
# from this table is not thereby cleared — it is simply not covered, and the
# source rule below is what carries it. Add to it as answers get pinned down;
# never add a guess, because everything here becomes unarguable.
TOXICITY = {
    # -- ferns: the classic pet-safe group, and where this gate was earned --
    "adiantum": 0, "maidenhair fern": 0,
    "asplenium": 0, "bird's nest fern": 0, "birds nest fern": 0,
    "nephrolepis": 0, "boston fern": 0,
    "platycerium": 0, "staghorn fern": 0,
    "pteris": 0, "davallia": 0, "rabbit's foot fern": 0,
    "pellaea": 0, "button fern": 0, "blue star fern": 0, "phlebodium": 0,
    # -- palms --
    "chamaedorea": 0, "parlour palm": 0, "parlor palm": 0,
    "howea": 0, "kentia palm": 0,
    "dypsis": 0, "areca palm": 0, "rhapis": 0, "lady palm": 0,
    # -- carnivores: none of the houseplant genera are ASPCA-listed --
    "dionaea": 0, "venus flytrap": 0,
    "nepenthes": 0, "sarracenia": 0, "drosera": 0, "sundew": 0,
    "pinguicula": 0, "butterwort": 0,
    # -- other settled non-toxic --
    "hoya": 0, "echeveria": 0, "haworthia": 0, "gasteria": 0,
    "peperomia": 0, "pilea": 0, "fittonia": 0, "tillandsia": 0,
    "calathea": 0, "goeppertia": 0, "maranta": 0, "ctenanthe": 0,
    "stromanthe": 0, "saintpaulia": 0, "african violet": 0,
    "streptocarpus": 0, "phalaenopsis": 0, "chlorophytum": 0,
    "spider plant": 0, "sempervivum": 0, "lithops": 0,
    # -- settled toxic: the aroids, and the usual suspects --
    "aglaonema": 1, "philodendron": 1, "monstera": 1, "epipremnum": 1,
    "pothos": 1, "scindapsus": 1, "syngonium": 1, "dieffenbachia": 1,
    "alocasia": 1, "colocasia": 1, "caladium": 1, "anthurium": 1,
    "spathiphyllum": 1, "peace lily": 1, "zamioculcas": 1, "zz plant": 1,
    "dracaena": 1, "sansevieria": 1, "snake plant": 1,
    "ficus": 1, "begonia": 1, "tradescantia": 1,
    "aloe": 1, "kalanchoe": 1, "crassula": 1, "jade plant": 1,
    "euphorbia": 1, "cyclamen": 1, "hedera": 1, "schefflera": 1,
    "yucca": 1, "rhaphidophora": 1, "thaumatophyllum": 1, "homalomena": 1,
}


def known_toxicity(name):
    """The settled answer for a plant, or None if this one is not covered.

    Longest key wins, so a species-level entry can override its genus without
    the order of the dict mattering."""
    n = name.lower().strip()
    hit = None
    for key, val in TOXICITY.items():
        if n == key or n.startswith(key + " ") or n.startswith(key + "'") \
           or key in n.split("(")[0].strip():
            if hit is None or len(key) > len(hit[0]):
                hit = (key, val)
    return hit


def read_html():
    with open(HTML, encoding="utf-8") as f:
        return f.read()


def strip_generated(s):
    """The source of truth is the batch files, so drop any previous block first."""
    i, j = s.find(BEGIN), s.find(END)
    if i == -1 or j == -1:
        return s
    return s[:i].rstrip("\n") + "\n" + s[j + len(END):].lstrip("\n")


def slice_between(s, start_pat, end_pat, what):
    i = s.find(start_pat)
    if i == -1:
        sys.exit("could not find %s in index.html" % what)
    j = s.find(end_pat, i)
    if j == -1:
        sys.exit("could not find the end of %s in index.html" % what)
    return s[i:j]


def app_vocab(s):
    """Read the enums out of the app itself, so this stays correct as it changes."""
    species_block = slice_between(s, "const SPECIES=[", "\n];", "the SPECIES list")
    names = re.findall(r'\{n:"((?:[^"\\]|\\.)*)"', species_block)
    cats  = re.findall(r'\{g:"((?:[^"\\]|\\.)*)"', species_block)

    picto_block = slice_between(s, "const PICTO={", "\n};", "the PICTO icon set")
    pictos = re.findall(r"^\s*([A-Za-z][A-Za-z0-9_]*)\s*:\s*'", picto_block, re.M)

    tags_block = slice_between(s, "const TAGS={", "\n};", "the TAGS list")
    tags = re.findall(r"^\s*([a-z]+)\s*:\s*\{", tags_block, re.M)

    return {"names": names, "cats": cats, "pictos": set(pictos),
            "tags": set(tags) - DERIVED}


def norm_word(v):
    """'Bright, indirect' and 'bright indirect' are the same answer."""
    return re.sub(r"[^a-z ]", " ", str(v).lower()).split() and \
           " ".join(re.sub(r"[^a-z ]", " ", str(v).lower()).split()) or ""


def coerce(r):
    """Accept the plain-English form of every field that is stored as a number
       or a triple, so nobody has to write the app's internal encoding."""
    for field, table in (("light", LIGHT_WORDS), ("humidity", HUM_WORDS)):
        v = r.get(field)
        if isinstance(v, str):
            w = norm_word(v)
            if w in table:
                r[field] = table[w]

    for field in ("toxic",):
        v = r.get(field)
        if isinstance(v, bool):
            r[field] = int(v)
        elif isinstance(v, str) and norm_word(v) in ("yes", "true", "toxic"):
            r[field] = 1
        elif isinstance(v, str) and norm_word(v) in ("no", "false", "safe"):
            r[field] = 0

    for field in ("water", "feed"):
        v = r.get(field)
        if isinstance(v, str):
            m = re.findall(r"\d+", v)          # "7-10 days" -> midpoint
            if m:
                r[field] = round(sum(int(x) for x in m) / len(m))

    # one string of exactly three sentences is as good as three strings
    lore = r.get("lore")
    if isinstance(lore, str) and lore.strip():
        parts = [x.strip() for x in re.split(r"(?<=[.!?])\s+", lore.strip()) if x.strip()]
        r["lore"] = parts

    # "2-3 meters" -> "2–3 m", matching the house style of the existing entries
    sz = r.get("size")
    if isinstance(sz, str):
        sz = re.sub(r"\bmet(?:er|re)s?\b", "m", sz, flags=re.I)
        sz = re.sub(r"\bcentimet(?:er|re)s?\b", "cm", sz, flags=re.I)
        sz = re.sub(r"(\d)\s*-\s*(\d)", r"\1–\2", sz)
        r["size"] = sz.strip()
    return r


def check(records, vocab):
    errs, warns = [], []
    seen = {n.lower() for n in vocab["names"]}
    batch = set()

    def bad(i, name, msg):
        errs.append("  [%d] %s: %s" % (i, name or "<no name>", msg))

    for i, r in enumerate(records):
        if not isinstance(r, dict):
            errs.append("  [%d] not a JSON object" % i); continue
        coerce(r)
        name = r.get("name")
        if not isinstance(name, str) or not name.strip():
            bad(i, None, "name missing or not a string"); continue
        name = name.strip()

        key = name.lower()
        if key in seen:      bad(i, name, "duplicates a plant already in the app")
        elif key in batch:   bad(i, name, "duplicated twice inside this batch")
        batch.add(key)

        cat = r.get("category")
        if cat not in vocab["cats"]:
            bad(i, name, "category %r is not one of %s" % (cat, vocab["cats"]))

        for f, lo, hi in (("water", 1, 90), ("feed", 0, 180),
                          ("light", 0, 4), ("humidity", 0, 2), ("toxic", 0, 1)):
            v = r.get(f)
            if isinstance(v, bool) or not isinstance(v, int):
                bad(i, name, "%s must be a number, got %r" % (f, v))
            elif not (lo <= v <= hi):
                bad(i, name, "%s=%d is outside %d–%d" % (f, v, lo, hi))

        # the gate: a settled answer beats whatever the batch says
        tox = r.get("toxic")
        hit = known_toxicity(name)
        if hit and isinstance(tox, int) and not isinstance(tox, bool) and tox != hit[1]:
            bad(i, name, "toxic=%d contradicts the settled answer for %r "
                         "(%s per ASPCA). Fix the record or, if you have a "
                         "source saying otherwise, amend TOXICITY in this script."
                % (tox, hit[0], "toxic" if hit[1] else "non-toxic"))

        tip = r.get("tip")
        if not isinstance(tip, str) or not tip.strip():
            bad(i, name, "tip missing")
        elif len(tip) > 160:
            bad(i, name, "tip is %d chars, keep it under 160" % len(tip))
        elif "!" in tip:
            warns.append("  %s: tip has an exclamation mark — house style has none" % name)

        tags = r.get("tags") or []
        if not isinstance(tags, list):
            bad(i, name, "tags must be an array (use [] or leave it out)")
        else:
            for tg in tags:
                if tg in DERIVED:
                    warns.append("  %s: tag %r is derived from the numbers, dropping it" % (name, tg))
                elif tg not in vocab["tags"]:
                    bad(i, name, "tag %r is not a real tag" % (tg,))

        for f in ("size", "propagation"):
            v = r.get(f)
            if v not in (None, "") and (not isinstance(v, str) or not v.strip()):
                bad(i, name, "%s must be a string if present" % f)

        pic = r.get("picto")
        if pic not in (None, "") and pic not in vocab["pictos"]:
            bad(i, name, "picto %r is not an icon in the app" % (pic,))

        col = r.get("colour", r.get("color"))
        if col not in (None, "") and not isinstance(col, str):
            bad(i, name, "colour must be a string")

        lore = r.get("lore")
        if lore in (None, [], ""):
            pass                      # the app simply omits the about card
        elif not isinstance(lore, list) or len(lore) != 3:
            bad(i, name, "lore came to %d sentences, need exactly 3 (or omit it)"
                % (len(lore) if isinstance(lore, list) else 1))
        else:
            for k, ln in enumerate(lore):
                if not isinstance(ln, str) or not ln.strip():
                    bad(i, name, "lore[%d] is empty" % k)
                elif len(ln) > 260:
                    bad(i, name, "lore[%d] is %d chars, keep it under 260" % (k, len(ln)))
                elif "!" in ln:
                    warns.append("  %s: lore[%d] has an exclamation mark" % (name, k))
    return errs, warns


def js(v):
    """JSON strings are valid JS strings; only </ needs care inside a <script>."""
    return json.dumps(v, ensure_ascii=False).replace("</", "<\\/")


def build_block(records):
    rows = []
    for r in records:
        tags = " ".join(t for t in (r.get("tags") or []) if t not in DERIVED)
        pic  = r.get("picto") or CATEGORY_ICON.get(r["category"], "broadleaf")
        lore = r.get("lore") or []
        rows.append(
            "{n:%s,g:%s,w:%d,f:%d,l:%d,h:%d,x:%d,\n  t:%s,\n  tg:%s,sz:%s,pr:%s,col:%s,pic:%s%s}"
            % (js(r["name"].strip()), js(r["category"]), r["water"], r["feed"],
               r["light"], r["humidity"], r["toxic"], js(r["tip"].strip()),
               js(tags), js((r.get("size") or "").strip()),
               js((r.get("propagation") or "").strip()),
               js((r.get("colour") or r.get("color") or "").strip()), js(pic),
               (",\n  lore:[%s]" % ",\n    ".join(js(x.strip()) for x in lore)) if lore else ""))
    return (
        BEGIN + "\n"
        "/* Generated by tools/merge_plants.py from the batch files in tools/batches/.\n"
        "   Each record is pushed into the same four structures the hand-written\n"
        "   plants live in, so nothing downstream can tell the difference. */\n"
        "(function(){\nconst ADDED=[\n" + ",\n".join(rows) + "\n];\n"
        "ADDED.forEach(r=>{\n"
        "  const g=SPECIES.find(x=>x.g===r.g);\n"
        "  if(!g){ console.warn(\"unknown category\",r.g,r.n); return; }\n"
        "  g.list.push({n:r.n,w:r.w,f:r.f,l:r.l,h:r.h,x:r.x,t:r.t});\n"
        "  if(r.lore) LORE[r.n]=r.lore;\n"
        "  EXTRA[r.n]=[r.tg,r.sz,r.pr,r.col];\n"
        "  PICTO_OF[r.n]=r.pic;\n"
        "});\n})();\n" + END)


def main():
    args = [a for a in sys.argv[1:]]
    html = read_html()

    if "--names" in args:
        vocab = app_vocab(strip_generated(html))
        out = os.path.join(ROOT, "tools", "existing-names.txt")
        with open(out, "w", encoding="utf-8") as f:
            f.write("\n".join(sorted(vocab["names"])) + "\n")
        print("%d existing plant names -> %s" % (len(vocab["names"]), out))
        return

    paths = [a for a in args if not a.startswith("--")]
    if not paths:
        sys.exit(__doc__)

    records = []
    for p in paths:
        with open(p, encoding="utf-8") as f:
            data = json.load(f)
        got = data["plants"] if isinstance(data, dict) else data
        print("%-40s %3d records" % (os.path.basename(p), len(got)))
        records += got

    base = strip_generated(html)
    vocab = app_vocab(base)
    errs, warns = check(records, vocab)

    for w in warns:
        print("warn:" + w)
    if errs:
        print("\n%d problem(s) — nothing was merged:" % len(errs))
        print("\n".join(errs))
        sys.exit(1)

    have = lambda f: sum(1 for r in records if r.get(f))
    print("\n%d records valid.  lore %d · size %d · propagation %d · colour %d · own icon %d"
          % (len(records), have("lore"), have("size"), have("propagation"),
             sum(1 for r in records if r.get("colour") or r.get("color")), have("picto")))
    if "--check" in args:
        return

    if base.count(ANCHOR) != 1:
        sys.exit("the insertion point moved — fix ANCHOR in this script")
    merged = base.replace(ANCHOR, "\n})();\n" + build_block(records) + "\nconst pictoId=", 1)
    with open(HTML, "w", encoding="utf-8") as f:
        f.write(merged)
    print("merged into index.html (library is now %d plants)"
          % (len(vocab["names"]) + len(records)))


if __name__ == "__main__":
    main()
