"""Kiểm tra QUY TẮC TẠO BÀI cho cả khoá (chạy trước khi dựng trang): python3 course/check_rules.py
Dừng (exit 1) nếu có lỗi chặn. Xem quy tắc đầy đủ trong tài liệu "Quy tắc tạo bài tập" của Project."""
import json, re, sys, glob, os
D = os.path.dirname(os.path.abspath(__file__)); V = os.path.join(D, "..", "vendor")
H = lambda s: re.findall(r"[一-鿿]", str(s))
errs, warns = [], []
E = errs.append; W = warns.append
weeks = sorted(int(re.search(r"zh-w(\d+)", f).group(1)) for f in glob.glob(os.path.join(D, "zh-w*.json")))
gloss = json.load(open(os.path.join(V, "zh-gloss.json"), encoding="utf-8"))
pairs = json.load(open(os.path.join(V, "stroke-pairs.json"), encoding="utf-8"))
guide = json.load(open(os.path.join(V, "write-guide.json"), encoding="utf-8"))
hzdir = os.path.join(V, "hzdata")
def strokes(c):
    p = os.path.join(hzdir, c + ".json")
    return len(json.load(open(p, encoding="utf-8"))["strokes"]) if os.path.exists(p) else None
NAMES = set()
for w in gloss:
    if re.search(r"\(tên|tên\)|giám đốc|cô giáo", gloss[w][2]): NAMES |= set(H(w))
