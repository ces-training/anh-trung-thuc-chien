"""Chuẩn bị ngữ liệu làm video trên Google Flow cho từng cảnh hội thoại.

Mỗi cảnh được chia thành các đoạn ngắn (mỗi đoạn <= ~7 giây lời nói, vì Flow/Veo làm clip 8 giây).
Mỗi đoạn có: ảnh khung đầu (ảnh cảnh đã có), câu lệnh dán vào Flow (mô tả + lời thoại), tên file cần lưu.
Kết quả: tools/flow-kit.json và ảnh khung đầu JPG 1280x720 trong tuan-1/flow/.
"""
import json, pathlib, re
from PIL import Image

ROOT = pathlib.Path(__file__).resolve().parent.parent
COURSE = ROOT / "tools" / "course"
IMG = ROOT / "tuan-1" / "img"
OUT = ROOT / "tuan-1" / "flow"
LANG = {"zh": "Mandarin Chinese (standard Putonghua, clear and slightly slow for learners)", "en": "English (clear, natural, slightly slow for learners)"}


def est(lang, text):
    n = len(re.sub(r"[\s，。！？、,.!?…]", "", text))
    return 0.6 + (0.28 * n if lang == "zh" else 0.075 * len(text))


def short_look(look):
    look = re.sub(r"^(A |a |An |an )?(realistic )?", "", look.strip())
    parts = [p.strip() for p in look.split(",")]
    return ", ".join(parts[:3])


def frame(key):
    OUT.mkdir(parents=True, exist_ok=True)
    src = IMG / f"{key}.webp"
    if not src.exists():
        return None
    im = Image.open(src).convert("RGB")
    w, h = im.size
    th = int(w * 9 / 16)
    if th <= h:
        top = (h - th) // 2; im = im.crop((0, top, w, top + th))
    else:
        tw = int(h * 16 / 9); left = (w - tw) // 2; im = im.crop((left, 0, left + tw, h))
    im = im.resize((1280, 720), Image.LANCZOS)
    dest = OUT / f"{key}.jpg"
    im.save(dest, "JPEG", quality=90)
    return f"flow/{key}.jpg"


def main():
    kit = []
    for f in sorted(p for p in COURSE.glob("*-w*.json") if re.match(r"(en|zh)-w\d+\.json$", p.name)):
        c = json.loads(f.read_text(encoding="utf-8")); L = c["lang"]
        looks = {m["name"]: short_look(m["look"]) for m in c.get("cast", [])}
        names = {m["key"]: m["name"] for m in c.get("cast", [])}
        fix = lambda txt: re.sub(r"\b(" + "|".join(map(re.escape, sorted(names, key=len, reverse=True))) + r")\b", lambda mm: names[mm.group(1)], txt) if names else txt
        for d in c["days"]:
            sc = d["scene"]; lines = sc["lines"]
            clips, cur, t = [], [], 0.0
            for i, ln in enumerate(lines):
                e = est(L, ln["t"])
                if cur and t + e > 7.0:
                    clips.append(cur); cur, t = [], 0.0
                cur.append(i); t += e
            if cur: clips.append(cur)
            base = f'{L}-{d["id"]}'
            item = {"key": base, "lang": L, "week": c["week"], "day": d["label"], "title": d["title"], "setting": sc["setting"],
                    "image": frame(sc["img"]), "imageKey": sc["img"], "clips": []}
            for ci, idxs in enumerate(clips):
                who = []
                for i in idxs:
                    w = lines[i]["who"]
                    if w not in who: who.append(w)
                dia = "\n".join(f'- {lines[i]["who"]} ({looks.get(lines[i]["who"], "a colleague")}) says: "{lines[i]["t"]}"' for i in idxs)
                prompt = (f"Use the uploaded image as the first frame and keep the same people, faces, clothes and room. "
                          f"Realistic 8-second video, steady camera, natural light, natural lip-sync and gestures. "
                          f"Scene: {re.sub(r'^Photo (of|in) ', '', fix(sc['imgPrompt'])).replace('No text in image.', '').strip()}\n"
                          f"The characters speak in {LANG[L]}, in this exact order, with a short natural pause between lines:\n{dia}\n"
                          f"No subtitles, no on-screen text, no background music, no other speech.")
                item["cast"] = [{"name": m["name"], "key": m["key"], "look": m["look"]} for m in c.get("cast", []) if any(l["who"] == m["name"] for l in lines)]
                item["clips"].append({"file": f"{base}-{ci + 1}.mp4", "lines": idxs, "speakers": who, "prompt": prompt,
                                      "say": [{"who": lines[i]["who"], "t": lines[i]["t"], "py": lines[i].get("py", ""), "vi": lines[i]["vi"]} for i in idxs]})
            kit.append(item)
    (ROOT / "tools" / "flow-kit.json").write_text(json.dumps(kit, ensure_ascii=False, indent=1), encoding="utf-8")
    print(len(kit), "cảnh,", sum(len(k["clips"]) for k in kit), "đoạn video")


if __name__ == "__main__":
    main()
