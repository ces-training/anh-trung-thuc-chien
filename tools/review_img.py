"""Trang duyệt tranh: liệt kê mọi chỗ trên web đang mượn ảnh, dùng hình vẽ hoặc còn trống.
Chạy: python3 tools/review_img.py [đường_dẫn_ra.html]   (mặc định tools/shots/duyet-tranh.html)
Không gọi Gemini, không tốn tiền. Hình vẽ lấy thẳng từ tools/build/page-template.html."""
import base64, glob, hashlib, io, json, os, re, subprocess, sys, tempfile
from PIL import Image

R = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
TPL = open(os.path.join(R, "tools", "build", "page-template.html"), encoding="utf-8").read()
IMGDIR = os.path.join(R, "tuan-1", "img")
PHOTOS = {os.path.splitext(f)[0]: f for f in os.listdir(IMGDIR) if f.endswith(".webp")}
NEW = set(open(os.path.join(R, "tools", "image-new.txt")).read().split()) if os.path.exists(os.path.join(R, "tools", "image-new.txt")) else set()
QA = json.load(open(os.path.join(R, "tools", "image-qa.json"), encoding="utf-8")) if os.path.exists(os.path.join(R, "tools", "image-qa.json")) else {}
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(R, "tools", "shots", "duyet-tranh.html")
NEW_ICONS = set(re.findall(r'^\s+"?([a-z][\w-]*)"?: \[', TPL[TPL.find("/* hình vẽ bằng mã cho các thẻ chưa có tranh"):TPL.find("/* dùng lại ảnh thật")], re.M))
DAYN = ["Thứ 2", "Thứ 3", "Thứ 4", "Thứ 5", "Thứ 6"]
WEEK_NAME = {"zh-w1": "Trung · Tuần 1", "zh-w2": "Trung · Tuần 2", "zh-w5": "Trung · học thử HSK2", "zh-h4-1": "Trung · nâng cao HSK4",
             "en-w1": "Anh · Tuần 1", "en-w2": "Anh · Tuần 2", "en-a2-1": "Anh · học thử A2", "en-b1-1": "Anh · học thử B1", "en-b2-1": "Anh · nâng cao B2"}

# --- chạy phần vẽ của trang trong node để lấy đúng hình học viên đang thấy ---
a = TPL.find("const AC_ ="); b = TPL.find("function cardArt(c)")
js = TPL[a:b] + "\nmodule.exports = { ICONS, IMG_ALIAS, CHARS, personSVG, charKey };\n"
tmp = tempfile.mkdtemp()
open(os.path.join(tmp, "art.js"), "w", encoding="utf-8").write(js)

def thumb(name, w=320):
    im = Image.open(os.path.join(IMGDIR, PHOTOS[name])).convert("RGB"); im.thumbnail((w, w))
    buf = io.BytesIO(); im.save(buf, "WEBP", quality=72)
    return "data:image/webp;base64," + base64.b64encode(buf.getvalue()).decode()

slots, need_icons, need_people = {}, set(), set()
def slot(sid, **kw):
    s = slots.setdefault(sid, {"id": sid, "uses": [], **{k: v for k, v in kw.items() if k != "use"}})
    if kw.get("use") and kw["use"] not in s["uses"]: s["uses"].append(kw["use"])
    for k in ("prompt",):
        if kw.get(k) and not s.get(k): s[k] = kw[k]
    return s

known_char = {"an", "tom", "kevin", "linh", "sarah", "wangli", "minh", "wangjl"}
for f in sorted(glob.glob(os.path.join(R, "tools", "course", "*.json"))):
    name = os.path.basename(f)[:-5]
    if name not in WEEK_NAME: continue
    W = json.load(open(f, encoding="utf-8")); wk = WEEK_NAME[name]
    prompts = {x["key"]: x.get("prompt", "") for x in (W.get("newImages") or []) + (W.get("newScenes") or [])}
    for c in W.get("cast", []):
        if c["key"] in known_char: continue
        ck = c.get("img") or "cast-" + c["key"]
        if ck in PHOTOS and ck not in NEW: continue
        s = slot("char-" + c["key"] + "-" + c["name"], group="char", key=c["name"], photo=ck if ck in PHOTOS else "", title=c["name"] + (f" ({c['py']})" if c.get("py") else ""),
                 sub=c.get("vi", ""), prompt=c.get("look", ""), use=wk)
        need_people.add(c["name"])
    for i, d in enumerate(W["days"]):
        where = f"{wk} · {DAYN[i] if i < 5 else d.get('label', '')}"
        sc = (d.get("scene") or {}).get("img")
        if sc and (sc not in PHOTOS or sc in NEW):
            slot(sc, group="scene", key=sc, title=d.get("title") or sc, sub="Tranh cảnh mở đầu (khung 16:9, dùng làm khung đầu cho phim)", prompt=prompts.get(sc, ""), use=where)
        for c in d.get("cards", []):
            k = c.get("img")
            if not k or (k in PHOTOS and k not in NEW): continue
            word = c["w"] + (f" ({c['py']})" if c.get("py") else "")
            s = slot(k, group="card", key=k, title=k, sub="", prompt=prompts.get(k, ""), use=f"{where} · {word} = {c.get('mEn') or ''} / {c.get('m') or ''}".replace(" =  / ", ""))
            need_icons.add(k)

