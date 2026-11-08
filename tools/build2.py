"""Dựng trang bài tập: python3 tools/build2.py   (chạy ở thư mục gốc repo hoặc bất kỳ đâu)

Đọc:
  tools/build/page-template.html   khuôn trang (giao diện, mã chạy bài); dữ liệu để trống bằng /*@TÊN@*/
  tools/course/zh-wN.json, en-wN.json   các tuần của hành trình chính (cần đủ cặp zh + en)
  tools/course/*.json có "demo": true    tuần học thử của lộ trình khác (zh-w5, en-a2-1, en-b1-1…)
  tools/vendor/stroke-pairs.json, write-guide.json, hzdata/*.json, zh-gloss.json, zhpy.json
Ghi: tuan-1/index.html

Trước khi dựng, chạy tools/course/check_rules.py; còn LỖI thì dừng, không ghi trang.
Thêm --no-check chỉ để thử nhanh trên máy, không dùng khi xuất bản."""
import glob, json, os, re, subprocess, sys

R = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
T = os.path.join(R, "tools")
C, V = os.path.join(T, "course"), os.path.join(T, "vendor")
OUT = os.path.join(R, "tuan-1", "index.html")
J = lambda o: json.dumps(o, ensure_ascii=False, separators=(",", ":"))
load = lambda p: json.load(open(p, encoding="utf-8"))


def main():
    if "--no-check" not in sys.argv:
        r = subprocess.run([sys.executable, os.path.join(C, "check_rules.py")], capture_output=True, text=True)
        print(r.stdout.strip())
        if r.returncode != 0:
            print(r.stderr.strip())
            sys.exit("DỪNG: check_rules.py còn lỗi, chưa dựng trang.")

    # 1. tuần của hành trình chính (zh-wN + en-wN) và tuần học thử
    main_w, demo = {"zh": {}, "en": {}}, {}
    for f in sorted(glob.glob(os.path.join(C, "*.json"))):
        name = os.path.basename(f)[:-5]
        if not re.match(r"^(zh|en)-", name): continue
        d = load(f)
        if "days" not in d: continue
        if d.get("demo"): demo[name] = d
        elif re.match(r"^(zh|en)-w\d+$", name): main_w[d["lang"]][int(d["week"])] = d
    weeks = sorted(set(main_w["zh"]) & set(main_w["en"]))
    lone = sorted(set(main_w["zh"]) ^ set(main_w["en"]))
    if lone: print(f"Lưu ý: tuần {lone} chỉ có một ngôn ngữ, chưa lên hành trình chính.")

    course = ["const COURSE = { en: {}, zh: {} };"]
    for L in ("en", "zh"):
        for w in weeks: course.append(f"COURSE.{L}[{w}] = {J(main_w[L][w])};")
    course.append(f"const COURSE_DEMO = {J(demo)};")

    # 2. dữ liệu bước 4 (chỉ các ngày có trên trang)
    day_ids = [d["id"] for L in ("zh",) for w in weeks for d in main_w[L][w]["days"]]
    day_ids += [d["id"] for k, W in demo.items() if W["lang"] == "zh" for d in W["days"]]
    pairs_all, guide_all = load(os.path.join(V, "stroke-pairs.json")), load(os.path.join(V, "write-guide.json"))
    pairs = {k: pairs_all[k] for k in day_ids if k in pairs_all}
    guide = {k: guide_all[k] for k in day_ids if k in guide_all}
    chars = []
    for ps in pairs.values():
        for p in ps: chars += [p["a"], p["b"]]
    for gs in guide.values():
        for g in gs: chars.append(g["ch"])
    hz, missing = {}, []
    for ch in dict.fromkeys(chars):
        p = os.path.join(V, "hzdata", ch + ".json")
        if not os.path.exists(p): missing.append(ch); continue
        x = load(p); hz[ch] = {"strokes": x["strokes"], "medians": x["medians"], "radStrokes": x.get("radStrokes")}
    if missing: sys.exit(f"DỪNG: thiếu dữ liệu nét chữ trong tools/vendor/hzdata/: {''.join(missing)}")

    gloss, zhpy = load(os.path.join(V, "zh-gloss.json")), load(os.path.join(V, "zhpy.json"))
    gx = os.path.join(V, "zh-gloss-hsk3.json")   # nghĩa Anh, Việt cho 600 từ HSK1–3 (tra từ ở tuần nâng cao)
    if os.path.exists(gx):
        for k, v in load(gx).items(): gloss.setdefault(k, v)
    site = {k: v for k, v in load(os.path.join(T, "site.json")).items() if not k.startswith("_")}
    funnel = open(os.path.join(T, "build", "funnel.js"), encoding="utf-8").read()
    adv = open(os.path.join(T, "build", "adv.js"), encoding="utf-8").read()

    # ngân hàng câu kiểm tra đầu vào: id cố định, 4 lựa chọn, đáp án đúng đứng đầu, mỗi mức ≥16 câu, mỗi kỹ năng ≥4 câu, câu nghe có giọng Gemini
    place = load(os.path.join(T, "course", "placement.json")); aud = load(os.path.join(R, "tuan-1", "audio", "index.json"))
    for L, lvs in (("zh", range(0, 5)), ("en", range(1, 5))):
        for q in place[L]:
            if len(q["opts"]) != 4 or len(set(q["opts"])) != 4: sys.exit(f"DỪNG: câu kiểm tra đầu vào cần 4 lựa chọn khác nhau: {q['q']}")
            if q.get("audio") and q["audio"] not in aud.get(L, {}): sys.exit(f"DỪNG: câu nghe kiểm tra đầu vào chưa có giọng Gemini: {q['audio']}")
        ids = [q.get("id") for q in place[L]]
        if None in ids or len(set(ids)) != len(ids): sys.exit(f"DỪNG: câu kiểm tra đầu vào {L} thiếu id hoặc trùng id")
        for lv in lvs:
            n = sum(q["lv"] == lv for q in place[L]); sk = {}
            for q in place[L]:
                if q["lv"] == lv: sk[q["sk"]] = sk.get(q["sk"], 0) + 1
            if n < 16 or min(sk.values()) < 4 or sk.get("Nghe", 0) < 4: sys.exit(f"DỪNG: kiểm tra đầu vào {L} mức {lv} cần ≥16 câu, mỗi kỹ năng ≥4 câu (có Nghe): đang có {sk}")
    place = {L: [dict(q, a=0) for q in place[L]] for L in ("zh", "en")}

    # 3. ghép vào khuôn
    s = open(os.path.join(T, "build", "page-template.html"), encoding="utf-8").read()
    fill = {
        "/*@COURSE@*/\n": "\n".join(course) + "\n",
        "/*@HZDATA@*/": J(hz),
        "/*@STROKE_PAIRS@*/": json.dumps(pairs, ensure_ascii=False, indent=1),
        "/*@WRITE_GUIDE@*/": json.dumps(guide, ensure_ascii=False, indent=1),
        "/*@ZHGLOSSDATA@*/": json.dumps(gloss, ensure_ascii=False),
        "/*@ZHPYDATA@*/": J(zhpy),
        "/*@SITE@*/": J(site),
        "/*@FUNNEL@*/": adv + "\n" + funnel,
        "/*@PLACEMENT@*/": json.dumps(place, ensure_ascii=False, indent=1),
    }
    for k, v in fill.items():
        if s.count(k) != 1: sys.exit(f"DỪNG: khuôn trang thiếu chỗ điền {k.strip()}")
        s = s.replace(k, v)
    if "/*@" in s: sys.exit("DỪNG: còn chỗ điền chưa có dữ liệu: " + re.search(r"/\*@\w+@\*/", s).group(0))
    open(OUT, "w", encoding="utf-8").write(s)
    sync_landing(site)
    nd = sum(len(main_w["zh"][w]["days"]) for w in weeks)
    print(f"Đã dựng tuan-1/index.html ({len(s.encode('utf-8')) // 1024} KB): tuần {weeks} ({nd} ngày × 2 ngôn ngữ), "
          f"học thử {', '.join(f'{k} ({len(W['days'])} ngày)' for k, W in demo.items())}, {len(hz)} chữ có dữ liệu nét.")


