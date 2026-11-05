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
# từ người học đã biết trước tuần demo (vd. HSK2 vào thẳng tuần 5 đã biết thẻ tuần 1–4 của sheet)
kb_p = os.path.join(D, "known-before.json")
kb = json.load(open(kb_p, encoding="utf-8")) if os.path.exists(kb_p) else None
for wk in weeks:
    if kb and wk >= kb["from_week"]:
        for k, ws in kb.items():
            if isinstance(ws, list):
                for w in ws: known |= set(H(w))
    zh = json.load(open(os.path.join(D, f"zh-w{wk}.json"), encoding="utf-8"))
    en_p = os.path.join(D, f"en-w{wk}.json")
    # tuần demo của một lộ trình riêng (vd. HSK2 tuần 5) không có bản tiếng Anh cùng số tuần
    if not os.path.exists(en_p) and not zh.get("demo"): E(f"tuần {wk}: thiếu bản tiếng Anh en-w{wk}.json (hai ngôn ngữ phải song song)")
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

# ---- tuần demo tiếng Anh (A2, B1): 14 bài, thêm U (spell), W (confuse), V (write) ----
for f in sorted(glob.glob(os.path.join(D, "en-*-*.json"))):
    en = json.load(open(f, encoding="utf-8"))
    tag = os.path.basename(f)
    if not en.get("demo"): continue
    if len(en["days"]) != 5: E(f"{tag}: cần đủ 5 ngày")
    for d in en["days"]:
        did = d["id"]
        if not 10 <= len(d["cards"]) <= 14: E(f"{did}: cần 10–14 thẻ")
        for c in d["cards"]:
            for k in ("w", "ipa", "m", "ex", "exm", "n"):
                if not c.get(k): E(f"{did}: thẻ “{c.get('w')}” thiếu {k}")
            sp = c.get("spell") or []
            if len(sp) != 2 or c["w"] in sp or len(set(sp)) != 2: E(f"{did}: thẻ “{c['w']}” cần đúng 2 cách viết SAI khác nhau (spell)")
        for l in d["scene"]["lines"]:
            if not l.get("vi"): E(f"{did}: câu cảnh “{l['t']}” thiếu vi")
        if not d["scene"].get("img"): E(f"{did}: cảnh thiếu img")
        for p in d["patterns"]:
            if not p.get("ex") or not p.get("bad") or not p.get("good") or not p.get("why"): E(f"{did}: mẫu “{p.get('t')}” thiếu ex/bad/good/why")
        for t in d["dialog"]["turns"]:
            for k in ("ai", "vi", "model", "accept", "frame", "hint"):
                if not t.get(k): E(f"{did}: lượt hội thoại “{t.get('ai','')}” thiếu {k}")
            if t.get("model") not in t.get("accept", []): E(f"{did}: câu mẫu “{t.get('model')}” chưa có trong accept")
        for s_ in d["shadow"]:
            if not s_.get("t") or not s_.get("focus"): E(f"{did}: câu nhại thiếu t/focus")
        r = d.get("reading") or {}
        if not r.get("text") or not r.get("vi") or not r.get("qs"): E(f"{did}: bài đọc thiếu text/vi/qs")
        for sec in ("vocab", "grammar", "listen", "hsk", "reading"):
            items = r.get("qs", []) if sec == "reading" else d.get(sec, [])
            for it in items:
                if it.get("k") == "type":
                    if not it.get("accept") or not it.get("why"): E(f"{did}/{sec}: câu gõ “{it['q'][:30]}” thiếu accept/why")
                    continue
                o = it["opts"]
                if not 2 <= len(o) <= 4 or len(set(o)) != len(o): E(f"{did}/{sec}: “{it['q'][:30]}” cần 2–4 đáp án khác nhau")
                need = {str(i) for i in range(len(o)) if i != it["a"]}
                if set(it.get("why", {})) != need: E(f"{did}/{sec}: “{it['q'][:30]}” phải giải thích đúng từng đáp án sai")
        cf = d.get("confuse") or []
        if len(cf) != 4: E(f"{did}: cần 4 cặp từ dễ nhầm (confuse)")
        for c in cf:
            for k in ("a", "aipa", "am", "b", "bipa", "bm", "note", "qa", "qb"):
                if not c.get(k): E(f"{did}: cặp {c.get('a')}/{c.get('b')} thiếu {k}")
            for q in ("qa", "qb"):
                if c.get(q) and (c[q]["t"].count("___") != 1 or not c[q].get("vi")): E(f"{did}: cặp {c['a']}/{c['b']} câu {q} cần đúng một chỗ ___ và có vi")
        w = d.get("write") or {}
        for k in ("task", "kind", "model", "frame", "gaps", "free", "hints", "check"):
            if not w.get(k): E(f"{did}: bài viết thiếu {k}")
        if w:
            n = len(w["frame"]) if w["kind"] == "form" else w["frame"].count("___")
            if n != len(w["gaps"]) or len(w["free"]) != len(w["gaps"]): E(f"{did}: bài viết có {n} chỗ trống nhưng {len(w['gaps'])} đáp án / {len(w['free'])} cờ free")
            if w["kind"] != "form":
                filled = w["frame"]
                for g in w["gaps"]: filled = filled.replace("___", g, 1)
                if filled != w["model"]: E(f"{did}: điền gaps vào frame không ra đúng bài mẫu")
                nw = len(re.findall(r"[A-Za-z0-9'@.-]+", w["model"]))
                if w.get("words") and not w["words"][0] <= nw <= w["words"][1]: E(f"{did}: bài mẫu có {nw} từ, ngoài khoảng {w['words']}")
            elif [x[0] for x in w["frame"]] != [x[0] for x in w["model"]] or [x[1] for x in w["model"]] != w["gaps"]: E(f"{did}: phiếu mẫu và khung không khớp")
print(f"Kiểm tra {len(weeks)} tuần: {len(errs)} lỗi, {len(warns)} lưu ý")
for e in errs: print("LỖI  ", e)
for w in warns: print("LƯU Ý", w)
sys.exit(1 if errs else 0)
