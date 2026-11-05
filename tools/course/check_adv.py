"""Kiểm tra tuần nâng cao (zh-h4-1, en-b2-1).
  python3 tools/course/check_adv.py tools/course/parts/zh-h4-1/d1.json --day 1   (một ngày, file phần)
  python3 tools/course/check_adv.py tools/course/zh-h4-1.json                    (cả tuần đã ghép)
In LỖI (phải sửa) và LƯU Ý; thoát mã 1 nếu còn lỗi. Xem khung ở tools/course/SCHEMA-ADV.md."""
import json, os, re, sys, glob
D = os.path.dirname(os.path.abspath(__file__)); V = os.path.join(D, "..", "vendor")
H = lambda s: re.findall(r"[一-鿿]", str(s))
errs, warns = [], []
E = errs.append; W = warns.append
plan = json.load(open(os.path.join(D, "plan-adv.json"), encoding="utf-8"))
gloss = json.load(open(os.path.join(V, "zh-gloss.json"), encoding="utf-8"))

def known_base():
    k = set()
    for x in json.load(open(os.path.join(D, "known-hsk3.json"), encoding="utf-8"))["words"]: k |= set(H(x["w"]))
    for f in glob.glob(os.path.join(D, "zh-w*.json")):
        for d in json.load(open(f, encoding="utf-8"))["days"]:
            for c in d["cards"]: k |= set(H(c["w"]))
    kb = json.load(open(os.path.join(D, "known-before.json"), encoding="utf-8"))
    for ws in kb.values():
        if isinstance(ws, list):
            for w in ws: k |= set(H(w))
    return k

def names(extra):
    n = set()
    for g in (gloss, extra):
        for w, v in g.items():
            if len(v) > 2 and re.search(r"\(tên|tên\)", str(v[2])): n |= set(H(w))
    return n

def mc(it, where, L):
    k = it.get("k")
    if k == "type":
        for f in ("q", "model", "accept", "why"):
            if not it.get(f): E(f"{where}: câu gõ thiếu {f}")
        if L == "zh" and it.get("accept") and not any(re.fullmatch(r"[a-z]+", a) for a in it["accept"]): E(f"{where}: câu gõ tiếng Trung cần bính âm không dấu viết liền trong accept")
        return
    if k == "order":
        if not 3 <= len(it.get("tokens", [])) <= 8: E(f"{where}: câu xếp cần 3–8 ô (tokens)")
        if len(set(it.get("tokens", []))) != len(it.get("tokens", [])): E(f"{where}: các ô xếp phải khác nhau")
        for f in ("q", "explain", "vi") + (("en",) if L == "zh" else ()):
            if not it.get(f): E(f"{where}: câu xếp thiếu {f}")
        return
    o = it.get("opts") or []
    if not it.get("q"): E(f"{where}: thiếu q")
    if not 2 <= len(o) <= 4 or len(set(o)) != len(o): E(f"{where}: “{str(it.get('q'))[:30]}” cần 2–4 đáp án khác nhau"); return
    if not isinstance(it.get("a"), int) or not 0 <= it["a"] < len(o): E(f"{where}: chỉ số đáp án a sai"); return
    need = {str(i) for i in range(len(o)) if i != it["a"]}
    if set((it.get("why") or {}).keys()) != need: E(f"{where}: “{str(it['q'])[:30]}” phải giải thích đúng từng đáp án sai (why có khoá {sorted(need)})")
    if L == "zh":
        vi = [x for x in o if not H(x) and re.search(r"[a-zA-ZÀ-ỹ]{2,}", x) and not re.fullmatch(r"[\d:.\s]+", x)]
        if vi and not any(it.get("optsEn") or []): E(f"{where}: “{it['q'][:30]}” có đáp án tiếng Việt nhưng thiếu optsEn")