# --- vẽ hình bằng node ---
q = {"icons": sorted(need_icons), "people": sorted(need_people)}
node = f"""const m=require({json.dumps(os.path.join(tmp, 'art.js'))});const q={json.dumps(q, ensure_ascii=False)};
const out={{icons:{{}},people:{{}},alias:m.IMG_ALIAS}};
for(const k of q.icons){{const ic=m.ICONS[k];if(ic)out.icons[k]=`<svg viewBox="0 0 160 120" xmlns="http://www.w3.org/2000/svg"><rect x="6" y="4" width="148" height="112" rx="28" fill="${{ic[0]}}"/>${{ic[1]}}</svg>`;}}
for(const n of q.people){{const c=m.CHARS[m.charKey(n)];out.people[n]={{svg:`<svg viewBox="0 0 120 140" xmlns="http://www.w3.org/2000/svg">${{m.personSVG(c,false)}}</svg>`,own:m.charKey(n)===n}};}}
console.log(JSON.stringify(out));"""
art = json.loads(subprocess.check_output(["node", "-e", node], text=True))
ALIAS = art["alias"]

for s in slots.values():
    k = s["key"]; s["doc"] = re.sub(r"[^A-Za-z0-9_-]", "", s["id"])[:40] + "-" + hashlib.md5(s["id"].encode()).hexdigest()[:6]
    if s.get("photo") or (s["group"] != "char" and k in PHOTOS):
        ph = s.get("photo") or k; q = QA.get(ph, {})
        s["now"] = {"type": "new", "photo": ph, "label": "Tranh mới vẽ" + ("" if q.get("ok", True) else " · máy báo cần xem")}
    elif s["group"] == "char":
        p = art["people"].get(k, {})
        s["now"] = {"type": "drawn", "svg": p.get("svg", ""), "label": "Hình vẽ theo mô tả nhân vật" if p.get("own") else "Hình vẽ chung (chưa có mô tả riêng)"}
    elif ALIAS.get(k) in PHOTOS:
        s["now"] = {"type": "alias", "photo": ALIAS[k], "label": f"Mượn ảnh “{ALIAS[k]}”"}
    elif k in art["icons"]:
        s["now"] = {"type": "icon", "svg": art["icons"][k], "label": "Hình vẽ mới hôm nay" if k in NEW_ICONS else "Hình vẽ có sẵn", "fresh": k in NEW_ICONS}
    else:
        s["now"] = {"type": "none", "label": "Đang trống"}

order = {"char": 0, "scene": 1, "card": 2}
items = sorted(slots.values(), key=lambda s: (order[s["group"]], s["uses"][0] if s["uses"] else "", s["key"]))
photos = {n: thumb(n) for n in sorted(PHOTOS) if not n.startswith(("coach-", "room-"))}
data = {"items": items, "photos": photos, "built": __import__("datetime").datetime.now().strftime("%d/%m/%Y %H:%M")}
page = open(os.path.join(R, "tools", "build", "review-template.html"), encoding="utf-8").read()
os.makedirs(os.path.dirname(OUT), exist_ok=True)
open(OUT, "w", encoding="utf-8").write(page.replace("/*__DATA__*/null", json.dumps(data, ensure_ascii=False)))
cnt = {}
for s in items: cnt[(s["group"], s["now"]["type"])] = cnt.get((s["group"], s["now"]["type"]), 0) + 1
print(OUT, f"{os.path.getsize(OUT) // 1024} KB", len(items), "mục", cnt)
