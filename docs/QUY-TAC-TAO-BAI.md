# Quy tắc tạo bài tập · Anh – Trung Thực Chiến

Áp dụng cho mọi tuần, mọi bài, cả tiếng Trung lẫn tiếng Anh. Trước khi giao một tuần mới, phải đi hết danh sách kiểm tra ở mục 9. Bản dựng tự chạy `course/check_rules.py`; còn lỗi là dừng, không xuất bản.

## 1. Định hướng chung
1. **Người học:** sinh viên và người đi làm. Bối cảnh là công sở, du học, giao tiếp công việc; không dùng bối cảnh gia đình trẻ con. Mục tiêu: giao tiếp công việc thành thạo, rồi thi chứng chỉ thật (HSK, TOEIC, IELTS).
2. **Hai ngôn ngữ song song:** mỗi tuần có `zh-wN.json` và `en-wN.json`, cùng chủ đề, cùng số ngày (Thứ 2 → Thứ 6).
3. **Nội dung:** lấy từ sheet "Khung chương trình 16 tuần". Giữ từ vựng và ngữ pháp của sheet, chuyển sang bối cảnh công sở.
4. **Chi phí:**
   - Chưa tạo hình hay giọng Gemini mới khi chị Duyên chưa duyệt.
   - Dùng lại ảnh có sẵn (cắt ghép, dùng tên khác qua `IMG_ALIAS`) và giọng máy.
   - Khi được duyệt: ảnh dùng flash-lite và tự kiểm lỗi; giọng dùng 3.8 flash TTS bản miễn phí, dự phòng flash-lite TTS.
5. **Tên nhân vật:** dùng đúng dàn nhân vật của tuần. Tên riêng phải có trong từ điển tra nhanh, ghi "(tên)".

## 2. Lộ trình một ngày
**Tiếng Trung đi đúng thứ tự Nghe → Nói → Nhận mặt chữ và đọc → Viết:**

| Bước | Bài (mã) | Hiển thị |
|---|---|---|
| 1 · Nghe | Thẻ nghe (T) → Nghe chọn nghĩa (Q) → Nghe cảnh (S) → Nghe hiểu (B) | Tranh, âm thanh, **chữ Hán luôn kèm bính âm**, nghĩa Anh · Việt. Trọng tâm là nghe, nhưng không ẩn chữ Hán. |
| 2 · Nói | Nhại theo (C) → Mẫu câu (P) → Hội thoại (I) | **Chữ Hán kèm bính âm** (bính âm nằm trên chữ). Rê chuột hoặc chạm vào từ để xem bính âm, nghĩa tiếng Anh, nghĩa tiếng Việt. |
| 3 · Nhận mặt chữ và đọc | Nhận mặt chữ (U) → Từ vựng (E) → Ngữ pháp (G) → Đọc (J) → Dạng đề HSK (H) | Chữ Hán là chính, **luôn có bính âm** (cả Mức 1 và Mức 2, cả đáp án). Chữ Hán ở đâu cũng tra được nghĩa. |
| 4 · Viết chữ | Đếm nét (W) → Hướng dẫn viết (V) | Chính tả viết tay để trong workbook. |

**Tiếng Anh:** T → S → P → E → G → B → C → I → H → J.

**Quy định chung:** tất cả bài đều mở (`LOCK_ORDER = false`), học viên tự chọn bài. Thứ tự trên chỉ là gợi ý.

