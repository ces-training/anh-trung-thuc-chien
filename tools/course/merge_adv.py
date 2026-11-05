"""Ghép các file phần tools/course/parts/<tuần>/d1..d5.json thành tools/course/<tuần>.json (tuần nâng cao),
đưa gloss của từng ngày vào tools/vendor/zh-gloss.json. Chạy: python3 tools/course/merge_adv.py zh-h4-1 en-b2-1"""
import json, os, sys
D = os.path.dirname(os.path.abspath(__file__)); V = os.path.join(D, "..", "vendor")
plan = json.load(open(os.path.join(D, "plan-adv.json"), encoding="utf-8"))
gp = os.path.join(V, "zh-gloss.json"); gloss = json.load(open(gp, encoding="utf-8")); add = 0
for wk in sys.argv[1:]:
    P = plan[wk]; days = []; imgs = []; newWords = []
    for n in range(1, 6):
        d = json.load(open(os.path.join(D, "parts", wk, f"d{n}.json"), encoding="utf-8"))
        for k, v in d.pop("gloss", {}).items():
            if k not in gloss: gloss[k] = v; add += 1
            if "(tên)" not in str(v[2]) and k not in newWords: newWords.append(k)   # từ mới ngoài thẻ (vd. 报价): cũng hiện bính âm
        d["adv"] = True; days.append(d)
    cast = [{k: v for k, v in c.items()} for c in P["cast"]]
    W = {"lang": P["lang"], "week": 1, "demo": True, "adv": True, "level": P["level"], "track": P["track"], "title": P["title"], "cando": P["cando"], "story": P["story"],
         "cast": cast, "days": days,
         "newScenes": [{"key": d["scene"]["img"], "prompt": d["scene"].get("imgPrompt", "")} for d in days], "newImages": []}
    if P["lang"] == "zh": W["pinyin"] = "new"; W["newWords"] = newWords
    json.dump(W, open(os.path.join(D, wk + ".json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(wk, "đã ghép", len(days), "ngày")
json.dump(gloss, open(gp, "w", encoding="utf-8"), ensure_ascii=False)
print("thêm", add, "từ vào zh-gloss.json")