def zh_texts(d):
    """mọi chuỗi tiếng Trung người học sẽ thấy (không tính nghĩa Việt, Anh)"""
    t = []
    for c in d.get("cards", []): t += [("thẻ", c.get("ex", ""))]
    for l in d.get("scene", {}).get("lines", []): t.append(("cảnh", l.get("t", "")))
    for p in d.get("patterns", []):
        t += [("mẫu câu", x[0]) for x in p.get("ex", [])] + [("mẫu câu", p.get("bad", "")), ("mẫu câu", p.get("good", ""))]
        for row in p.get("f", []): t += [("mẫu câu", x) for x in row]
    for sec in ("vocab", "grammar", "listen", "hsk", "near", "orderPara"):
        for it in d.get(sec, []):
            t += [(sec, it.get("q", "")), (sec, it.get("audio") or ""), (sec, it.get("model", ""))] + [(sec, o) for o in it.get("opts", []) + it.get("tokens", []) + it.get("accept", [])]
            t += [(sec, v) for v in (it.get("why") or {}).values()] if isinstance(it.get("why"), dict) else [(sec, it.get("why", ""))]
    for s in d.get("shadow", []): t.append(("nhại", s.get("t", "")))
    for tu in d.get("dialog", {}).get("turns", []): t += [("hội thoại", tu.get("ai", "")), ("hội thoại", tu.get("model", "")), ("hội thoại", tu.get("frame", "")), ("hội thoại", tu.get("hint", ""))] + [("hội thoại", a) for a in tu.get("accept", [])]
    r = d.get("reading", {}); t.append(("đọc", r.get("text", ""))); t.append(("đọc", r.get("title", "")))
    for q in r.get("qs", []): t += [("câu hỏi đọc", q.get("q", ""))] + [("câu hỏi đọc", o) for o in q.get("opts", [])] + [("câu hỏi đọc", v) for v in (q.get("why") or {}).values()]
    n = d.get("notes", {}); t += [("nghe điền", l.get("t", "")) for l in n.get("lines", [])]
    for f in n.get("form", []): t += [("nghe điền", f.get("label", ""))] + [("nghe điền", o) for o in f.get("opts", [])] + [("nghe điền", f.get("answer", ""))]
    lt = d.get("longturn", {}); t += [("nói dài", lt.get("cue", "")), ("nói dài", lt.get("model", ""))] + [("nói dài", x) for x in lt.get("points", []) + lt.get("useful", [])]
    w = d.get("write", {}); t += [("viết", w.get("model", "")), ("viết", w.get("frame", "")), ("viết", w.get("task", ""))] + [("viết", x) for x in w.get("gaps", []) + w.get("hints", []) + w.get("check", [])]
    return t

