"""Tạo trang 'Bộ ngữ liệu Google Flow' từ tools/flow-kit.json.
python3 tools/flow_page.py <file html ra> <tiền tố ảnh khung> <tiền tố ảnh nhân vật>
"""
import json, pathlib, sys, html
ROOT = pathlib.Path(__file__).resolve().parent.parent
kit = json.loads((ROOT / "tools" / "flow-kit.json").read_text(encoding="utf-8"))
out, fpre, ipre = sys.argv[1], sys.argv[2], sys.argv[3]
KNOWN = {"an", "tom", "kevin", "linh", "sarah", "wangli", "minh", "wangjl"}
idx = json.loads((ROOT / "tuan-1" / "img" / "index.json").read_text())
def char_img(k):
    key = ("char-" if k in KNOWN else "cast-") + k
    return f"{ipre}{key}.webp" if key in idx else ""
E = html.escape
cards = []
for s in kit:
    lang = "Tiếng Trung" if s["lang"] == "zh" else "Tiếng Anh"
    cast = "".join(f'<figure>{f"<img src={chr(34)}{char_img(c["key"])}{chr(34)} alt={chr(34)}{E(c["name"])}{chr(34)}><a class=dl href={chr(34)}{char_img(c["key"])}{chr(34)} download>Tải ảnh</a>" if char_img(c["key"]) else "<div class=noimg>Chưa có ảnh</div>"}<figcaption><b>{E(c["name"])}</b><small>{E(c["look"])}</small></figcaption></figure>' for c in s["cast"])
    clips = []
    for i, c in enumerate(s["clips"]):
        say = "".join(f'<li><span class=who>{E(x["who"])}</span><span class=t lang="{s["lang"]}">{E(x["t"])}</span>{f"<span class=py>{E(x[chr(112)+chr(121)])}</span>" if x.get("py") else ""}<span class=vi>{E(x["vi"])}</span></li>' for x in c["say"])
        clips.append(f'''<div class="clip"><div class="ch"><b>Đoạn {i+1}/{len(s["clips"])}</b><span>Lưu file tên: <code>{E(c["file"])}</code></span></div>
<ol class="say">{say}</ol>
<details><summary>Câu lệnh dán vào Flow</summary><textarea readonly rows="9">{E(c["prompt"])}</textarea></details>
<button class="cp" data-t="{E(c["prompt"])}">Chép câu lệnh</button></div>''')
    img = f'<img src="{fpre}{s["imageKey"]}.jpg" alt="Ảnh khung đầu"><a class="dl" href="{fpre}{s["imageKey"]}.jpg" download="{s["imageKey"]}.jpg">Tải ảnh khung đầu</a>' if s["image"] else "<div class=noimg>Chưa có ảnh khung</div>"
    cards.append(f'''<section class="scene" data-lang="{s["lang"]}" data-week="{s["week"]}"><header><p class="eyebrow">{lang} · Tuần {s["week"]} · {E(s["day"])} · mã <code>{E(s["key"])}</code></p><h2>{E(s["title"])}</h2><p>{E(s["setting"])}</p></header>
<div class="grid"><div class="frame">{img}</div><div class="cast">{cast}</div></div>
<div class="clips">{"".join(clips)}</div></section>''')
total = sum(len(s["clips"]) for s in kit)
page = f'''<!doctype html><html lang="vi"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Bộ ngữ liệu Flow</title>
<style>
:root{{--bg:#F5F6FA;--card:#fff;--ink:#0E1730;--muted:#515B70;--line:#DDE2EC;--en:#1F44D6;--zh:#D3271E;--sun:#FFD43B;--soft:#EEF1F8}}
@media (prefers-color-scheme:dark){{:root:not([data-theme="light"]){{--bg:#0B1020;--card:#131B31;--ink:#EEF2FA;--muted:#A9B3C7;--line:#283553;--soft:#18223C;--en:#8EA2FF;--zh:#FF8475}}}}
:root[data-theme="dark"]{{--bg:#0B1020;--card:#131B31;--ink:#EEF2FA;--muted:#A9B3C7;--line:#283553;--soft:#18223C;--en:#8EA2FF;--zh:#FF8475}}
*{{box-sizing:border-box}}body{{margin:0;background:var(--bg);color:var(--ink);font:15px/1.55 "Be Vietnam Pro",system-ui,sans-serif}}
main{{max-width:1100px;margin:0 auto;padding:20px 16px 60px}}h1{{margin:0 0 6px;font-size:26px}}.lead{{color:var(--muted)}}
.steps{{background:var(--card);border-radius:16px;padding:14px 18px;border:1px solid var(--line)}}.steps li{{margin:4px 0}}
.bar{{display:flex;gap:8px;flex-wrap:wrap;margin:14px 0;position:sticky;top:0;background:var(--bg);padding:8px 0;z-index:2}}
.bar button{{border:1.5px solid var(--line);background:var(--card);color:var(--ink);border-radius:999px;padding:6px 14px;font:inherit;font-weight:600;cursor:pointer}}.bar button[aria-pressed=true]{{background:var(--ink);color:var(--bg)}}
.scene{{background:var(--card);border:1px solid var(--line);border-radius:20px;padding:16px;margin:14px 0}}
.scene[data-lang=zh]{{border-left:6px solid var(--zh)}}.scene[data-lang=en]{{border-left:6px solid var(--en)}}
.eyebrow{{margin:0;font-size:12.5px;font-weight:700;color:var(--muted)}}.scene h2{{margin:2px 0 4px;font-size:20px}}.scene header p{{margin:2px 0}}
.grid{{display:grid;grid-template-columns:minmax(0,1.4fr) minmax(0,1fr);gap:14px;margin:10px 0}}@media(max-width:760px){{.grid{{grid-template-columns:minmax(0,1fr)}}}}
.frame img{{width:100%;border-radius:14px;display:block;aspect-ratio:16/9;object-fit:cover}}
.cast{{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:10px;align-content:start}}
.cast figure{{margin:0;background:var(--soft);border-radius:12px;padding:8px}}.cast img{{width:100%;aspect-ratio:1;object-fit:cover;border-radius:10px}}
.cast figcaption small{{display:block;color:var(--muted);font-size:12px;line-height:1.35}}
.dl{{display:inline-block;margin-top:6px;font-weight:700;font-size:13px;color:var(--en)}}
.noimg{{padding:20px;text-align:center;color:var(--muted);background:var(--soft);border-radius:10px}}
.clips{{display:grid;gap:10px}}.clip{{border:1.5px dashed var(--line);border-radius:14px;padding:10px 12px}}
.ch{{display:flex;justify-content:space-between;gap:8px;flex-wrap:wrap}}code{{background:var(--soft);padding:1px 6px;border-radius:6px}}
.say{{margin:8px 0;padding-left:18px}}.say li{{margin:4px 0}}.who{{font-weight:800;margin-right:6px}}.t{{font-weight:700}}.t[lang=zh]{{font-size:18px}}
.py,.vi{{display:block;font-size:13px;color:var(--muted)}}.py{{color:var(--zh)}}
textarea{{width:100%;font:12.5px/1.45 ui-monospace,monospace;border-radius:10px;border:1px solid var(--line);background:var(--soft);color:var(--ink);padding:8px}}
.cp{{margin-top:6px;border:0;background:var(--en);color:#fff;border-radius:999px;padding:7px 16px;font:inherit;font-weight:700;cursor:pointer}}
</style></head><body><main>
<h1>Bộ ngữ liệu làm video trên Google Flow</h1>
<p class="lead">{len(kit)} cảnh · {total} đoạn video 8 giây. Mỗi đoạn: ảnh khung đầu + câu lệnh có sẵn lời thoại. Phụ đề do web tự chạy, không cần làm trong Flow.</p>
<ol class="steps"><li>Trong Flow chọn <b>Frames to Video</b>, tải <b>ảnh khung đầu</b> của cảnh lên (ảnh nhân vật dùng làm ảnh tham chiếu nếu Flow cho phép).</li>
<li>Bấm <b>Chép câu lệnh</b> của từng đoạn, dán vào Flow, tạo video.</li>
<li>Tải video về, <b>đặt đúng tên file</b> ghi ở mỗi đoạn, rồi gửi cho em (kéo vào chat hoặc thả vào thư mục chung). Em tự nén, tự canh phụ đề theo lời nói và đưa lên web.</li></ol>
<div class="bar" role="group" aria-label="Lọc"><button data-f="all" aria-pressed="true">Tất cả</button><button data-f="zh" aria-pressed="false">Tiếng Trung</button><button data-f="en" aria-pressed="false">Tiếng Anh</button><button data-f="w1" aria-pressed="false">Tuần 1</button><button data-f="w2" aria-pressed="false">Tuần 2</button></div>
{"".join(cards)}
</main><script>
document.querySelectorAll('.cp').forEach(b=>b.onclick=async()=>{{try{{await navigator.clipboard.writeText(b.dataset.t);b.textContent='Đã chép ✓';}}catch(e){{const t=b.parentElement.querySelector('textarea');b.parentElement.querySelector('details').open=true;t.select();b.textContent='Chép bằng Ctrl+C';}}setTimeout(()=>b.textContent='Chép câu lệnh',2000);}});
document.querySelectorAll('.bar button').forEach(b=>b.onclick=()=>{{const f=b.dataset.f;document.querySelectorAll('.bar button').forEach(x=>x.setAttribute('aria-pressed',x===b));
document.querySelectorAll('.scene').forEach(s=>{{s.hidden=!(f==='all'||s.dataset.lang===f||('w'+s.dataset.week)===f);}});}});
</script></body></html>'''
pathlib.Path(out).write_text(page, encoding="utf-8")
print("ok", out)
