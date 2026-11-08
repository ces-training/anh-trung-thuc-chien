#!/usr/bin/env python3
"""Thống kê từng câu của bài kiểm tra đầu vào từ tệp CSV tải ở bảng "Kiểm tra đầu vào" (Google Sheet).
Cách dùng: python3 tools/placement_stats.py duong-dan.csv  → in bảng và ghi tools/placement-stats.md

Mỗi câu: số lượt, % đúng, % "chưa biết", thời gian trung bình, độ phân biệt (tương quan giữa làm đúng câu này
và trình độ được xếp; < 0,2 là câu kém phân biệt: người giỏi và người yếu làm như nhau, hoặc người giỏi lại sai).
Cảnh báo: % đúng > 95% (quá dễ so với mức), < 25% (khó hơn cả đoán bừa với 4 lựa chọn), "chưa biết" > 40%, ít nhất 15 lượt mới kết luận.
Lượt có Độ tin cậy "Nghi đoán" bị bỏ qua."""
import csv, json, os, re, sys, statistics

R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if len(sys.argv) < 2: sys.exit(__doc__)
bank = json.load(open(os.path.join(R, "tools", "course", "placement.json"), encoding="utf-8"))
info = {q["id"]: q for L in ("zh", "en") for q in bank[L]}
LV = {"Chưa học (HSK0)": 0, "HSK1": 1, "HSK2": 2, "HSK3": 3, "HSK4": 4, "Mới bắt đầu (dưới A1)": 0, "A1": 1, "A2": 2, "B1": 3, "B2": 4}

rows = list(csv.DictReader(open(sys.argv[1], encoding="utf-8-sig")))
data, skipped = {}, 0
for r in rows:
    if (r.get("Độ tin cậy") or "").startswith("Nghi đoán"): skipped += 1; continue
    lv = next((v for k, v in LV.items() if (r.get("Trình độ xếp") or "").startswith(k)), None)
    for m in re.finditer(r"(\w+-\d+)=([01?])@([\d.]+)", r.get("Từng câu") or ""):
        d = data.setdefault(m.group(1), []); d.append((m.group(2), float(m.group(3)), lv))

def corr(xs, ys):
    if len(set(xs)) < 2 or len(set(ys)) < 2: return None
    mx, my = statistics.mean(xs), statistics.mean(ys)
    num = sum((a - mx) * (b - my) for a, b in zip(xs, ys)); den = (sum((a - mx) ** 2 for a in xs) * sum((b - my) ** 2 for b in ys)) ** .5
    return num / den if den else None

out = []
for iid, v in sorted(data.items()):
    n = len(v); right = sum(a == "1" for a, _, _ in v) / n; dunno = sum(a == "?" for a, _, _ in v) / n
    t = statistics.mean(s for _, s, _ in v); pairs = [(1 if a == "1" else 0, lv) for a, _, lv in v if lv is not None]
    dsc = corr([p[0] for p in pairs], [p[1] for p in pairs]) if pairs else None
    warn = []
    if n >= 15:
        if right > .95: warn.append("quá dễ")
        if right < .25: warn.append("khó hơn đoán bừa")
        if dunno > .4: warn.append("nhiều người chưa biết")
        if dsc is not None and dsc < .2: warn.append("phân biệt kém")
    else: warn.append("chưa đủ lượt")
    q = info.get(iid, {})
    out.append((iid, q.get("sk", "?"), n, right, dunno, t, dsc, ", ".join(warn), q.get("q", "(câu đã xoá)")))

lines = [f"# Thống kê câu kiểm tra đầu vào", "", f"{len(rows)} lượt, bỏ {skipped} lượt nghi đoán.", "",
         "| Câu | Kỹ năng | Lượt | Đúng | Chưa biết | Giây | Phân biệt | Cảnh báo | Nội dung |", "|---|---|---|---|---|---|---|---|---|"]
for iid, sk, n, right, dunno, t, dsc, warn, q in out:
    lines.append(f"| {iid} | {sk} | {n} | {right:.0%} | {dunno:.0%} | {t:.1f} | {'' if dsc is None else f'{dsc:.2f}'} | {warn} | {q[:60]} |")
open(os.path.join(R, "tools", "placement-stats.md"), "w", encoding="utf-8").write("\n".join(lines) + "\n")
print("\n".join(lines[:3])); print(f"Đã ghi tools/placement-stats.md ({len(out)} câu). Câu có cảnh báo: {sum(1 for o in out if o[7] and o[7] != 'chưa đủ lượt')}")