## 3. Nội dung
1. **Chỉ dùng chữ và từ đã học.** Bài đọc, câu hỏi đọc, câu hội thoại và cặp chữ đếm nét chỉ được dùng chữ có trong thẻ từ từ Tuần 1 đến hôm nay, cộng với tên riêng. `check_rules.py` báo LỖI nếu sai.
2. **Đủ dữ liệu cho từng câu:**
   - Mọi câu tiếng Trung đều có bính âm, nghĩa tiếng Anh và nghĩa tiếng Việt.
   - Mọi thẻ từ có: `w, py, m, mEn, ex, expy, exm, exEn, n`, và `img` nếu có tranh.
   - **Song ngữ, tiếng Anh trước:** chỗ nào có nghĩa tiếng Việt thì phải có nghĩa tiếng Anh, hiện tiếng Anh trước (đậm), tiếng Việt sau (nhạt). Trường dữ liệu: cảnh `en`; hội thoại `en` (lời đối tác) và `men` (câu mẫu); mẫu câu `ex[i][2]`; bài đọc `en`; nhại theo `en`; trắc nghiệm có đáp án tiếng Việt thì có `optsEn`; cặp đếm nét `aen, ben`; hướng dẫn viết `en`.
   - **Chữ Hán luôn kèm bính âm** ở mọi bài, mọi mức: câu hỏi, đáp án, phản hồi, gợi ý. Chữ Hán trong câu tiếng Việt cũng có bính âm (trừ khi đã viết bính âm trong ngoặc ngay sau).
3. **Từ điển tra nhanh:** mọi từ trong thẻ phải có trong `vendor/zh-gloss.json` dạng `[bính âm, nghĩa Anh, nghĩa Việt]`.
4. **Hội thoại:** mỗi lượt có `ai, py, vi, en, model, mpy, men, accept, hint`, có `frame` cho Mức 1. `accept` phải gồm cả bính âm không dấu.
5. **Nhại theo:** mỗi câu có `t, py, focus, en` (`en` để trống chỉ với câu luyện âm). Dòng Chú ý nói rõ chỗ khó: thanh điệu, âm cuối, ghép âm.
6. **Mẫu câu:** có `t` (tên mẫu, có công thức), `f` (dòng đầu là ví dụ chia ô, ô thứ 2 là phần chính), `ex` (1–3 câu, mỗi câu `[chữ Hán, nghĩa Việt, nghĩa Anh]`), `bad`, `good`, `why`.
7. **Bài đọc:** có `text, py, en, vi, qs`. Câu hỏi hỏi đúng thông tin trong bài, mỗi đáp án sai có `why`.
8. **Câu trắc nghiệm:**
   - 2–4 đáp án, không trùng nhau.
   - Mỗi đáp án sai có giải thích riêng, chỉ ra đáp án đó là gì và vì sao không khớp.
9. **Bước 4:**
   - **Đếm nét (W):** 4 cặp mỗi ngày. Chữ thứ nhất có trong bài; chữ thứ hai trông giống và **khác số nét**. Kèm ghi chú bộ phận khác nhau, ví dụ "吗 = 口 + 马".
   - **Hướng dẫn viết (V):** 4 chữ mỗi ngày, có cách nhớ (`k`) và ít nhất 2 quy tắc viết (`r`). Câu "Chữ có N nét" tự sinh từ dữ liệu nét.
10. **Câu tương tự để làm lại:** bài nào sinh câu tự động (Q, U) thì tạo sẵn 2 phương án `alts`. Bài soạn tay (B, E, G, J) nên soạn thêm 1–2 câu cùng dạng; chưa có thì trang xáo lại đáp án.

## 4. Tương tác (mọi bài)
1. **Tự phát âm thanh:**
   - Câu, thẻ, cảnh mới hiện ra là tự phát một lần.
   - Công tắc "🔊 Tự phát" mặc định **bật**, trang nhớ lựa chọn của từng học viên.
   - Bài đọc không tự phát; học viên bấm "Nghe cả đoạn".
2. **Đúng ngay:** tô xanh, đọc lại đáp án, **sau 1,2 giây tự sang câu tiếp** (`AUTO_MS`).
3. **Sai lần đầu:**
   - Không bắt sửa ngay. Ghi "Chưa đúng, không sao!", **hiện đáp án đúng 2 giây** (`SHOW_ANS_MS`), đọc đáp án, rồi sang câu tiếp.
   - Câu đó vào kho ôn; ô tiến độ chuyển màu vàng.
