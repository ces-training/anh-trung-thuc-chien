"""Vẽ tranh minh hoạ bằng Gemini (Nano Banana) cho trang bài tập.

Đọc tools/image-list.json, vẽ tranh nào chưa có, lưu webp vào tuan-1/img/ và viết tuan-1/img/index.json.
Chân dung nhân vật được vẽ trước, rồi dùng làm ảnh tham chiếu để các cảnh giữ đúng gương mặt.
Biến môi trường: GEMINI_API_KEY, GEMINI_IMAGE_MODEL (tuỳ chọn), REDO = "" | "all" | danh sách key cách nhau dấu phẩy.
"""
import base64, hashlib, io, json, os, pathlib, re, sys, time, urllib.error, urllib.request
from PIL import Image

ROOT = pathlib.Path(__file__).resolve().parent.parent
LIST = ROOT / "tools" / "image-list.json"
OUT = ROOT / "tuan-1" / "img"
MODELS = [m for m in [os.environ.get("GEMINI_IMAGE_MODEL", "").strip(), "gemini-3.1-flash-image", "gemini-3.1-flash-image-preview", "gemini-2.5-flash-image"] if m]
WIDTH = {"1:1": 512, "16:9": 1280, "4:3": 800}


def request(model, key, parts, aspect, size=True):
    cfg = {"responseModalities": ["IMAGE"], "imageConfig": {"aspectRatio": aspect}}
    if size:
        cfg["imageConfig"]["imageSize"] = "1K"
    body = {"contents": [{"parts": parts}], "generationConfig": cfg}
    req = urllib.request.Request(f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent",
                                 data=json.dumps(body).encode(), headers={"Content-Type": "application/json", "x-goog-api-key": key})
    with urllib.request.urlopen(req, timeout=180) as f:
        j = json.load(f)
    for c in j.get("candidates", []):
        for p in c.get("content", {}).get("parts", []):
            if "inlineData" in p:
                return base64.b64decode(p["inlineData"]["data"])
    raise RuntimeError("Không có ảnh trong phản hồi: " + json.dumps(j)[:300])


def save(raw, key, aspect):
    im = Image.open(io.BytesIO(raw)).convert("RGB")
    w = WIDTH.get(aspect, 800)
    if im.width > w:
        im = im.resize((w, round(im.height * w / im.width)), Image.LANCZOS)
    dest = OUT / f"{key}.webp"
    im.save(dest, "WEBP", quality=80, method=6)
    return dest


def write_index(items):
    idx = {}
    for it in items:
        f = OUT / f'{it["key"]}.webp'
        if f.exists():
            idx[it["key"]] = f"{f.name}?v={hashlib.md5(f.read_bytes()).hexdigest()[:8]}"
    (OUT / "index.json").write_text(json.dumps(idx, indent=0), encoding="utf-8")
    return len(idx)


def main():
    items = json.loads(LIST.read_text(encoding="utf-8"))
    OUT.mkdir(parents=True, exist_ok=True)
    redo = os.environ.get("REDO", "").strip()
    if redo:
        keys = None if redo == "all" else {x.strip() for x in redo.split(",")}
        for it in items:
            f = OUT / f'{it["key"]}.webp'
            if f.exists() and (keys is None or it["key"] in keys):
                f.unlink()
    todo = [it for it in items if not (OUT / f'{it["key"]}.webp').exists()]
    print(f"Tổng {len(items)} tranh, cần vẽ {len(todo)}.")
    key = os.environ.get("GEMINI_API_KEY", "").strip()
    if todo and not key:
        print("::error::Chưa có secret GEMINI_API_KEY."); write_index(items); sys.exit(1)
    mi, size, made, fails = 0, True, 0, 0
    for it in todo:
        missing = [r for r in it["refs"] if not (OUT / f"{r}.webp").exists()]
        if missing:
            print(f"Bỏ qua {it['key']} vì chưa có chân dung {missing}"); continue
        parts = [{"text": it["prompt"]}]
        for r in it["refs"]:
            parts.append({"inlineData": {"mimeType": "image/webp", "data": base64.b64encode((OUT / f"{r}.webp").read_bytes()).decode()}})
        for attempt in range(6):
            try:
                raw = request(MODELS[mi], key, parts, it["aspect"], size)
                save(raw, it["key"], it["aspect"]); made += 1
                print(f"✓ {it['key']} ({MODELS[mi]})"); time.sleep(float(os.environ.get("PAUSE", "2")))
                break
            except urllib.error.HTTPError as e:
                msg = e.read().decode(errors="ignore")
                if e.code == 404 and mi + 1 < len(MODELS):
                    print(f"Không thấy model {MODELS[mi]}, chuyển sang {MODELS[mi + 1]}"); mi += 1; continue
                if e.code == 400 and size and "imageSize" in msg:
                    size = False; continue
                if e.code == 429:
                    if "limit: 0" in msg or "free_tier" in msg and "limit: 0" in msg:
                        print("::error::Khoá API chưa bật thanh toán: Gemini không cho vẽ tranh ở gói miễn phí. Bật billing trong Google AI Studio rồi chạy lại.")
                        print(f"Đã vẽ {made} tranh, tổng có {write_index(items)}."); sys.exit(1)
                    if "PerDay" in msg or "per day" in msg.lower():
                        print("Hết lượt trong ngày, lần chạy sau làm tiếp."); print(f"Đã vẽ {made}, tổng có {write_index(items)}."); return
                    m = re.search(r'"retryDelay":\s*"(\d+)', msg); wait = int(m.group(1)) + 2 if m else 30
                    print(f"Bị giới hạn tốc độ, chờ {wait} giây…"); time.sleep(wait); continue
                print(f"✗ {it['key']}: HTTP {e.code} {msg[:400]}"); fails += 1; break
            except Exception as e:
                print(f"✗ {it['key']}: {e}"); time.sleep(5)
                if attempt == 5: fails += 1
    print(f"Đã vẽ thêm {made} tranh, lỗi {fails}, tổng có {write_index(items)} tranh.")


if __name__ == "__main__":
    main()
