"""Tạo giọng đọc qua Gemini Batch API (rẻ bằng nửa giá, không vướng giới hạn 100 lượt/ngày của cách gọi thường).
Dùng chung danh sách, giọng nhân vật, cách lưu và kiểm tra độ dài với make_audio.py.
Chạy: GEMINI_API_KEY=... python3 tools/make_audio_batch.py   (chạy lại được: câu đã có file thì bỏ qua;
lô đã gửi được ghi ở tools/.audio-batches.json để lần sau đọc kết quả, không gửi lại).
Biến tuỳ chọn: CHUNK (số câu mỗi lô, mặc định 120), GEMINI_TTS_MODEL (mặc định gemini-3.8-flash-tts)."""
import base64, json, os, sys, time, urllib.error, urllib.request
sys.path.insert(0, os.path.dirname(__file__))
import make_audio as A

API = "https://generativelanguage.googleapis.com/v1beta/"
MODEL = os.environ.get("GEMINI_TTS_MODEL", "").strip() or "gemini-3.8-flash-tts"
KEY = os.environ.get("GEMINI_API_KEY", "").strip()
STATE = A.ROOT / "tools" / ".audio-batches.json"
CHUNK = int(os.environ.get("CHUNK", "120"))

def req(method, path, body=None):
    r = urllib.request.Request(API + path, method=method, data=json.dumps(body).encode() if body else None,
                               headers={"Content-Type": "application/json", "x-goog-api-key": KEY})
    with urllib.request.urlopen(r, timeout=300) as f:
        return json.load(f)

def voice_of(r):
    return A.VOICES[r["lang"]].get(r["who"]) or A.VOICES.get(r["lang"] + "_course", {}).get(r["who"]) or A.VOICES[r["lang"]]["_"]

def save_pcm(r, pcm):
    if len(pcm) < 24000 * 2 * 0.25: return "quá ngắn"
    secs, n = len(pcm) / 48000, len(r["text"])
    limit = 2.0 + (0.5 * n if r["lang"] == "zh" else 0.13 * n)
    if secs > limit: return f"dài bất thường {secs:.1f}s"
    A.to_mp3(pcm, A.OUT / r["lang"] / (A.clip_id(r) + ".mp3")); return None

def main():
    rows = json.loads(A.LIST.read_text(encoding="utf-8"))
    byid = {A.clip_id(r): r for r in rows}
    state = json.loads(STATE.read_text()) if STATE.exists() else {"batches": []}
    pending_ids = {i for b in state["batches"] if not b.get("done") for i in b["ids"]}
    todo = [r for r in rows if not (A.OUT / r["lang"] / (A.clip_id(r) + ".mp3")).exists() and A.clip_id(r) not in pending_ids]
    print(f"Tổng {len(rows)} câu, cần gửi {len(todo)}, đang chờ {len(pending_ids)}.")
    for i in range(0, len(todo), CHUNK):
        part = todo[i:i + CHUNK]
        body = {"batch": {"display_name": f"giong-{int(time.time())}-{i // CHUNK}", "input_config": {"requests": {"requests": [
            {"request": {"contents": [{"parts": [{"text": r["text"]}]}], "generationConfig": {"responseModalities": ["AUDIO"],
             "speechConfig": {"voiceConfig": {"prebuiltVoiceConfig": {"voiceName": voice_of(r)}}}}}, "metadata": {"key": A.clip_id(r)}} for r in part]}}}}
        try:
            j = req("POST", f"models/{MODEL}:batchGenerateContent", body)
        except urllib.error.HTTPError as e:
            print("Không gửi được lô:", e.code, e.read()[:300]); break
        state["batches"].append({"name": j["name"], "ids": [A.clip_id(r) for r in part]}); STATE.write_text(json.dumps(state))
        print(f"Đã gửi lô {j['name']} ({len(part)} câu)")
    made, bad = 0, []
    while True:
        open_b = [b for b in state["batches"] if not b.get("done")]
        if not open_b: break
        for b in open_b:
            try:
                j = req("GET", b["name"])
            except Exception as e:
                print("Chưa đọc được", b["name"], e); continue
            st = j.get("metadata", {}).get("state", "")
            if st in ("BATCH_STATE_FAILED", "BATCH_STATE_CANCELLED", "BATCH_STATE_EXPIRED"):
                print(f"Lô {b['name']} hỏng ({st}), lần sau gửi lại"); b["done"] = True; continue
            if st != "BATCH_STATE_SUCCEEDED": continue
            for x in j.get("response", {}).get("inlinedResponses", {}).get("inlinedResponses", []):
                cid = (x.get("metadata") or {}).get("key"); r = byid.get(cid)
                if not r: continue
                try:
                    part = next(p for p in x["response"]["candidates"][0]["content"]["parts"] if "inlineData" in p)
                    why = save_pcm(r, base64.b64decode(part["inlineData"]["data"]))
                except Exception as e:
                    why = "không có âm thanh"
                if why: bad.append(f"{cid} {r['text'][:30]} ({why})")
                else: made += 1
            b["done"] = True; print(f"Xong lô {b['name']}, đã lưu {made} file")
        STATE.write_text(json.dumps(state))
        if any(not b.get("done") for b in state["batches"]): time.sleep(30)
    print(f"Đã tạo thêm {made} file, lỗi {len(bad)}, tổng có {A.write_index(rows)} file.")
    for x in bad[:40]: print("✗", x)

if __name__ == "__main__":
    main()