4. **Cuối bài:** làm lại **câu tương tự** cho mỗi câu đã sai, có nhãn "🔁 Làm lại câu tương tự". Sai tiếp thì **mới hiện gợi ý và giải thích**, rồi nút "Đã hiểu, làm câu tương tự →". Lặp đến khi đúng, tối đa 4 vòng (`MAX_ROUNDS`).
5. **Luôn có lối đi tiếp,** không chỗ nào bắt học viên mắc kẹt:
   - nút "Bỏ qua, câu tiếp →" hoặc "Câu tiếp →";
   - "Đã hiểu, đi tiếp →" ở bài mẫu câu;
   - "Dùng câu mẫu, đi tiếp →" ở bài hội thoại.
6. **Xong bài:** chỉ hiện nút "Bài tiếp →", không tự mở bài sau.
7. **Dạng đề HSK:** như thi thật, không tự chuyển, không làm lại.

## 5. Từng dạng bài
- **T · Thẻ:**
  - Tranh, âm thanh, chữ Hán kèm bính âm.
  - Mặt sau có nghĩa Anh rồi Việt, câu ví dụ có bính âm và nghĩa Anh, Việt, ghi nhớ. Có nút lưu vào kho ôn.
- **Q · Nghe chọn nghĩa:** âm tự phát; chọn tranh và nghĩa; mỗi đáp án một tranh.
- **S · Nghe cảnh:**
  - Tự phát cả cảnh. Chữ Hán luôn hiện; có công tắc bính âm và nghĩa (Anh · Việt).
  - Video Google Flow: giữ tiếng gốc, phụ đề dưới khung hình khớp từng câu. Cần lời thoại đúng thứ tự từ chị Duyên.
- **B · Nghe hiểu:** câu nghe tự phát; đáp án chữ Hán có bính âm, đáp án tiếng Việt có tiếng Anh ở trên; có tranh cho đáp án hoặc ảnh cảnh.
- **C · Nhại theo:**
  - Mẫu tự phát. Nghe xong, nút 🎤 hiện ra. Có "Nghe lại mẫu" và "Nghe chậm".
  - Máy chấm từng chữ, tô màu: xanh đúng, vàng sai thanh, xanh dương sai âm, gạch đứt là thiếu. Kèm mẹo sửa âm.
  - Đạt từ 70% thì tự sang câu tiếp. Có "Nghe giọng bạn" và "Bỏ qua".
- **P · Mẫu câu:** 3 bước:
  1. Xem và nghe mẫu: ô vàng là phần chính.
  2. Tự lắp câu: chạm ô chữ.
  3. Câu nào đúng?: chọn giữa `good` và `bad`, rồi đọc `why`.
- **I · Hội thoại:**
  - Lời đối tác tự phát. Học viên trả lời bằng 🎤 hoặc gõ; tiếng Trung chấp nhận bính âm không dấu.
  - Có 💡 Gợi ý 2 bậc (ý chính và khung câu, rồi đáp án mẫu) và nút 🔊 Nghe đáp án mẫu.
  - Ghi âm từng lượt; cuối bài nghe lại cả cuộc hội thoại.
  - Đổi vai: Vai 1 trả lời, Vai 2 hỏi theo nhiệm vụ. Nhận xét thanh điệu và phát âm.
- **U · Nhận mặt chữ:** xen kẽ 2 kiểu: nhìn chữ to (có bính âm) chọn nghĩa Anh · Việt, hoặc đọc nghĩa chọn chữ (đáp án chữ có bính âm). Không dùng kiểu "nghe âm chọn chữ" vì bính âm trên đáp án làm lộ đáp án.
- **E, G · Từ vựng, ngữ pháp:**
  - Có tranh theo đáp án, không có thì dùng ảnh cảnh.
  - Tiếng Trung Mức 1: bài gõ đổi thành chọn hoặc xếp ô có bính âm.