def sync_landing(site):
    """Trang chủ (index.html) dùng chung cấu hình: địa chỉ nhận form, Zalo, ngân hàng, giá."""
    p = os.path.join(R, "index.html"); h = open(p, encoding="utf-8").read(); h0 = h
    q = lambda v: json.dumps(v, ensure_ascii=False)
    h = re.sub(r'formEndpoint: "[^"]*"', "formEndpoint: " + q(site.get("sheetUrl", "")), h, count=1)
    h = re.sub(r'(\n  zalo: )"[^"]*"', lambda m: m.group(1) + q(site.get("zalo", "")), h, count=1)
    h = re.sub(r'(\n  zaloUrl: )"[^"]*"', lambda m: m.group(1) + q(site.get("zaloUrl", "")), h, count=1)
    h = re.sub(r'(\n  hotline: )"[^"]*"', lambda m: m.group(1) + q(site.get("hotline", "")), h, count=1)
    b = site.get("bank", {})
    h = re.sub(r'bank: \{ id: "[^"]*", account: "[^"]*", name: "[^"]*" \}', f'bank: {{ id: {q(b.get("id", ""))}, account: {q(b.get("account", ""))}, name: {q(b.get("name", ""))} }}', h, count=1)
    P = site["prices"]
    for k in ("online", "member", "vip"):
        h = re.sub(r"(\b" + k + r": \{ month: )\d+,(\s+)term: \d+", lambda m: f"{m.group(1)}{P[k]['month']},{m.group(2)}term: {P[k]['term']}", h, count=1)
    h = re.sub(r"(\n    ticket: )\d+", lambda m: m.group(1) + str(P["ticket"]), h, count=1)
    tr = site.get("trial", {})
    note = f' · học thử lần đầu {tr["live"]:,}đ'.replace(",", ".") if tr.get("live") else ""
    h = re.sub(r'(<span data-price="ticket">[^<]*</span>/buổi, gồm đồ uống)(<span class="trialnote">[^<]*</span>)?', lambda m: m.group(1) + (f'<span class="trialnote">{note}</span>' if note else ""), h, count=1)
    if h != h0: open(p, "w", encoding="utf-8").write(h); print("Đã cập nhật trang chủ theo tools/site.json.")


if __name__ == "__main__":
    main()
