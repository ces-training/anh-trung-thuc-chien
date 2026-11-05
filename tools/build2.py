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

    # 3. ghép vào khuôn
    s = open(os.path.join(T, "build", "page-template.html"), encoding="utf-8").read()
    fill = {
        "/*@COURSE@*/\n": "\n".join(course) + "\n",
        "/*@HZDATA@*/": J(hz),
        "/*@STROKE_PAIRS@*/": json.dumps(pairs, ensure_ascii=False, indent=1),
        "/*@WRITE_GUIDE@*/": json.dumps(guide, ensure_ascii=False, indent=1),
        "/*@ZHGLOSSDATA@*/": json.dumps(gloss, ensure_ascii=False),
        "/*@ZHPYDATA@*/": J(zhpy),
    }
    for k, v in fill.items():
        if s.count(k) != 1: sys.exit(f"DỪNG: khuôn trang thiếu chỗ điền {k.strip()}")
        s = s.replace(k, v)
    if "/*@" in s: sys.exit("DỪNG: còn chỗ điền chưa có dữ liệu: " + re.search(r"/\*@\w+@\*/", s).group(0))
    open(OUT, "w", encoding="utf-8").write(s)
    nd = sum(len(main_w["zh"][w]["days"]) for w in weeks)
    print(f"Đã dựng tuan-1/index.html ({len(s.encode('utf-8')) // 1024} KB): tuần {weeks} ({nd} ngày × 2 ngôn ngữ), "
          f"học thử {', '.join(f'{k} ({len(W['days'])} ngày)' for k, W in demo.items())}, {len(hz)} chữ có dữ liệu nét.")


if __name__ == "__main__":
    main()
