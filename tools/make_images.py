"""Vẽ tranh minh hoạ cho trang bài tập, theo cách rẻ nhất mà vẫn giữ chất lượng.

- Tranh có nhân vật cố định (chân dung, cảnh có ảnh tham chiếu): Gemini Flash Image, vì cần giữ đúng gương mặt.
- Tranh minh hoạ từ vựng (không cần tham chiếu): Imagen 4 Fast, rẻ hơn khoảng 3 lần.
- Mỗi tranh vẽ xong được một model đọc ảnh rất rẻ kiểm tra (thừa tay, chữ giả, mặt méo).
  Không đạt thì vẽ lại tối đa 1 lần; vẫn không đạt thì giữ tranh nhưng ghi vào báo cáo để người xem duyệt.
- Tranh đã có thì không vẽ lại. Cuối mỗi lần chạy in ra chi phí ước tính.

Biến môi trường: GEMINI_API_KEY, REDO = "" | "all" | danh sách key cách nhau dấu phẩy,
IMAGE_MODEL_REF / IMAGE_MODEL_CHEAP / QA_MODEL (tuỳ chọn, để đổi model).
"""
import base64, hashlib, io, json, os, pathlib, re, sys, time, urllib.error, urllib.request
from PIL import Image

ROOT = pathlib.Path(__file__).resolve().parent.parent
LIST = ROOT / "tools" / "image-list.json"
OUT = ROOT / "tuan-1" / "img"
QA_FILE = ROOT / "tools" / "image-qa.json"
API = "https://generativelanguage.googleapis.com/v1beta/models/"
REF_MODELS = [m for m in [os.environ.get("IMAGE_MODEL_REF", "").strip(), "gemini-3.1-flash-image", "gemini-2.5-flash-image"] if m]
CHEAP_MODELS = [m for m in [os.environ.get("IMAGE_MODEL_CHEAP", "").strip(), "gemini-3.1-flash-lite-image"] if m]
QA_MODELS = [m for m in [os.environ.get("QA_MODEL", "").strip(), "gemini-2.5-flash-lite", "gemini-flash-lite-latest"] if m]
# Giá ước tính (USD/tranh) để in báo cáo chi phí
PRICE = {"gemini-3.1-flash-image": 0.067, "gemini-3.1-flash-lite-image": 0.034, "gemini-2.5-flash-image": 0.039, "qa": 0.0003}
WIDTH = {"1:1": 512, "16:9": 1280, "4:3": 800}
QA_PROMPT = ("You are checking a photo for a language-learning website. Answer only JSON: "
             '{"ok": true|false, "problems": ["..."]}. '
             "Set ok=false ONLY for clear, noticeable defects on the main people or the "
             "foreground: a person with three or more arms or hands, a hand not attached to any body, a badly deformed hand or face, "
             "or clearly readable fake text or fake Chinese characters in the foreground. Ignore blank badges or cards, tiny blurry "
             "background details, distant signs, and numbers on buses or clocks.")


class Stop(Exception):
    pass


def post(url, key, body, timeout=180):
    req = urllib.request.Request(url, data=json.dumps(body).encode(), headers={"Content-Type": "application/json", "x-goog-api-key": key})
    with urllib.request.urlopen(req, timeout=timeout) as f:
        return json.load(f)


def gemini_image(model, key, prompt, refs, aspect):
    parts = [{"text": prompt}] + [{"inlineData": {"mimeType": "image/webp", "data": base64.b64encode((OUT / f"{r}.webp").read_bytes()).decode()}} for r in refs]
    cfg = {"responseModalities": ["IMAGE"], "imageConfig": {"aspectRatio": aspect}}
    if model == "gemini-3.1-flash-image":
        cfg["imageConfig"]["imageSize"] = "1K"
    j = post(API + model + ":generateContent", key, {"contents": [{"parts": parts}], "generationConfig": cfg})
    for c in j.get("candidates", []):
        for p in c.get("content", {}).get("parts", []):
            if "inlineData" in p:
                return base64.b64decode(p["inlineData"]["data"])
    raise RuntimeError("Không có ảnh trong phản hồi")


