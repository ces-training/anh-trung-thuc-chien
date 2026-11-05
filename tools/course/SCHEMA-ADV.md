# Tuần nâng cao (Trung HSK3 → HSK4, Anh B2): khung dữ liệu

Hai tuần học thử: `zh-h4-1.json` (lộ trình Tiếng Trung · Nâng cao, người đã vững HSK3) và `en-b2-1.json` (lộ trình Tiếng Anh · Nâng cao B2+).
Giữ toàn bộ quy tắc trong `docs/QUY-TAC-TAO-BAI.md` và khung chung trong `SCHEMA.md`, `en-b1-1.json`, `zh-w5.json`, **trừ** những điểm ghi dưới đây.
Kiểm tra từng ngày: `python3 tools/course/check_adv.py <file> --day N` (N = 1..5). Chạy đến khi báo 0 lỗi.

## Khác biệt so với các tuần trước
1. **16 bài/ngày**, đi theo 4 bước:
   Nghe: T → Q → S → B → **Y (Nghe điền thông tin)** · Nói: C → P → I → **X (Nói dài 1–2 phút)** · Đọc: U → E → G → J → H · Viết: W → V.
   U, W, V đổi nội dung: U = từ gần nghĩa (Trung) / biến đổi từ (Anh); W = sắp xếp câu thành đoạn; V = viết theo dạng đề.
2. **Tiếng Trung: ẩn bính âm, chỉ hiện ở từ mới.** Dữ liệu VẪN ghi đủ bính âm (`py`, `expy`, `mpy`…) cho mọi câu: trang tự ẩn, chỉ hiện trên chữ thuộc thẻ từ của tuần, người học chạm vào từ để xem bính âm và nghĩa.
3. **Tiếng Trung: chỉ dùng chữ đã học** = chữ trong 600 từ HSK1–3 (`known-hsk3.json`) + thẻ từ các tuần đã có + thẻ từ của tuần này từ Thứ 2 đến hôm nay (`plan-adv.json`) + tên riêng. `check_adv.py` báo từng chữ ngoài vốn này. Cần chữ mới thì đổi cách nói; tên riêng ghi trong `gloss` với nghĩa có "(tên)".
4. Tiếng Anh: không cần `spell`. Thẻ từ có `w, ipa, m, ex, exm, n, img`. Nghĩa tiếng Việt viết tự nhiên; không cần `mEn`.
5. Mỗi ngày dùng ĐÚNG danh sách thẻ từ trong `plan-adv.json` (đúng thứ tự). Không thêm, không bớt.

