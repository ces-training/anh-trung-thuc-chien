"""Gộp câu của mọi tuần học vào tools/audio-list.json để make_audio.py tạo giọng (chạy: python3 tools/audio_course.py).
Giữ nguyên các dòng cũ (lời người hướng dẫn, câu đã có), chỉ thêm câu còn thiếu, không trùng.
Thứ tự ưu tiên: tuần 1 → 5 tuần học thử → tuần 2 → các tuần sau, để nếu hết lượt thì phần quan trọng xong trước."""
import contextlib, io, json, os, re, sys
sys.path.insert(0, os.path.dirname(__file__))
with contextlib.redirect_stdout(io.StringIO()):
    import media_need as M

LIST = os.path.join(M.R, "tools", "audio-list.json")
rows = json.load(open(LIST, encoding="utf-8"))
have = {(r["lang"], r["who"] or "_", r["text"]) for r in rows}

def rank(name):
    if re.search(r"-w1$", name): return (0, name)
    if not re.search(r"-w\d+$", name): return (1, name)
    return (2 + int(name.split("-w")[1]), name)

added = 0
for name, W in sorted(M.week_files(), key=lambda x: rank(x[0])):
    for L, who, t, kind in M.clips(W):
        k = (L, who or "_", t)
        if k in have or (L, "_", t) in have: continue
        have.add(k); rows.append({"lang": L, "who": "" if who == "_" else who, "text": t}); added += 1
json.dump(rows, open(LIST, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(f"Thêm {added} câu, danh sách có {len(rows)} câu.")
