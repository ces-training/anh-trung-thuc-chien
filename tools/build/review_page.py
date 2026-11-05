"""Tạo trang duyệt nội dung một tuần (để chị Duyên đọc, góp ý): python3 tools/build/review_page.py zh-h4-1 out.html"""
import html, json, os, sys
R = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
wk, out = sys.argv[1], sys.argv[2]
W = json.load(open(os.path.join(R, "tools", "course", wk + ".json"), encoding="utf-8"))
zh = W["lang"] == "zh"
e = lambda s: html.escape(str(s or ""))
def zt(t, py=""):
    return f'<span class="t" lang="{"zh" if zh else "en"}">{e(t)}</span>' + (f'<span class="py">{e(py)}</span>' if py else "")
def mcs(items, title):
    if not items: return ""
    rows = []
    for i, it in enumerate(items, 1):
        if it.get("k") == "type":
            rows.append(f'<li><p>{e(it["q"])}</p><p class="ok">✓ {e(it["model"])}</p><p class="why">{e(it.get("why"))}</p></li>'); continue
        if it.get("k") == "order":
            rows.append(f'<li><p>{e(it["q"])}</p><ol class="ord">{"".join(f"<li>{zt(t)}</li>" for t in it["tokens"])}</ol><p class="why">{e(it.get("explain"))}</p><p class="vi">{e(it.get("vi"))}</p></li>'); continue
        au = f'<p class="au">🔊 {e(it["audio"])}</p>' if it.get("audio") else ""
        ops = "".join(f'<li class="{"ok" if j == it["a"] else ""}">{e(o)}{" · " + e(it["optsEn"][j]) if it.get("optsEn") and j < len(it["optsEn"]) and it["optsEn"][j] else ""}{"" if j == it["a"] else f"<span class=why> · {e((it.get("why") or {}).get(str(j)))}</span>"}</li>' for j, o in enumerate(it["opts"]))
        rows.append(f'<li>{au}<p>{e(it["q"])}</p><ul class="opts">{ops}</ul></li>')
    return f'<h4>{title}</h4><ol class="items">{"".join(rows)}</ol>'
parts = []
for d in W["days"]:
    s = [f'<section class="day" id="{e(d["id"])}"><h2>{e(d["label"])} · {e(d["title"])}</h2><p class="muted">{e(d["desc"])}</p><p class="rule">{e(d["rule"])}</p>']
    s.append('<h4>Thẻ từ</h4><table><tr><th>Từ</th><th>Nghĩa</th><th>Ví dụ</th><th>Ghi nhớ</th></tr>' + "".join(
        f'<tr><td>{zt(c["w"], c.get("py") or c.get("ipa"))}</td><td>{e(c.get("mEn"))}{" · " if c.get("mEn") else ""}{e(c["m"])}</td><td>{zt(c["ex"], c.get("expy"))}<span class="vi">{e(c.get("exEn"))} {e(c["exm"])}</span></td><td class="small">{e(c["n"])}</td></tr>' for c in d["cards"]) + "</table>")
    sc = d["scene"]; s.append(f'<h4>Cảnh</h4><p class="muted">{e(sc["setting"])}</p><ol class="lines">' + "".join(f'<li><b>{e(l["who"])}:</b> {zt(l["t"], l.get("py"))}<span class="vi">{e(l.get("en"))} {e(l["vi"])}</span></li>' for l in sc["lines"]) + "</ol>")
    s.append("<h4>Mẫu câu</h4>" + "".join(f'<div class="pat"><b>{e(p["t"])}</b><ul>{"".join(f"<li>{zt(x[0])} <span class=vi>{e(x[2] if len(x) > 2 else "")} {e(x[1])}</span></li>" for x in p["ex"])}</ul><p>✗ {zt(p["bad"])} → ✓ {zt(p["good"])}</p><p class="why">{e(p["why"])}</p></div>' for p in d["patterns"]))
    nt = d.get("notes")
    if nt: s.append(f'<h4>Nghe điền · {e(nt["title"])}</h4><ol class="lines">' + "".join(f'<li><b>{e(l["who"])}:</b> {zt(l["t"], l.get("py"))}<span class="vi">{e(l["vi"])}</span></li>' for l in nt["lines"]) + '</ol><table><tr><th>Ô</th><th>Đáp án</th></tr>' + "".join(f'<tr><td>{e(f["label"])}</td><td class="ok">{e(f.get("answer") or (f["opts"][f["a"]] if f.get("opts") else ""))}</td></tr>' for f in nt["form"]) + "</table>")
    for k, t in (("listen", "Nghe hiểu"), ("vocab", "Từ vựng"), ("grammar", "Ngữ pháp"), ("hsk", "Dạng đề"), ("near", "Từ gần nghĩa" if zh else "Biến đổi từ"), ("orderPara", "Sắp xếp đoạn")):
        s.append(mcs(d.get(k), t))
    s.append("<h4>Nhại theo</h4><ul>" + "".join(f'<li>{zt(x["t"], x.get("py"))} <span class="why">{e(x["focus"])}</span></li>' for x in d["shadow"]) + "</ul>")
    dl = d["dialog"]; s.append(f'<h4>Hội thoại · {e(dl["title"])} (đối tác: {e(dl["partner"])})</h4><ol class="lines">' + "".join(f'<li><b>{e(dl["partner"])}:</b> {zt(t["ai"], t.get("py"))}<span class="vi">{e(t["vi"])}</span><br><b>Bạn:</b> {zt(t["model"], t.get("mpy"))} <span class="why">Gợi ý: {e(t["hint"])}</span></li>' for t in dl["turns"]) + "</ol>")
    lt = d.get("longturn")
    if lt: s.append(f'<h4>Nói dài</h4><p>{zt(lt["cue"], lt.get("cuePy"))}</p><p class="vi">{e(lt["cueVi"])}</p><ul>{"".join(f"<li>{zt(p)}</li>" for p in lt["points"])}</ul><p><b>Bài mẫu:</b> {zt(lt["model"], lt.get("modelPy"))}</p><p class="vi">{e(lt["modelVi"])}</p><p class="small">Cụm hữu ích: {" · ".join(e(u) for u in lt["useful"])}</p><p class="small">Tự chấm: {" · ".join(e(c) for c in lt["check"])}</p>')
    r = d["reading"]; s.append(f'<h4>Đọc · {e(r["title"])}</h4><p>{zt(r["text"], r.get("py"))}</p><p class="vi">{e(r.get("en"))} {e(r["vi"])}</p>' + mcs(r["qs"], "Câu hỏi đọc"))
    w = d.get("write")
    if w: s.append(f'<h4>Viết · {e(w["task"])}</h4><pre>{e(w["model"])}</pre><p class="small">Khung: {e(w["frame"])}</p><p class="small">Tự kiểm tra: {" · ".join(e(c) for c in w["check"])}</p>')
    s.append("</section>"); parts.append("".join(s))