- **J · Đọc:**
  - 3 bước: nghe cả đoạn (tô sáng câu đang đọc) → đọc → câu hỏi.
  - Bính âm luôn bật sẵn, có công tắc tắt để học viên tự thử đọc.
  - Tra từ có bính âm, nghĩa Anh, nghĩa Việt và nút nghe. Bản dịch có tiếng Anh trước, tiếng Việt sau.
- **H · Dạng đề HSK:** đúng dạng đề thật; điểm tính theo lần đầu.
- **W · Đếm nét:** ô chữ có "Xem từng nét" đếm theo 1, 2, 3…; câu chọn chữ hỏi "Chữ nào có N nét?", dưới từng chữ có bính âm, nghĩa và nút "Đếm nét".
- **V · Hướng dẫn viết:**
  - Đi lần lượt Xem thứ tự nét → Tô nét (sai 2 lần thì nét đúng nháy lên) → Tự viết (có nút Gợi ý) → Kiểm tra (tính giờ, không gợi ý).
  - Tự chuyển bước, tự chuyển chữ, có nút "Ở lại". Cuối có Kết quả.

## 6. Phản hồi và lời nhắc
1. **Luôn tích cực:**
   - Nói phần đúng trước, rồi chỉ một hai chỗ cần chỉnh.
   - Không dùng lời chê ("sai rồi", "kém").
   - Sai lần đầu: "Chưa đúng, không sao!". Ở lần làm lại: "Gần được rồi!".
2. **Đầu mỗi bài có 3 khung:**
   - "Cách làm" (3 bước);
   - "Quy tắc cần nhớ";
   - "Làm sao cho hiệu quả" (2–3 mẹo riêng cho dạng bài, thêm mẹo cho tiếng Trung).
3. **Khuyến nghị trình duyệt:**
   - Hiện ở màn hình "Chạm để bắt đầu" (mỗi lần học), đầu các bài nghe, nói, đọc, và trong phòng Hướng dẫn.
   - Máy tính, Android: Chrome hoặc Edge. iPhone, iPad: Safari.
   - Cảnh báo khi mở trong Zalo, Facebook hoặc Messenger, khi dùng Firefox, hoặc khi máy thiếu giọng tiếng Trung.
4. **Chấm phát âm chỉ là ước lượng,** máy chấm qua chữ nó nghe được. Không thay giáo viên; lỗi nặng chuyển cho lớp nhóm.

## 7. Hiển thị
1. **Cỡ chữ:**
   - Chữ thường 18px, chữ phụ không dưới 14px.
   - Chữ Hán trong câu nhại theo, đọc, mẫu câu từ 22px trở lên. Bính âm trên chữ từ 11px trở lên.
2. **Tranh:** câu hỏi nào cũng có tranh. Thứ tự ưu tiên: tranh riêng của câu → tranh của từ đáp án → tranh cho từng đáp án → ảnh cảnh của ngày.
3. **Màn hình nhỏ:** chạy tốt ở 390px, không có thanh cuộn ngang. Nút bấm đủ lớn cho ngón tay.

## 8. Kỹ thuật và xuất bản
1. **Dữ liệu và mã nguồn** (tất cả trong repo):
   - Dữ liệu tuần: `tools/course/{zh,en}-wN.json`. Tuần học thử của lộ trình khác: `tools/course/zh-w5.json`, `en-a2-1.json`, `en-b1-1.json` (có `"demo": true`, mỗi tuần một ngôn ngữ).
   - Khuôn trang (giao diện, mã chạy bài): `tools/build/page-template.html`. Sửa giao diện ở đây, không sửa thẳng `tuan-1/index.html`.
   - Dữ liệu bước 4: `tools/vendor/stroke-pairs.json`, `tools/vendor/write-guide.json`, `tools/vendor/hzdata/*.json` (lấy từ hanzi-writer-data).
   - Từ điển: `tools/vendor/zh-gloss.json`. Bính âm từng chữ: `tools/vendor/zhpy.json` (sinh bằng pinyin-pro).
