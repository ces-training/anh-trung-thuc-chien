"""Tạo file giọng đọc mẫu bằng Gemini TTS cho trang bài tập.

Đọc tools/audio-list.json, gọi Gemini cho câu nào chưa có file, lưu mp3 vào
tuan-1/audio/<lang>/<id>.mp3 rồi viết tuan-1/audio/index.json để trang web dùng.
Chạy lại bao nhiêu lần cũng được: file đã có thì bỏ qua.
Biến môi trường: GEMINI_API_KEY (bắt buộc), GEMINI_TTS_MODEL (tuỳ chọn),
REDO = "" | "all" | danh sách id cách nhau dấu phẩy.
"""
import base64, hashlib, json, os, pathlib, re, subprocess, sys, time, urllib.error, urllib.request

ROOT = pathlib.Path(__file__).resolve().parent.parent
LIST = ROOT / "tools" / "audio-list.json"
OUT = ROOT / "tuan-1" / "audio"
MODELS = [m for m in [os.environ.get("GEMINI_TTS_MODEL", "").strip(), "gemini-3.1-flash-tts-preview", "gemini-2.5-flash-preview-tts"] if m]

# Giọng cho từng nhân vật (giọng có sẵn của Gemini). "_" = giọng đọc thẻ, câu mẫu.
VOICES = {
    "en": {"_": "Kore", "An": "Aoede", "Tom": "Puck", "Kevin": "Charon", "Linh": "Leda", "Sarah": "Despina"},
    "zh": {"_": "Kore", "An": "Aoede", "王丽": "Despina", "Lệ": "Despina", "Minh": "Orus", "阮明": "Orus", "王经理": "Iapetus"},
}
STYLE = {
    "en": "Say this clearly and naturally, in a warm, friendly tone, at a calm pace for language learners: ",
    "zh": "请用标准普通话，清楚、自然、友好地说，语速适合初学者：",
}


def clip_id(r):
    return hashlib.sha1(f'{r["lang"]}|{r["who"]}|{r["text"]}'.encode()).hexdigest()[:12]


def call(model, key, text, voice):
    body = {
        "contents": [{"parts": [{"text": text}]}],
        "generationConfig": {"responseModalities": ["AUDIO"],
                             "speechConfig": {"voiceConfig": {"prebuiltVoiceConfig": {"voiceName": voice}}}},
    }
    req = urllib.request.Request(
        f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent",
        data=json.dumps(body).encode(), headers={"Content-Type": "application/json", "x-goog-api-key": key})
    with urllib.request.urlopen(req, timeout=120) as f:
        j = json.load(f)
    for part in j["candidates"][0]["content"]["parts"]:
        if "inlineData" in part:
            return base64.b64decode(part["inlineData"]["data"])
    raise RuntimeError("Không có âm thanh trong phản hồi")


def to_mp3(pcm, dest):
    dest.parent.mkdir(parents=True, exist_ok=True)
    # PCM 24 kHz, 16-bit, mono -> mp3; cắt khoảng lặng đầu, chừa 0,15 giây cuối
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-f", "s16le", "-ar", "24000", "-ac", "1", "-i", "pipe:0",
                    "-af", "silenceremove=start_periods=1:start_threshold=-45dB,apad=pad_dur=0.15",
                    "-codec:a", "libmp3lame", "-q:a", "4", str(dest)], input=pcm, check=True)


def write_index(rows):
    idx = {"en": {}, "zh": {}}
    for r in rows:
        f = OUT / r["lang"] / (clip_id(r) + ".mp3")
        if f.exists():
            idx[r["lang"]].setdefault(r["text"], {})[r["who"] or "_"] = f'{r["lang"]}/{f.name}'
    (OUT / "index.json").write_text(json.dumps(idx, ensure_ascii=False, indent=0), encoding="utf-8")
    return sum(len(v) for d in idx.values() for v in d.values())


def main():
    rows = json.loads(LIST.read_text(encoding="utf-8"))
    OUT.mkdir(parents=True, exist_ok=True)
    redo = os.environ.get("REDO", "").strip()
    if redo:
        ids = None if redo == "all" else {x.strip() for x in redo.split(",")}
        for r in rows:
            f = OUT / r["lang"] / (clip_id(r) + ".mp3")
            if f.exists() and (ids is None or clip_id(r) in ids):
                f.unlink()
    todo = [r for r in rows if not (OUT / r["lang"] / (clip_id(r) + ".mp3")).exists()]
    print(f"Tổng {len(rows)} câu, cần tạo {len(todo)}.")
    key = os.environ.get("GEMINI_API_KEY", "").strip()
    if todo and not key:
        print("::error::Chưa có secret GEMINI_API_KEY trong Settings → Secrets and variables → Actions.")
        write_index(rows); sys.exit(1)
    model_i, made, fails = 0, 0, 0
    for r in todo:
        voice = VOICES[r["lang"]].get(r["who"], VOICES[r["lang"]]["_"])
        text = STYLE[r["lang"]] + r["text"]
        for attempt in range(6):
            try:
                pcm = call(MODELS[model_i], key, text, voice)
                if len(pcm) < 24000 * 2 * 0.25:
                    raise RuntimeError("Âm thanh quá ngắn")
                to_mp3(pcm, OUT / r["lang"] / (clip_id(r) + ".mp3"))
                made += 1
                print(f"✓ {clip_id(r)} [{r['lang']} {r['who'] or '_'} · {voice}] {r['text']}")
                time.sleep(float(os.environ.get("PAUSE", "1")))
                break
            except urllib.error.HTTPError as e:
                msg = e.read().decode(errors="ignore")
                if e.code == 404 and model_i + 1 < len(MODELS):
                    print(f"Không thấy model {MODELS[model_i]}, chuyển sang {MODELS[model_i + 1]}"); model_i += 1; continue
                if e.code == 402:
                    print("::error::Hết tiền trả trước (prepay credits) của khoá Gemini. Nạp thêm ở https://ai.studio/projects rồi chạy lại.")
                    write_index(rows); sys.exit(1)
                if e.code == 429:
                    if "PerDay" in msg or "per day" in msg.lower():
                        print("Hết lượt miễn phí trong ngày. Lần chạy sau sẽ làm tiếp.")
                        print(f"Đã tạo thêm {made} file, tổng có {write_index(rows)} file."); return
                    m = re.search(r'"retryDelay":\s*"(\d+)', msg)
                    wait = int(m.group(1)) + 2 if m else 30
                    print(f"Bị giới hạn tốc độ, chờ {wait} giây…"); time.sleep(wait); continue
                print(f"✗ {r['text']}: HTTP {e.code} {msg[:300]}"); fails += 1; break
            except Exception as e:
                print(f"✗ {r['text']}: {e}"); time.sleep(3)
                if attempt == 5: fails += 1
    print(f"Đã tạo thêm {made} file, lỗi {fails}, tổng có {write_index(rows)} file.")


if __name__ == "__main__":
    main()
