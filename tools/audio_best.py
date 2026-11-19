"""Thu lại giọng đọc sạch: mỗi câu thử vài lần (model Pro trước, Flash sau), đo độ rè, giữ bản sạch nhất.

Vì sao cần: từ 11/2026 các model TTS của Gemini hay ra tiếng quá to, vỡ (rè). Độ rè đo bằng số chỗ
sóng âm nhảy vọt (|chênh lệch giữa 2 mẫu liền nhau| > 0,5) trên 10.000 mẫu; giọng cũ chị Duyên thấy
ổn có trung vị khoảng 0,8. Câu ngắn (1–2 chữ, dãy số) model hay không chịu đọc, nên thử thêm lời dặn
("请读：", "Say: ") và dùng Whisper nghe lại để chắc chỉ đọc đúng câu, không đọc lời dặn.

Cách chạy (ở thư mục repo):
  GEMINI_API_KEY=... python3 tools/audio_best.py              # các câu chưa có file
  GEMINI_API_KEY=... IDS_FILE=ds.txt python3 tools/audio_best.py  # thu lại danh sách id (mỗi dòng 1 id hoặc đường dẫn mp3)
Cần: pip install faster-whisper pypinyin (Whisper chỉ chạy khi có lời dặn).
"""
import base64, difflib, json, os, pathlib, re, sys, time, urllib.error, urllib.request
import numpy as np

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import make_audio as M

KEY = os.environ["GEMINI_API_KEY"].strip()
GOOD = float(os.environ.get("GOOD", "3"))      # độ rè chấp nhận ngay
OKAY = float(os.environ.get("OKAY", "8"))      # nếu thử hết mà chưa đạt GOOD thì vẫn nhận bản tốt nhất nếu ≤ OKAY
TRIES = [("gemini-2.5-pro-preview-tts", "{t}"), ("gemini-2.5-pro-preview-tts", "{t}"), ("gemini-2.5-flash-preview-tts", "{t}"),
         ("gemini-2.5-pro-preview-tts", "{t}"), ("gemini-2.5-flash-preview-tts", "{t}")]
SHORT = {"zh": ["请读：{t}", "Say: {t}", "Transcript: {t}", "Say in Mandarin Chinese: {t}"],
         "en": ["Read aloud: {t}", "Say: {t}", "Transcript: {t}"], "vi": ["Đọc: {t}", "Say: {t}"]}
DIG = str.maketrans("0123456789", "零一二三四五六七八九")
_W = None


def call(model, text, voice):
    body = {"contents": [{"parts": [{"text": text}]}],
            "generationConfig": {"responseModalities": ["AUDIO"], "speechConfig": {"voiceConfig": {"prebuiltVoiceConfig": {"voiceName": voice}}}}}
    req = urllib.request.Request(f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent",
                                 data=json.dumps(body).encode(), headers={"Content-Type": "application/json", "x-goog-api-key": KEY})
    for _ in range(6):  # bị giới hạn tốc độ (429) thì chờ rồi gọi lại, không tính là một lần thử
        try:
            j = json.load(urllib.request.urlopen(req, timeout=180)); break
        except urllib.error.HTTPError as e:
            msg = e.read().decode(errors="ignore")
            if e.code == 402: sys.exit("Hết tiền trả trước của khoá Gemini.")
            if e.code != 429: return None
            m = re.search(r'"retryDelay":\s*"(\d+)', msg); time.sleep(int(m.group(1)) + 2 if m else 30)
        except Exception:
            return None
    else:
        return None
    for p in j.get("candidates", [{}])[0].get("content", {}).get("parts", []):
        if "inlineData" in p: return M.wav_data(base64.b64decode(p["inlineData"]["data"]))
    return None