known = set()
for wk in weeks:
    zh = json.load(open(os.path.join(D, f"zh-w{wk}.json"), encoding="utf-8"))
    en_p = os.path.join(D, f"en-w{wk}.json")
    if not os.path.exists(en_p): E(f"tuần {wk}: thiếu bản tiếng Anh en-w{wk}.json (hai ngôn ngữ phải song song)")
    for d in zh["days"]:
        did = d["id"]
        for c in d["cards"]: known |= set(H(c["w"]))
        # 1. bài đọc chỉ dùng chữ đã học
        r = d.get("reading")
        if not r: W(f"{did}: chưa có bài đọc")
        else:
            un = [c for c in dict.fromkeys(H(r["text"])) if c not in known | NAMES]
            if un: E(f"{did}: bài đọc có chữ CHƯA HỌC: {''.join(un)} (chỉ dùng chữ trong thẻ từ đến hôm nay, hoặc thêm vào tên riêng trong từ điển)")
            for q in r.get("qs", []):
                uq = [c for c in dict.fromkeys(H(q["q"] + "".join(q.get("opts", [])))) if c not in known | NAMES]
                if uq: E(f"{did}: câu hỏi đọc có chữ chưa học: {''.join(uq)}")
            if not r.get("py") or not r.get("vi"): E(f"{did}: bài đọc thiếu bính âm hoặc bản dịch")
        # 2. từ điển rê chuột: mọi thẻ từ phải có pinyin + Anh + Việt
        for c in d["cards"]:
            for w in re.split(r"\s*/\s*|\s+", c["w"]):
                if w and H(w) and w not in gloss and not all(ch in gloss for ch in w): W(f"{did}: từ “{w}” chưa có trong từ điển tra nhanh (vendor/zh-gloss.json)")
        # 3. hội thoại đủ trường để nghe, gợi ý, đổi vai
        for t in d["dialog"]["turns"]:
            for k in ("ai", "py", "vi", "model", "mpy", "accept", "hint"):
                if not t.get(k): E(f"{did}: lượt hội thoại “{t.get('ai','')}” thiếu {k}")
        # 4. nhại theo có bính âm và dòng Chú ý
        for s in d.get("shadow", []):
            if not s.get("py") or not s.get("focus"): E(f"{did}: câu nhại “{s.get('t')}” thiếu py/focus")
        # 5. mẫu câu đủ 3 bước: câu mẫu, câu sai, câu đúng, giải thích
        for p in d["patterns"]:
            if not p.get("ex") or not p.get("bad") or not p.get("good") or not p.get("why"): E(f"{did}: mẫu “{p.get('t')}” thiếu ex/bad/good/why")
        # 6. cảnh có ảnh để làm tranh nền cho câu hỏi
        if not d["scene"].get("img"): E(f"{did}: cảnh thiếu img (tranh nền cho câu hỏi)")
        # 7. bước 4: cặp chữ khác số nét; hướng dẫn viết đủ cách nhớ + quy tắc
        ps = pairs.get(did) or []
        if len(ps) < 4: E(f"{did}: cần 4 cặp chữ đếm nét")
        for p in ps:
            na, nb = strokes(p["a"]), strokes(p["b"])
            if na is None or nb is None: E(f"{did}: thiếu dữ liệu nét cho {p['a']}/{p['b']}")
            elif na == nb: E(f"{did}: cặp {p['a']}/{p['b']} cùng {na} nét — phải khác số nét")
            if p["a"] not in known: E(f"{did}: chữ {p['a']} (cặp đếm nét) chưa học")
        gs = guide.get(did) or []
        if len(gs) < 4: E(f"{did}: cần 4 chữ hướng dẫn viết")
        for g in gs:
            if g["ch"] not in known: E(f"{did}: chữ viết {g['ch']} chưa học")
            if not g.get("k") or len(g.get("r", [])) < 2: E(f"{did}: chữ viết {g['ch']} thiếu cách nhớ/quy tắc")
            if strokes(g["ch"]) is None: E(f"{did}: thiếu dữ liệu nét cho {g['ch']}")
        # 8. nghĩa song ngữ: mọi chỗ có nghĩa tiếng Việt phải có nghĩa tiếng Anh (hiện tiếng Anh trước)
        for c in d["cards"]:
            if not c.get("mEn"): E(f"{did}: thẻ “{c['w']}” thiếu mEn (nghĩa tiếng Anh)")
            if c.get("exm") and not c.get("exEn"): E(f"{did}: câu ví dụ của “{c['w']}” thiếu exEn")
        for l in d["scene"]["lines"]:
            if l.get("vi") and not l.get("en"): E(f"{did}: câu cảnh “{l['t']}” thiếu en")
        for t in d["dialog"]["turns"]:
            if not t.get("en") or not t.get("men"): E(f"{did}: lượt hội thoại “{t['ai']}” thiếu en/men")
        for p in d["patterns"]:
            for x in p.get("ex", []):
                if len(x) < 3 or not x[2]: E(f"{did}: câu mẫu “{x[0]}” thiếu nghĩa tiếng Anh (phần tử thứ 3)")
        if r and not r.get("en"): E(f"{did}: bài đọc thiếu en")
        VIOPT = lambda o: not H(o) and len(o.strip()) > 3 and re.search(r"[a-zA-ZÀ-ỹ]{2,}", o) and not re.fullmatch(r"[\d:.\s]+", o)
        for sec in ("vocab", "listen", "hsk", "grammar") + (("reading",) if r else ()):
            items = d[sec]["qs"] if sec == "reading" else d.get(sec, [])
            for it in items:
                if it.get("k") == "type" or not it.get("opts"): continue
                if any(VIOPT(o) for o in it["opts"]) and not any(it.get("optsEn") or []): E(f"{did}/{sec}: câu “{it['q'][:30]}” có đáp án tiếng Việt nhưng thiếu optsEn")
        for p in ps:
            if not p.get("aen") or not p.get("ben"): E(f"{did}: cặp đếm nét {p['a']}/{p['b']} thiếu aen/ben")
        for g in gs:
            if not g.get("en"): E(f"{did}: chữ viết {g['ch']} thiếu en")
print(f"Kiểm tra {len(weeks)} tuần: {len(errs)} lỗi, {len(warns)} lưu ý")
for e in errs: print("LỖI  ", e)
for w in warns: print("LƯU Ý", w)
sys.exit(1 if errs else 0)