## Các trường của một ngày (file phần: `tools/course/parts/<tuần>/dN.json`)
```jsonc
{
  "id": "h4-w1-thu-2",          // Trung: h4-w1-thu-{2..6}; Anh: b2-w1-thu-{2..6}
  "label": "Thứ 2", "title": "…", "desc": "…", "rule": "…",   // tiếng Việt
  "cards": [ … ],                // 11 (Trung) / 12 (Anh), đúng plan-adv.json
  "scene": { "setting": "…", "img": "scene-zh-fair-d1", "imgPrompt": "…", "lines": [ /* 8–10 câu */ ] },
  "patterns": [ /* 3 mẫu; Trung: ex = [chữ Hán, Việt, Anh]; Anh: ex = [Anh, Việt] */ ],
  "vocab":   [ /* 8 MC */ ], "grammar": [ /* 7: MC hoặc type */ ], "listen": [ /* 7 MC có audio */ ],
  "hsk":     [ /* 5: đúng dạng đề thật. Trung: HSK4 (听力 判断对错/对话, 阅读 选词填空, 书写 完成句子 dùng k:"order"). Anh: IELTS/TOEIC B2 */ ],
  "shadow":  [ /* 6 câu nhại: Trung {t, py, focus, en}; Anh {t, focus} */ ],
  "dialog":  { "title": "…", "partner": "…", "turns": [ /* 5 lượt, đủ trường như tuần trước */ ] },
  "reading": { "title": "…", "text": "…", "py": "…(Trung)", "vi": "…", "en": "…(Trung)", "qs": [ /* 5 MC */ ] },

  "near": [ /* U · 6 MC */ ],
  // Trung: từ gần nghĩa, dễ nhầm (以为/认为, 帮助/帮忙, 适合/合适…), câu điền: "q": "Chọn từ đúng: 这个价格对我们很___。(Giá này rất phù hợp với chúng tôi.)"
  //        opts là chữ Hán; why giải thích khác nhau về nghĩa và cách dùng (loại từ, kết hợp).
  // Anh:  biến đổi từ (word formation) kiểu IELTS/TOEIC: "q": "Chọn dạng đúng: The results were ___ better than expected. (significant)"
  //        opts: ["significantly","significant","significance"]; why giải thích loại từ cần dùng.

  "orderPara": [ /* W · 4 câu sắp xếp */
    { "k": "order", "q": "Sắp xếp thành đoạn văn đúng (HSK4 阅读 · 排列顺序)",
      "tokens": ["câu A (đúng thứ tự)", "câu B", "câu C"],   // 3–4 câu, ghi theo ĐÚNG thứ tự; trang tự xáo
      "explain": "tiếng Việt: dựa vào từ nối/đại từ nào để biết thứ tự (因为…所以, 但是, 这/它…; however, this, as a result…)",
      "vi": "dịch cả đoạn", "en": "(Trung) bản tiếng Anh của cả đoạn" }
  ],

  "notes": { /* Y · Nghe điền thông tin */
    "title": "Ghi chú: thông tin đơn hàng",          // tiếng Việt
    "lines": [ { "who": "小刘", "t": "…", "py": "…", "vi": "…", "en": "…" } ],   // 6–10 câu: một người nói hoặc hội thoại
    "form": [                                           // 5–6 ô
      // Anh: gõ đáp án ≤ 3 từ hoặc số (đúng kiểu IELTS Listening)
      { "label": "Number of stores in the first phase", "answer": "12", "accept": ["12", "twelve"], "why": "Ingrid nói: twelve stores in the first phase." },
      // Trung: chọn trong 3 phương án chữ Hán (không gõ)
      { "label": "Số lượng tối thiểu", "opts": ["一千个", "两千个", "五百个"], "a": 0, "why": { "1": "…", "2": "…" } }
    ]
  },

  "longturn": { /* X · Nói dài */
    "cue": "đề bằng ngôn ngữ đích (Anh: kiểu IELTS Speaking Part 2 cue card; Trung: đề nói 1 phút)",
    "cueVi": "đề tiếng Việt", "cuePy": "(Trung) bính âm của cue",
    "points": ["ý 1 cần nói", "ý 2", "ý 3", "ý 4"],     // ngôn ngữ đích (Trung có thêm "pointsVi")
    "pointsVi": ["…"],
    "prep": 60, "speak": [60, 120],                    // giây: chuẩn bị, nói tối thiểu–tối đa
    "model": "bài nói mẫu 120–180 từ (Anh) / 80–130 chữ Hán (Trung)", "modelPy": "(Trung)", "modelVi": "…",
    "useful": ["cụm hữu ích 1", "…"],                  // 5–8 cụm, ngôn ngữ đích
    "check": ["Tự chấm (tiếng Việt): Nói đủ 4 ý", "Dùng ít nhất 3 từ nối", "…"]   // 4–6 mục
  },

  "write": { /* V · Viết theo dạng đề, khung như tuần A2/B1 */
    "task": "…", "kind": "email" | "message" | "report" | "essay",
    "model": "…", "frame": "… ___ …", "gaps": ["…"], "free": [true, false],
    "hints": ["…"], "check": ["…"], "words": [min, max]   // Anh: số từ; Trung: số chữ Hán
  },
  "gloss": { "价格": ["jiàgé", "price", "giá cả"] }     // (Trung) MỌI thẻ từ + tên riêng mới; tên ghi nghĩa Việt có "(tên)"
}
```

## Câu trắc nghiệm, câu gõ (như tuần trước)
- MC: `q, opts (2–4, khác nhau), a, why` (why giải thích TỪNG đáp án sai, khoá là số dạng chuỗi). Trung: đáp án tiếng Việt thì thêm `optsEn`.
- Câu gõ (chỉ trong grammar): `{ "k": "type", "q", "model", "accept", "why" }`; Trung: `accept` gồm chữ Hán VÀ bính âm không dấu viết liền.
- Câu xếp (trong hsk của Trung, dạng 完成句子): `{ "k": "order", "q": "HSK4 书写 · 完成句子: xếp các từ thành câu", "tokens": ["从","这家工厂","进口","我们","产品"] → GHI ĐÚNG THỨ TỰ, "explain", "vi", "en" }`.
- Câu nghe dùng `audio` (văn bản sẽ được đọc). Tiếng Anh: hội thoại ghi "Woman: … Man: …".

## Nội dung
- Bối cảnh công sở, mạch truyện liền 5 ngày theo `plan-adv.json`. Đúng dàn nhân vật.
- Trình độ: Trung ≈ HSK4 (câu dài hơn, từ nối 虽然…但是, 不但…而且, 只要…就, 既然, 由于…), Anh ≈ B2 (câu phức, bị động, điều kiện, mệnh đề quan hệ, từ nối học thuật).
- Lời giải thích, gợi ý, phản hồi bằng tiếng Việt, luôn tích cực. Không dùng gạch ngang dài (—) trong câu tiếng Việt.
- Ảnh: `img` của thẻ chỉ dùng khoá có sẵn (xem `tools/image-list.json`) hoặc để trống; cảnh dùng khoá mới theo `plan-adv.json`.