def crackle(pcm):
    a = np.frombuffer(pcm[:len(pcm) // 2 * 2], dtype=np.int16).astype(np.float32) / 32768
    return float((np.abs(np.diff(a)) > 0.5).sum() / max(len(a), 1) * 1e4)


def norm(s, lang):
    if lang == "zh":
        from pypinyin import lazy_pinyin
        s = "".join(ch for ch in s.translate(DIG) if "一" <= ch <= "鿿")
        return " ".join(lazy_pinyin(s))
    return " ".join(re.findall(r"[a-zà-ỹđ]+|\d", s.lower()))


def says_only(pcm, r):
    global _W
    import scipy.signal as ss
    from faster_whisper import WhisperModel
    if _W is None: _W = WhisperModel("small", device="cpu", compute_type="int8")
    a = np.frombuffer(pcm, dtype=np.int16).astype(np.float32) / 32768
    seg, _ = _W.transcribe(ss.resample_poly(a, 2, 3), language=r["lang"], beam_size=5)
    h = "".join(x.text for x in seg)
    hs = [h]
    if r["lang"] == "zh":  # Whisper hay viết số bằng chữ số: thử cả đọc từng chữ số (số điện thoại) lẫn đọc thành số (2500 → 二千五百)
        try:
            import cn2an; hs.append(cn2an.transform(h, "an2cn"))
        except Exception: pass
        hs = [x.replace("两", "二") for x in hs]
    want = norm(r["text"].replace("两", "二") if r["lang"] == "zh" else r["text"], r["lang"])
    for x in hs:
        got = norm(x, r["lang"])
        if difflib.SequenceMatcher(None, want, got).ratio() >= 0.75 and len(got) <= len(want) * 1.25 + 3: return True
    print(f"    nghe thành: {h.strip()}", flush=True)
    return False


def one(r):
    voice = M.VOICES[r["lang"]].get(r["who"]) or M.VOICES.get(r["lang"] + "_course", {}).get(r["who"]) or M.VOICES[r["lang"]]["_"]
    n = len(r["text"]); limit = 2.0 + (0.5 * n if r["lang"] == "zh" else 0.13 * n)
    plan = TRIES + [(m, p) for p in SHORT.get(r["lang"], []) for m in ("gemini-2.5-pro-preview-tts", "gemini-2.5-flash-preview-tts")]
    plan += [("gemini-3.8-flash-tts", "{t}")] * 5  # 2.5 không chịu đọc một số từ đơn, con số: dùng 3.8, chỉ nhận bản ít rè
    best = None
    for model, p in plan:
        pcm = call(model, p.format(t=r["text"]), voice)
        time.sleep(0.3)
        if not pcm or len(pcm) < 24000 * 2 * 0.25 or len(pcm) / 48000 > limit + (1.5 if p != "{t}" else 0): continue
        if p != "{t}" and not says_only(pcm, r): continue
        c = crackle(pcm)
        if best is None or c < best[0]: best = (c, pcm, model[11:14], p[:8])
        if c <= GOOD: break
    if best and best[0] <= OKAY:
        M.to_mp3(best[1], M.OUT / r["lang"] / (M.clip_id(r) + ".mp3"))
        return best
    return best and (best[0], None, best[2], best[3])


def main():
    rows = json.loads(M.LIST.read_text(encoding="utf-8"))
    ids = None
    if os.environ.get("IDS_FILE"):
        ids = {pathlib.Path(x.strip()).stem for x in open(os.environ["IDS_FILE"]) if x.strip()}
    todo = [r for r in rows if (M.clip_id(r) in ids if ids is not None else not (M.OUT / r["lang"] / (M.clip_id(r) + ".mp3")).exists())]
    print(f"Cần thu {len(todo)} câu.", flush=True)
    ok = bad = 0
    for i, r in enumerate(todo, 1):
        b = one(r)
        if b and b[1] is not None:
            ok += 1; print(f"✓ {i}/{len(todo)} rè {b[0]:.1f} [{b[2]} {b[3]}] {r['text'][:40]}", flush=True)
        else:
            bad += 1; print(f"✗ {i}/{len(todo)} {'rè %.1f' % b[0] if b else 'không đọc'} {r['who']} {r['text'][:40]}", flush=True)
        if i % 25 == 0: M.write_index(rows)
    print(f"Xong: {ok} đạt, {bad} chưa đạt; tổng {M.write_index(rows)} file.")


if __name__ == "__main__":
    main()