nav = "".join(f'<a href="#{e(d["id"])}">{e(d["label"])}</a>' for d in W["days"])
page = f'''<!doctype html><html lang="vi"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Duyệt {e(W["level"])} tuần 1</title>
<style>:root{{--ink:#0E1730;--muted:#515B70;--line:#DDE2EC;--bg:#F5F6FA;--card:#fff;--ok:#146C43;--acc:#1F44D6}}
@media (prefers-color-scheme:dark){{:root:not([data-theme=light]){{--ink:#EEF2FA;--muted:#A9B3C7;--line:#283553;--bg:#0B1020;--card:#131B31;--ok:#5BD38C;--acc:#8EA2FF}}}}
:root[data-theme=dark]{{--ink:#EEF2FA;--muted:#A9B3C7;--line:#283553;--bg:#0B1020;--card:#131B31;--ok:#5BD38C;--acc:#8EA2FF}}
body{{margin:0;background:var(--bg);color:var(--ink);font:16px/1.6 "Be Vietnam Pro",system-ui,sans-serif}}main{{max-width:980px;margin:0 auto;padding:16px}}
nav{{position:sticky;top:0;background:var(--bg);padding:8px 0;display:flex;gap:8px;flex-wrap:wrap;z-index:2}}nav a{{padding:6px 12px;border-radius:999px;background:var(--card);border:1px solid var(--line);text-decoration:none;color:var(--ink);font-weight:600}}
.day{{background:var(--card);border:1px solid var(--line);border-radius:16px;padding:16px;margin:16px 0}}h1{{font-size:26px}}h2{{font-size:22px;margin:0 0 6px}}h4{{margin:18px 0 6px;color:var(--acc)}}
table{{width:100%;border-collapse:collapse;font-size:15px;display:block;overflow-x:auto}}td,th{{border-bottom:1px solid var(--line);padding:6px;text-align:left;vertical-align:top}}
.t[lang=zh]{{font-size:19px}}.py{{display:block;color:var(--acc);font-size:14px}}.vi{{display:block;color:var(--muted);font-size:14px}}.why{{color:var(--muted);font-size:14px}}.ok{{color:var(--ok);font-weight:700}}.muted{{color:var(--muted)}}.small{{font-size:14px}}
.rule{{border-left:3px solid #FFD43B;padding-left:10px}}.items>li{{margin:8px 0}}.opts{{margin:4px 0}}pre{{white-space:pre-wrap;font:inherit;background:var(--bg);padding:10px;border-radius:10px}}.pat{{border:1px dashed var(--line);border-radius:10px;padding:8px 12px;margin:6px 0}}.au{{color:var(--muted);font-size:14px}}</style></head>
<body><main><h1>Duyệt tuần học thử {e(W["level"])} · {e(W["title"])}</h1><p>{e(W["cando"])}</p><p class="muted">{e(W["story"])}</p><nav>{nav}</nav>{"".join(parts)}</main></body></html>'''
open(out, "w", encoding="utf-8").write(page); print("đã ghi", out)
