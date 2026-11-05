"""Thống kê giọng đọc và tranh còn thiếu cho mọi tuần trên web (chạy: python3 tools/media_need.py [--json out.json])."""
import glob, json, os, re, sys
R = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
C = os.path.join(R, "tools", "course")
AUD = json.load(open(os.path.join(R, "tuan-1", "audio", "index.json"), encoding="utf-8"))
IMG = {os.path.splitext(f)[0] for f in os.listdir(os.path.join(R, "tuan-1", "img"))}
LISTED = {x["key"]: x for x in json.load(open(os.path.join(R, "tools", "image-list.json"), encoding="utf-8"))}
tpl = open(os.path.join(R, "tools", "build", "page-template.html"), encoding="utf-8").read()
_a = tpl.find("const IMG_ALIAS")
ALIAS = dict(re.findall(r'"?([\w-]+)"?:\s*"([\w-]+)"', tpl[_a:tpl.find("};", _a)]))
HAN = re.compile(r"[一-鿿]")

def week_files():
    for f in sorted(glob.glob(os.path.join(C, "*.json"))):
        n = os.path.basename(f)[:-5]
        if re.match(r"^(zh|en)-(w\d+|[a-z]\d-\d)$", n): yield n, json.load(open(f, encoding="utf-8"))

def clips(W):
    L = W["lang"]; out = []
    def add(t, who="_", kind=""):
        if isinstance(t, str) and t.strip(): out.append((L, who or "_", t.strip(), kind))
    for d in W["days"]:
        for c in d.get("cards", []): add(c.get("w"), kind="thẻ từ"); add(c.get("ex"), kind="câu ví dụ")
        for l in d.get("scene", {}).get("lines", []): add(l.get("t"), l.get("who"), "cảnh mở đầu")
        for p in d.get("patterns", []):
            for x in p.get("ex", []): add(x[0], kind="mẫu câu")
            add(p.get("good"), kind="mẫu câu")
        for k in ("listen", "hsk", "vocab", "grammar", "near", "orderPara"):
            for it in d.get(k, []) or []:
                add(it.get("audio"), kind="câu nghe"); add(it.get("hearAfter"), kind="câu nghe")
                if it.get("k") in ("type", "order") and it.get("model"): add(it.get("model"), kind="đáp án mẫu")
        for x in d.get("shadow", []): add(x.get("t"), kind="nhại theo")
        dl = d.get("dialog", {})
        for t in dl.get("turns", []): add(t.get("ai"), dl.get("partner"), "hội thoại"); add(t.get("model"), kind="hội thoại")
        add(d.get("reading", {}).get("text"), kind="bài đọc")
        for l in (d.get("notes") or {}).get("lines", []): add(l.get("t"), l.get("who"), "nghe điền")
        add((d.get("longturn") or {}).get("model"), kind="nói dài")
        for c in d.get("confuse", []) or []:
            add(c.get("a"), kind="từ dễ nhầm"); add(c.get("b"), kind="từ dễ nhầm")
            for q in ("qa", "qb"): add((c.get(q) or {}).get("t"), kind="từ dễ nhầm")
    return out

def secs(L, t):
    return max(1.0, len(HAN.findall(t)) / 3.5 + 0.6) if L == "zh" else max(1.0, len(t.split()) / 2.4 + 0.6)

def has_audio(L, who, t):
    m = AUD.get(L, {}).get(t)
    return bool(m and (who in m or "_" in m))

def imgs(W):
    keys = set()
    for d in W["days"]:
        for c in d.get("cards", []):
            if c.get("img"): keys.add(c["img"])
        if d.get("scene", {}).get("img"): keys.add(d["scene"]["img"])
    for x in W.get("newImages", []) or []: keys.add(x["key"])
    return keys

rows, seen, need_img = [], set(), {}
for name, W in week_files():
    cs = clips(W); new = []
    for L, who, t, kind in cs:
        k = (L, who, t)
        if k in seen: continue
        seen.add(k); new.append((L, who, t, kind))
    miss = [x for x in new if not has_audio(x[0], x[1], x[2])]
    ik = imgs(W)
    real = {k for k in ik if k in IMG}
    alias = {k for k in ik - real if ALIAS.get(k) in IMG}
    missing = sorted(ik - real - alias)
    rows.append({"week": name, "level": W.get("level", ""), "clips": len(new), "missing": len(miss), "secs": round(sum(secs(L, t) for L, _, t, _ in miss)),
                 "chars": sum(len(t) for _, _, t, _ in miss), "img_total": len(ik), "img_real": len(real), "img_alias": len(alias), "img_missing": missing,
                 "byKind": {k: sum(1 for x in miss if x[3] == k) for k in sorted({x[3] for x in miss})}})
coach = json.load(open(os.path.join(R, "tools", "audio-list.json"), encoding="utf-8"))
coach_miss = [r for r in coach if not has_audio(r["lang"], r["who"] or "_", r["text"])]
res = {"weeks": rows, "coach_missing": len(coach_miss), "img_have": len(IMG), "aliases_used": sum(r["img_alias"] for r in rows)}
if "--json" in sys.argv: json.dump(res, open(sys.argv[sys.argv.index("--json") + 1], "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(f"{'Tuần':10} {'câu':>5} {'thiếu':>6} {'giây':>6} {'tranh':>6} {'có':>4} {'mượn':>5} {'thiếu':>6}")
for r in rows: print(f"{r['week']:10} {r['clips']:5} {r['missing']:6} {r['secs']:6} {r['img_total']:6} {r['img_real']:4} {r['img_alias']:5} {len(r['img_missing']):6}")
print("Lời người hướng dẫn chưa có giọng:", len(coach_miss))
print("Tổng câu thiếu:", sum(r["missing"] for r in rows), "· tổng giây:", sum(r["secs"] for r in rows))