def check_day(d, n, wk, L, extra_gloss, known):
    P = plan[wk]["days"][str(n)]; did = d.get("id", f"ngày {n}")
    pre = {"zh": "h4-w1-thu-", "en": "b2-w1-thu-"}[L]
    if d.get("id") != pre + str(n + 1): E(f"{did}: id phải là {pre}{n + 1}")
    ws = [c.get("w") for c in d.get("cards", [])]
    if ws != P["cards"]: E(f"{did}: thẻ từ phải đúng danh sách plan-adv.json theo thứ tự: {P['cards']} (đang có {ws})")
    if d.get("scene", {}).get("img") != P["scene"]: E(f"{did}: scene.img phải là {P['scene']}")
    for k in ("label", "title", "desc", "rule"):
        if not d.get(k): E(f"{did}: thiếu {k}")
    cnt = {"patterns": (3, 3), "vocab": (8, 8), "grammar": (7, 7), "listen": (7, 7), "hsk": (5, 5), "shadow": (6, 6), "near": (6, 6), "orderPara": (4, 4)}
    for k, (a, b) in cnt.items():
        if not a <= len(d.get(k) or []) <= b: E(f"{did}: {k} cần {a} mục (đang có {len(d.get(k) or [])})")
    lines = d.get("scene", {}).get("lines", [])
    if not 8 <= len(lines) <= 10: E(f"{did}: cảnh cần 8–10 câu")
    for l in lines:
        for f in ("who", "t", "vi") + (("py", "en") if L == "zh" else ()):
            if not l.get(f): E(f"{did}: câu cảnh “{l.get('t','')[:20]}” thiếu {f}")
    for c in d.get("cards", []):
        for f in (("w", "py", "m", "mEn", "ex", "expy", "exm", "exEn", "n") if L == "zh" else ("w", "ipa", "m", "ex", "exm", "n")):
            if not c.get(f): E(f"{did}: thẻ “{c.get('w')}” thiếu {f}")
    for p in d.get("patterns", []):
        for f in ("t", "f", "ex", "bad", "good", "why"):
            if not p.get(f): E(f"{did}: mẫu “{p.get('t')}” thiếu {f}")
        for x in p.get("ex", []):
            if L == "zh" and (len(x) < 3 or not x[2]): E(f"{did}: câu mẫu “{x[0]}” cần [chữ Hán, Việt, Anh]")
    for sec in ("vocab", "grammar", "listen", "hsk", "near"):
        for i, it in enumerate(d.get(sec) or []): mc(it, f"{did}/{sec}#{i+1}", L)
    for it in d.get("listen") or []:
        if not it.get("audio"): E(f"{did}/listen: “{it.get('q','')[:30]}” thiếu audio")
    for i, it in enumerate(d.get("orderPara") or []):
        if it.get("k") != "order": E(f"{did}/orderPara#{i+1}: cần k = order")
        mc(it, f"{did}/orderPara#{i+1}", L)
        if not 3 <= len(it.get("tokens", [])) <= 4: E(f"{did}/orderPara#{i+1}: cần 3–4 câu")
    for s in d.get("shadow") or []:
        for f in ("t", "focus") + (("py", "en") if L == "zh" else ()):
            if not s.get(f): E(f"{did}: câu nhại “{s.get('t','')}” thiếu {f}")
    dl = d.get("dialog") or {}
    if not dl.get("title") or not dl.get("partner"): E(f"{did}: hội thoại thiếu title/partner")
    if len(dl.get("turns", [])) != 5: E(f"{did}: hội thoại cần 5 lượt")
    for t in dl.get("turns", []):
        for f in ("ai", "vi", "model", "accept", "frame", "hint") + (("py", "en", "mpy", "men") if L == "zh" else ()):
            if not t.get(f): E(f"{did}: lượt “{t.get('ai','')[:20]}” thiếu {f}")
        if L == "en" and t.get("model") not in t.get("accept", []): E(f"{did}: câu mẫu “{t.get('model','')[:30]}” phải có trong accept")
        if L == "zh" and not any(re.fullmatch(r"[a-z]+", a) for a in t.get("accept", [])): E(f"{did}: lượt “{t.get('ai','')[:20]}” cần bính âm không dấu viết liền trong accept")
    r = d.get("reading") or {}
    for f in ("title", "text", "vi", "qs") + (("py", "en") if L == "zh" else ()):
        if not r.get(f): E(f"{did}: bài đọc thiếu {f}")
    if len(r.get("qs", [])) != 5: E(f"{did}: bài đọc cần 5 câu hỏi")
    for i, q in enumerate(r.get("qs", [])): mc(q, f"{did}/reading#{i+1}", L)
    nt = d.get("notes") or {}
    if not nt.get("title") or not 6 <= len(nt.get("lines", [])) <= 10: E(f"{did}: nghe điền cần title và 6–10 câu")
    for l in nt.get("lines", []):
        for f in ("who", "t", "vi") + (("py", "en") if L == "zh" else ()):
            if not l.get(f): E(f"{did}: câu nghe điền thiếu {f}")
    if not 5 <= len(nt.get("form", [])) <= 6: E(f"{did}: nghe điền cần 5–6 ô")
    script = " ".join(l.get("t", "") for l in nt.get("lines", []))
    for f in nt.get("form", []):
        if not f.get("label"): E(f"{did}: ô nghe điền thiếu label")
        if L == "en":
            if not f.get("answer") or not f.get("accept") or not f.get("why"): E(f"{did}: ô “{f.get('label')}” thiếu answer/accept/why")
            elif len(f["answer"].split()) > 3: E(f"{did}: đáp án “{f['answer']}” dài quá 3 từ")
            elif f["answer"].lower() not in script.lower(): W(f"{did}: đáp án “{f['answer']}” không xuất hiện nguyên văn trong bài nghe (kiểm lại)")
        else:
            mc(dict(f, q=f.get("label", "")), f"{did}/notes", L)
            if f.get("opts") and isinstance(f.get("a"), int) and f["opts"][f["a"]].rstrip("。") not in script: W(f"{did}: đáp án “{f['opts'][f['a']]}” không có nguyên văn trong bài nghe")
    lt = d.get("longturn") or {}
    for f in ("cue", "cueVi", "points", "model", "modelVi", "useful", "check", "prep", "speak") + (("cuePy", "modelPy", "pointsVi") if L == "zh" else ()):
        if not lt.get(f): E(f"{did}: nói dài thiếu {f}")
    if len(lt.get("points", [])) < 3 or len(lt.get("useful", [])) < 5 or len(lt.get("check", [])) < 4: E(f"{did}: nói dài cần ≥3 ý, ≥5 cụm hữu ích, ≥4 mục tự chấm")
    mlen = len(H(lt.get("model", ""))) if L == "zh" else len(re.findall(r"[A-Za-z']+", lt.get("model", "")))
    if lt.get("model") and not ((80 <= mlen <= 140) if L == "zh" else (110 <= mlen <= 200)): E(f"{did}: bài nói mẫu có {mlen} {'chữ' if L == 'zh' else 'từ'} (cần {'80–140 chữ' if L == 'zh' else '110–200 từ'})")
    w = d.get("write") or {}
    for f in ("task", "kind", "model", "frame", "gaps", "free", "hints", "check", "words"):
        if not w.get(f): E(f"{did}: bài viết thiếu {f}")
    if w.get("frame") and w.get("gaps") is not None:
        if w["frame"].count("___") != len(w["gaps"]) or len(w.get("free", [])) != len(w["gaps"]): E(f"{did}: bài viết có {w['frame'].count('___')} chỗ trống nhưng {len(w['gaps'])} đáp án / {len(w.get('free', []))} cờ free")
        filled = w["frame"]
        for g in w["gaps"]: filled = filled.replace("___", g, 1)
        if filled != w.get("model"): E(f"{did}: điền gaps vào frame không ra đúng bài mẫu")
        n_ = len(H(w["model"])) if L == "zh" else len(re.findall(r"[A-Za-z0-9'@.-]+", w["model"]))
        if w.get("words") and not w["words"][0] <= n_ <= w["words"][1]: E(f"{did}: bài viết mẫu có {n_} {'chữ' if L == 'zh' else 'từ'}, ngoài khoảng {w['words']}")
    if L == "zh":
        g2 = dict(gloss); g2.update(extra_gloss)
        for c in d.get("cards", []):
            if c.get("w") not in g2: E(f"{did}: thẻ “{c.get('w')}” chưa có trong gloss (thêm vào khoá gloss của ngày)")
        for w_, v in extra_gloss.items():
            if not (isinstance(v, list) and len(v) == 3 and all(v)): E(f"{did}: gloss “{w_}” cần [bính âm, nghĩa Anh, nghĩa Việt]")
        kn = known | names(extra_gloss)
        for i in range(1, n + 1): kn |= set(H("".join(plan[wk]["days"][str(i)]["cards"])))
        bad = {}
        for where, s in zh_texts(d):
            for ch in H(s):
                if ch not in kn: bad.setdefault(ch, set()).add(where)
        for ch, wh in sorted(bad.items()): E(f"{did}: chữ CHƯA HỌC “{ch}” (ở: {', '.join(sorted(wh))}). Đổi cách nói, hoặc nếu là tên riêng thì thêm vào gloss với nghĩa Việt có '(tên)'")
        for l in lines + d.get("shadow", []):
            if H(l.get("t", "")) and not l.get("py"): E(f"{did}: câu “{l.get('t')}” thiếu bính âm")

def main():
    f = sys.argv[1]; day = int(sys.argv[sys.argv.index("--day") + 1]) if "--day" in sys.argv else None
    x = json.load(open(f, encoding="utf-8"))
    known = known_base()
    if day:
        wk = os.path.basename(os.path.dirname(f)); L = plan[wk]["lang"]
        check_day(x, day, wk, L, x.get("gloss", {}), known)
    else:
        wk = os.path.basename(f)[:-5]; L = x["lang"]
        if len(x.get("days", [])) != 5: E("cần đủ 5 ngày")
        for i, d in enumerate(x.get("days", []), 1): check_day(d, i, wk, L, {}, known)
    print(f"{os.path.basename(f)}: {len(errs)} lỗi, {len(warns)} lưu ý")
    for e in errs: print("LỖI  ", e)
    for w in warns: print("LƯU Ý", w)
    sys.exit(1 if errs else 0)

if __name__ == "__main__":
    main()
