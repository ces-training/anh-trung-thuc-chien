# Anh – Trung Thực Chiến

Trang web chương trình tiếng Anh và tiếng Trung giao tiếp cho sinh viên và người đi làm.

- Trang chủ: https://ces-training.github.io/anh-trung-thuc-chien/
- Bài tập tuần 1: https://ces-training.github.io/anh-trung-thuc-chien/tuan-1/

## Sửa nội dung
- Thông tin liên hệ, ngân hàng, giá, địa chỉ nhận form: khối `SITE_CONFIG` cuối file `index.html`.
- Ảnh: thay file cùng tên trong thư mục `images/`.

## Dựng và đẩy trang bài tập

- Nội dung bài: `tools/course/*.json`; giao diện: `tools/build/page-template.html`.
- Dựng: `python3 tools/build2.py` (tự kiểm tra quy tắc, ghi `tuan-1/index.html`).
- Kiểm thử: `node tools/t20.js` (mọi bài) và `node tools/t20.js --shots` (ảnh máy tính, điện thoại).
- Đẩy lên: `python3 tools/deploy.py "nội dung thay đổi"` (chỉ đẩy khi kho là của ces-training; mặc định `[skip ci]`).
- Tuần học thử: `#w5-thu-2` (HSK2), `#a2-w1-thu-2` (Anh A2), `#b1-w1-thu-2` (Anh B1), mở từ trang Lộ trình hoặc kết quả kiểm tra đầu vào.

## Giọng đọc mẫu (Gemini)

- Danh sách câu cần đọc: `tools/audio-list.json` (220 câu, có tên nhân vật để chọn giọng).
- Workflow **Tạo giọng đọc Gemini** (tab Actions) gọi Gemini TTS, lưu mp3 vào `tuan-1/audio/` và tự cập nhật trang.
- Cần secret `GEMINI_API_KEY` (Settings → Secrets and variables → Actions).
- Câu nào chưa có file thì trang tự dùng giọng đọc của trình duyệt.
- Đổi giọng nhân vật: sửa `VOICES` trong `tools/make_audio.py`, rồi chạy workflow với `redo = all`.