def imagen(model, key, prompt, aspect):
    j = post(API + model + ":predict", key, {"instances": [{"prompt": prompt}], "parameters": {"sampleCount": 1, "aspectRatio": aspect, "personGeneration": "allow_adult"}})
    preds = j.get("predictions") or []
    if not preds or "bytesBase64Encoded" not in preds[0]:
        raise RuntimeError("Imagen không trả ảnh (có thể bị bộ lọc an toàn chặn)")
    return base64.b64decode(preds[0]["bytesBase64Encoded"])


def qa_check(key, raw):
    small = Image.open(io.BytesIO(raw)).convert("RGB"); small.thumbnail((768, 768))
    buf = io.BytesIO(); small.save(buf, "JPEG", quality=85)
    body = {"contents": [{"parts": [{"text": QA_PROMPT}, {"inlineData": {"mimeType": "image/jpeg", "data": base64.b64encode(buf.getvalue()).decode()}}]}],
            "generationConfig": {"responseMimeType": "application/json", "temperature": 0}}
    for m in QA_MODELS:
        try:
            j = post(API + m + ":generateContent", key, body, timeout=60)
            txt = j["candidates"][0]["content"]["parts"][0]["text"]
            r = json.loads(re.search(r"\{.*\}", txt, re.S).group(0))
            ok = bool(r.get("ok")); return ok, ([] if ok else (r.get("problems") or []))
        except urllib.error.HTTPError as e:
            if e.code == 404:
                continue
            return True, [f"không kiểm tra được (HTTP {e.code})"]
        except Exception as e:
            return True, [f"không kiểm tra được ({e})"]
    return True, ["không có model kiểm tra"]


def save(raw, key, aspect):
    im = Image.open(io.BytesIO(raw)).convert("RGB")
    w = WIDTH.get(aspect, 800)
    if im.width > w:
        im = im.resize((w, round(im.height * w / im.width)), Image.LANCZOS)
    im.save(OUT / f"{key}.webp", "WEBP", quality=80, method=6)


def write_index(items):
    idx = {}
    for it in items:
        f = OUT / f'{it["key"]}.webp'
        if f.exists():
            idx[it["key"]] = f"{f.name}?v={hashlib.md5(f.read_bytes()).hexdigest()[:8]}"
    (OUT / "index.json").write_text(json.dumps(idx, indent=0), encoding="utf-8")
    return len(idx)


def handle_http(e, where):
    msg = e.read().decode(errors="ignore")
    if e.code == 402:
        raise Stop("Hết tiền trả trước (prepay credits) của khoá Gemini. Nạp thêm ở https://ai.studio/projects rồi chạy lại.")
    if e.code == 429:
        if "limit: 0" in msg:
            raise Stop(f"{where}: model này không có lượt ở gói hiện tại (cần bật thanh toán).")
        m = re.search(r'"retryDelay":\s*"(\d+)', msg)
        return ("wait", int(m.group(1)) + 2 if m else 30)
    if e.code == 404:
        return ("next", 0)
    return ("fail", f"HTTP {e.code} {msg[:300]}")


def draw(it, key, state):
    """Vẽ một tranh, trả về (raw, model)."""
    if it["refs"]:
        chain, fn = REF_MODELS, lambda m: gemini_image(m, key, it["prompt"], it["refs"], it["aspect"])
    else:
        chain = CHEAP_MODELS + REF_MODELS
        fn = lambda m: imagen(m, key, it["prompt"], it["aspect"]) if m.startswith("imagen") else gemini_image(m, key, it["prompt"], [], it["aspect"])
    i = 0
    while i < len(chain):
        m = chain[i]
        if m in state["dead"]:
            i += 1; continue
        try:
            return fn(m), m
        except urllib.error.HTTPError as e:
            kind, val = handle_http(e, m)
            if kind == "wait":
                print(f"  chờ {val} giây vì giới hạn tốc độ…"); time.sleep(val); continue
            if kind == "next":
                print(f"  không dùng được {m}, chuyển model khác"); state["dead"].add(m); i += 1; continue
            print(f"  {m}: {val}"); i += 1
        except RuntimeError as e:
            print(f"  {m}: {e}"); i += 1
    raise RuntimeError("không model nào vẽ được")