2. **Dựng trang:** `python3 tools/build2.py` → `tuan-1/index.html`. Bản dựng tự chạy `tools/course/check_rules.py`; còn LỖI thì dừng.
3. **Kiểm thử trước khi giao:**
   - `node tools/t20.js`: tất cả bài, 2 ngôn ngữ, 2 mức, chạy qua máy chủ http; câu đầu mỗi bài cố ý trả lời sai để chắc không có câu nào kẹt.
   - `node tools/t20.js --shots`: chụp màn hình máy tính (1280) và điện thoại (390) vào `tools/shots/`, báo trang nào có thanh cuộn ngang.
   - Hướng dẫn viết chữ Hán (V) cần vẽ nét bằng tay: máy chỉ kiểm tra mở được 4 bước, phải thử tay trên điện thoại.
4. **Xuất bản:**
   - `python3 tools/deploy.py "nội dung thay đổi" [--test]`: dựng, kiểm tra, rồi mới đẩy.
   - Bản xem trong Claude: artifact JKSzCSN4FVjwQhXtu9L7wv.
   - Trang thật: repo `ces-training/anh-trung-thuc-chien`, thư mục `tuan-1/`.
   - **Chỉ đẩy lên khi kết nối GitHub đang là tài khoản ces-training** (`deploy.py` tự dừng nếu kho trỏ chỗ khác). Tài khoản ivythaibinh dành cho Lingo Cub và Rung Chuông Vàng. Nếu kết nối đang sai tài khoản, báo chị và chỉ cách đổi; không tự đổi, không cấp quyền chéo.
   - Commit mặc định có `[skip ci]` để GitHub không tự tạo ảnh hoặc giọng. Chỉ thêm `--ci` khi chị Duyên đã duyệt danh sách tranh, giọng mới.
5. **Micro:** chỉ chạy trên trang thật (https), không chạy trong bản xem của Claude.

## 9. Danh sách kiểm tra trước khi giao một tuần mới
- [ ] Có đủ bản `zh` và `en` cho tuần, đúng bối cảnh công sở, đúng dàn nhân vật.
- [ ] `check_rules.py` báo 0 lỗi: chữ đã học, đủ dữ liệu hội thoại, nhại theo, mẫu câu, bài đọc, 4 cặp chữ khác số nét, 4 chữ viết.
- [ ] Từ mới đã có trong từ điển tra nhanh (bính âm, Anh, Việt).
- [ ] Mọi câu có tranh; mọi đáp án sai có giải thích.
- [ ] Chữ Hán luôn kèm bính âm ở mọi bài; nghĩa luôn có tiếng Anh trước, tiếng Việt sau; tra từ ở mọi chữ Hán.
- [ ] Âm thanh: mọi câu có file giọng Gemini (thêm vào `tools/audio-list.json`, giọng cố định theo nhân vật), đã chạy `audio_clean.py`; không để câu nào chỉ có giọng trình duyệt.
- [ ] Tự phát, tự chuyển 1,2 giây, sai thì hiện đáp án 2 giây, cuối bài làm lại câu tương tự, luôn có nút đi tiếp.
- [ ] Mỗi bài có Cách làm, Quy tắc, Làm sao cho hiệu quả; bài nghe và nói có khuyến nghị trình duyệt.
- [ ] `node tools/t20.js` 0 lỗi; thử sai không kẹt; `--shots` không có cuộn ngang, ảnh chụp máy tính và điện thoại ổn.
- [ ] Đẩy lên bằng tài khoản ces-training, cập nhật bản xem trong Claude, cập nhật ghi chú tiến độ trong Project.
