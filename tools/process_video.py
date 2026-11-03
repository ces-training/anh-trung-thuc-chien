"""Đưa video Google Flow lên web: nén, tìm đoạn có lời nói, canh phụ đề theo từng câu.

python3 tools/process_video.py <các file .mp4 đặt tên theo bộ ngữ liệu, vd zh-w1-thu-2-1.mp4>
- Nén H.264 960px + AAC, lưu vào tuan-1/vid/
- Dò khoảng lặng trong tiếng (ffmpeg silencedetect) để tìm từng câu nói, gán lần lượt cho các câu của đoạn
- Ghi tuan-1/vid/index.json; cảnh nào đủ mọi đoạn thì web tự chuyển sang phát video + phụ đề
"""
import json, pathlib, re, subprocess, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
VID = ROOT / "tuan-1" / "vid"
KIT = {s["key"]: s for s in json.loads((ROOT / "tools" / "flow-kit.json").read_text(encoding="utf-8"))}


def speech_segments(path):
    dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", path], capture_output=True, text=True).stdout or 0)
    err = subprocess.run(["ffmpeg", "-hide_banner", "-i", path, "-vn", "-af", "highpass=f=120,silencedetect=noise=-32dB:d=0.22", "-f", "null", "-"], capture_output=True, text=True).stderr
    starts = [float(x) for x in re.findall(r"silence_start: ([\d.]+)", err)]
    ends = [float(x) for x in re.findall(r"silence_end: ([\d.]+)", err)]
    sil = []
    for i, s in enumerate(starts):
        sil.append((s, ends[i] if i < len(ends) else dur))
    segs, t = [], 0.0
    for s, e in sil:
        if s - t > 0.15: segs.append([t, s])
        t = e
    if dur - t > 0.15: segs.append([t, dur])
    return [x for x in segs if x[1] - x[0] >= 0.25], dur


def fit(segs, n, weights):
    segs = [list(x) for x in segs]
    while len(segs) > n:  # gộp hai đoạn có khoảng lặng ngắn nhất
        gaps = [segs[i + 1][0] - segs[i][1] for i in range(len(segs) - 1)]
        i = gaps.index(min(gaps)); segs[i] = [segs[i][0], segs[i + 1][1]]; del segs[i + 1]
    if len(segs) < n:  # thiếu đoạn: chia khoảng nói theo độ dài câu
        a, b = (segs[0][0], segs[-1][1]) if segs else (0.3, 7.5)
        tot = sum(weights); out, t = [], a
        for w in weights:
            d = (b - a) * w / tot; out.append([t, t + d]); t += d
        return out
    return segs


def main(files):
    idx = json.loads((VID / "index.json").read_text()) if (VID / "index.json").exists() else {}
    for f in files:
        name = pathlib.Path(f).name
        m = re.match(r"((?:zh|en)-w\d+-thu-\d)-(\d+)\.mp4$", name)
        if not m or m.group(1) not in KIT:
            print("Bỏ qua (sai tên):", name); continue
        key, n = m.group(1), int(m.group(2)); clip = KIT[key]["clips"][n - 1]
        dest = VID / name
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", f, "-c:v", "libx264", "-preset", "veryfast", "-crf", "27", "-vf", "scale=960:-2",
                        "-c:a", "aac", "-b:a", "96k", "-movflags", "+faststart", str(dest)], check=True)
        segs, dur = speech_segments(str(dest))
        w = [max(1, len(x["t"])) for x in clip["say"]]
        cues = [[round(s, 2), round(e, 2), li] for (s, e), li in zip(fit(segs, len(clip["lines"]), w), clip["lines"])]
        ent = idx.get(key) if isinstance(idx.get(key), dict) else {"clips": []}
        clips = {c["src"]: c for c in ent.get("clips", [])}
        clips[name] = {"src": name, "n": n, "cues": cues, "dur": round(dur, 2)}
        ent["clips"] = sorted(clips.values(), key=lambda c: c["n"])
        ent["complete"] = len(ent["clips"]) == len(KIT[key]["clips"])
        idx[key] = ent
        print(f"✓ {name}: {len(segs)} đoạn nói → {len(cues)} câu {cues}")
    (VID / "index.json").write_text(json.dumps(idx, ensure_ascii=False, indent=0), encoding="utf-8")


if __name__ == "__main__":
    main(sys.argv[1:])
