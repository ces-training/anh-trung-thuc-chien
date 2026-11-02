# Course data schema (one file per language per week)

Files: `course/zh-w1.json`, `course/zh-w2.json`, `course/en-w1.json`, `course/en-w2.json`.
All learner-facing explanations are in **Vietnamese**. Target-language text in Chinese (simplified) or English.
Pinyin fields (`py`) use tone marks (nǐ hǎo) and apply ONLY to zh files; omit `py` keys in en files.
Every array must be non-empty unless marked optional. Keep JSON valid UTF-8, no comments.

```jsonc
{
  "lang": "zh",                 // "zh" | "en"
  "week": 1,
  "title": "Chào hỏi, làm quen, gia đình",   // Vietnamese week title
  "cando": "Chào hỏi, giới thiệu tên, quốc tịch, tuổi và gia đình", // Vietnamese, one line
  "cast": [                     // recurring characters of the week's story (max 6)
    { "key": "liuxing", "name": "刘星", "py": "Liú Xīng", "vi": "cậu con trai 12 tuổi, nghịch ngợm", "look": "English visual description for an illustrator: a 12-year-old Chinese boy, short spiky black hair, red hoodie" }
  ],
  "days": [                     // exactly 5 days: Thứ 2..Thứ 6
    {
      "id": "w1-thu-2",          // w{week}-thu-{2..6}
      "label": "Thứ 2",
      "title": "Chào hỏi, cảm ơn, tạm biệt",       // Vietnamese
      "desc": "Một câu tiếng Việt mô tả hôm nay học gì",
      "rule": "1–2 câu tiếng Việt: điểm cần nhớ nhất của ngày (dùng cho thẻ quy tắc)",

      "cards": [                 // 8–14 flashcards: every NEW word/phrase of the day
        { "w": "你好", "py": "nǐ hǎo", "m": "xin chào", "ex": "你好！我叫刘星。", "expy": "Nǐ hǎo! Wǒ jiào Liú Xīng.", "exm": "Xin chào! Tôi tên là Lưu Tinh.", "n": "Ghi nhớ ngắn: cách dùng / bẫy hay gặp / thanh điệu", "img": "wave" }
        // "img": optional concept key for a photo. Use ONLY for concrete, picturable things/situations.
        // Prefer existing keys: wave handshake name student teacher work vietnam china engineer calc sales designer manager
        // colleague team company card email home city from where uk morning new repeat role cart bye thanks polite
        // me you she person what question is also no back
        // or invent a new lowercase key (e.g. "dad", "mom", "breakfast", "clock") and add it to "newImages" below.
      ],

      "scene": {                 // the short "film" scene of the day, rewritten as an original dialogue (6–10 lines)
        "setting": "Vietnamese: where/when/who (1–2 sentences)",
        "img": "home-gift",      // key for the scene image (unique per day, lowercase, a–z0–9-)
        "imgPrompt": "English illustrator brief of the moment, naming cast keys present, e.g. 'liuxing and xiadonghai in a living room, the stepdad offers a wrapped gift, the boy hesitates'",
        "lines": [ { "who": "夏东海", "t": "你好！你是刘星吗？", "py": "Nǐ hǎo! Nǐ shì Liú Xīng ma?", "vi": "Chào cháu! Cháu là Lưu Tinh à?" } ]
      },

      "patterns": [              // 2–4 grammar/sentence patterns of the day
        { "t": "Câu chữ 是: A 是 B", "f": [["我", "是", "刘星"]], "ex": [["我是学生。", "Tôi là học sinh."]], "bad": "我是叫刘星。", "good": "我叫刘星。", "why": "Vietnamese explanation" }
        // f = formula rows; each row 2–4 chips; the 2nd chip is highlighted as the key element.
      ],

      "vocab":   [ MC, ... ],    // 6–8 items (from "Bài tập từ vựng")
      "grammar": [ MC or TYPE, ... ], // 5–7 items (from "Bài tập hiểu mẫu câu, ngữ pháp")
      "listen":  [ MC with "audio", ... ], // 5–7 items (from "Bài tập nghe hiểu"); "audio" = target-language text to be spoken
      "hsk":     [ MC (audio optional), ... ], // 4–5 items (from "Bài dạng HSK"); en: TOEIC/Cambridge-style equivalent

      "shadow": [                // 6–8 lines to listen & repeat (from "Bài tập luyện thanh")
        { "t": "你好", "py": "nǐ hǎo", "focus": "Vietnamese: what to pay attention to (tone sandhi, stress...)" }
      ],

      "dialog": {                // learner role-play with a partner (from "Bài tập hội thoại"), 4–6 turns
        "title": "Vietnamese situation title",
        "partner": "夏东海",      // who speaks to the learner (a cast name)
        "turns": [
          { "ai": "你好！你是刘星吗？", "py": "Nǐ hǎo! Nǐ shì Liú Xīng ma?", "vi": "Chào cháu! Cháu là Lưu Tinh à?",
            "model": "是，我是刘星。", "mpy": "Shì, wǒ shì Liú Xīng.", "accept": ["是，我是刘星。", "我是刘星。", "是。"],
            "frame": "是，我是___。", "hint": "Vietnamese hint" }
        ]
      },

      "reading": {               // optional (from "Bài đọc hiểu")
        "text": "你好！我叫刘星。…", "py": "…", "vi": "Vietnamese translation",
        "qs": [ MC, ... ]        // 3–5
      }
    }
  ],
  "newImages": [                 // concept photos needed that are NOT in the existing key list (max 12 per file, concrete only)
    { "key": "dad", "prompt": "English photo brief: a smiling Vietnamese father in his 40s at home" }
  ]
}
```

MC item:
`{ "q": "Vietnamese question (may quote target text)", "opts": ["…","…","…"], "a": 0, "why": { "1": "why option 1 is wrong (Vietnamese)", "2": "…" }, "audio": "optional target-language text to play", "line": null }`
- 2–4 options, `a` = index of correct option, `why` must explain EVERY wrong option (keys are wrong indexes as strings).
- Put target-language text in options when testing recognition (e.g. ["再见","谢谢","你好"]).

TYPE item (only in `grammar`; use sparingly, short answers):
`{ "k": "type", "q": "Vietnamese prompt, e.g. 'Điền vào chỗ trống: 我___刘星。(Tôi tên là Lưu Tinh.)'", "model": "叫", "accept": ["叫", "jiao"], "why": "Vietnamese rule shown when wrong" }`
- For zh, `accept` must include the hanzi answer AND toneless pinyin without spaces (e.g. "jiao", "nihao").

Quality rules:
- Content must follow the sheet's topic, vocabulary and grammar for that day; do not introduce words beyond the day's list plus earlier days.
- Answers must be unambiguous. Explanations explicit: say exactly why a wrong option is wrong.
- Scenes are ORIGINAL short dialogues inspired by the sheet's scene description (do not copy copyrighted script text).
- No trailing commas; run `python3 course/validate.py course/<file>.json` until it prints OK.