def main():
    items = json.loads(LIST.read_text(encoding="utf-8"))
    OUT.mkdir(parents=True, exist_ok=True)
    qa_log = json.loads(QA_FILE.read_text(encoding="utf-8")) if QA_FILE.exists() else {}
    redo = os.environ.get("REDO", "").strip()
    if redo:
        keys = None if redo == "all" else {x.strip() for x in redo.split(",")}
        for it in items:
            f = OUT / f'{it["key"]}.webp'
            if f.exists() and (keys is None or it["key"] in keys):
                f.unlink()
    if os.environ.get("AUDIT", "").strip() in ("1", "true"):
        try:
            req = urllib.request.Request("https://generativelanguage.googleapis.com/v1beta/models?pageSize=1000", headers={"x-goog-api-key": os.environ.get("GEMINI_API_KEY", "")})
            ms = json.load(urllib.request.urlopen(req, timeout=60)).get("models", [])
            print("Model ảnh/giọng đọc dùng được: " + ", ".join(m["name"].split("/")[-1] + "[" + "/".join(m.get("supportedGenerationMethods", [])) + "]" for m in ms if re.search(r"image|imagen|tts|lite", m["name"])))
        except Exception as e:
            print("Không liệt kê được model:", e)
        key = os.environ.get("GEMINI_API_KEY", "").strip(); bad = []
        for it in items:
            f = OUT / f'{it["key"]}.webp'
            if not f.exists():
                continue
            ok, problems = qa_check(key, f.read_bytes())
            qa_log[it["key"]] = dict(qa_log.get(it["key"], {}), ok=ok, problems=problems)
            print(("✓ " if ok else "⚠ ") + it["key"] + ("" if ok else ": " + "; ".join(problems)))
            if not ok:
                bad.append(it["key"])
        QA_FILE.write_text(json.dumps(qa_log, ensure_ascii=False, indent=1), encoding="utf-8")
        print(f"Kiểm tra xong, chi phí ước tính {len(items) * PRICE['qa']:.3f} USD. Cần xem lại: " + (", ".join(bad) or "không có"))
        return
    todo = [it for it in items if not (OUT / f'{it["key"]}.webp').exists()]
    print(f"Tổng {len(items)} tranh, cần vẽ {len(todo)}.")
    key = os.environ.get("GEMINI_API_KEY", "").strip()
    if todo and not key:
        print("::error::Chưa có secret GEMINI_API_KEY."); write_index(items); sys.exit(1)
    state, cost, made, flagged = {"dead": set()}, 0.0, 0, []
    try:
        for it in todo:
            if any(not (OUT / f"{r}.webp").exists() for r in it["refs"]):
                print(f"Bỏ qua {it['key']}: chưa có chân dung tham chiếu"); continue
            best = None
            for attempt in (1, 2):
                try:
                    raw, model = draw(it, key, state)
                except RuntimeError as e:
                    print(f"✗ {it['key']}: {e}"); break
                cost += PRICE.get(model, 0.067)
                ok, problems = qa_check(key, raw); cost += PRICE["qa"]
                best = (raw, model, ok, problems)
                if ok:
                    break
                print(f"  lần {attempt} chưa đạt: {'; '.join(problems)}" + (" → vẽ lại" if attempt == 1 else ""))
            if best:
                raw, model, ok, problems = best
                save(raw, it["key"], it["aspect"]); made += 1
                qa_log[it["key"]] = {"model": model, "ok": ok, "problems": problems}
                if not ok:
                    flagged.append(it["key"])
                print(f"{'✓' if ok else '⚠'} {it['key']} ({model})")
                time.sleep(float(os.environ.get("PAUSE", "1")))
    except Stop as e:
        print(f"::error::{e}")
        QA_FILE.write_text(json.dumps(qa_log, ensure_ascii=False, indent=1), encoding="utf-8")
        print(f"Đã vẽ {made} tranh, chi phí ước tính {cost:.2f} USD, tổng có {write_index(items)} tranh."); sys.exit(1)
    QA_FILE.write_text(json.dumps(qa_log, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"Đã vẽ thêm {made} tranh, chi phí ước tính {cost:.2f} USD, tổng có {write_index(items)} tranh.")
    if flagged:
        print("::warning::Cần người xem duyệt: " + ", ".join(flagged))


if __name__ == "__main__":
    main()
