import json, re, sys

def err(m):
    print("ERROR:", m); global bad; bad = True

def mc(it, where, lang):
    if it.get("k") == "type":
        for k in ("q", "model", "accept", "why"):
            if k not in it: err(f"{where}: type item missing {k}")
        if lang == "zh" and isinstance(it.get("accept"), list) and not any(re.fullmatch(r"[a-z]+", a.replace(" ", "")) for a in it["accept"]):
            err(f"{where}: zh type item needs a toneless pinyin accept")
        return
    for k in ("q", "opts", "a", "why"):
        if k not in it: err(f"{where}: MC missing {k}"); return
    if not (2 <= len(it["opts"]) <= 4): err(f"{where}: 2–4 options")
    if not (0 <= it["a"] < len(it["opts"])): err(f"{where}: bad answer index")
    for i in range(len(it["opts"])):
        if i != it["a"] and str(i) not in it["why"]: err(f"{where}: why missing for wrong option {i}")
    if len(set(it["opts"])) != len(it["opts"]): err(f"{where}: duplicate options")

bad = False
f = sys.argv[1]
d = json.load(open(f, encoding="utf-8"))
L = d.get("lang")
if L not in ("zh", "en"): err("lang")
for k in ("week", "title", "cando", "cast", "days"):
    if k not in d: err("missing " + k)
if len(d.get("days", [])) != 5: err("need 5 days")
keyre = re.compile(r"^[a-z0-9-]+$")
for di, day in enumerate(d.get("days", [])):
    w = f"day{di+1}"
    for k in ("id", "label", "title", "desc", "rule", "cards", "scene", "patterns", "vocab", "grammar", "listen", "hsk", "shadow", "dialog"):
        if k not in day: err(f"{w}: missing {k}")
    if day.get("id") != f"w{d.get('week')}-thu-{di+2}": err(f"{w}: id must be w{d.get('week')}-thu-{di+2}")
    for c in day.get("cards", []):
        for k in ("w", "m", "ex", "exm", "n"):
            if not c.get(k): err(f"{w} card {c.get('w')}: missing {k}")
        if L == "zh" and (not c.get("py") or not c.get("expy")): err(f"{w} card {c.get('w')}: py/expy")
        if c.get("img") and not keyre.match(c["img"]): err(f"{w} card img key")
    if not (6 <= len(day.get("cards", [])) <= 16): err(f"{w}: 6–16 cards")
    sc = day.get("scene", {})
    for k in ("setting", "img", "imgPrompt", "lines"):
        if not sc.get(k): err(f"{w} scene missing {k}")
    if sc.get("img") and not keyre.match(sc["img"]): err(f"{w} scene img key")
    for ln in sc.get("lines", []):
        if not ln.get("who") or not ln.get("t") or not ln.get("vi"): err(f"{w} scene line incomplete")
        if L == "zh" and not ln.get("py"): err(f"{w} scene line py")
    for p in day.get("patterns", []):
        for k in ("t", "f", "ex", "bad", "good", "why"):
            if k not in p: err(f"{w} pattern missing {k}")
    for sec in ("vocab", "grammar", "listen", "hsk"):
        for i, it in enumerate(day.get(sec, [])):
            mc(it, f"{w} {sec}[{i}]", L)
            if sec == "listen" and not it.get("audio"): err(f"{w} listen[{i}] needs audio")
            if sec != "grammar" and it.get("k") == "type": err(f"{w} {sec}: only MC allowed")
    for s in day.get("shadow", []):
        if not s.get("t") or not s.get("focus"): err(f"{w} shadow incomplete")
        if L == "zh" and not s.get("py"): err(f"{w} shadow py")
    dg = day.get("dialog", {})
    for k in ("title", "partner", "turns"):
        if not dg.get(k): err(f"{w} dialog missing {k}")
    for t in dg.get("turns", []):
        for k in ("ai", "vi", "model", "accept", "frame"):
            if not t.get(k): err(f"{w} dialog turn missing {k}")
        if L == "zh" and (not t.get("py") or not t.get("mpy")): err(f"{w} dialog turn py/mpy")
    if day.get("reading"):
        for i, it in enumerate(day["reading"].get("qs", [])): mc(it, f"{w} reading[{i}]", L)
for im in d.get("newImages", []):
    if not keyre.match(im.get("key", "")) or not im.get("prompt"): err("newImages entry")
print("FAIL" if bad else "OK")
