# Anh – Trung Thực Chiến

Trang web chương trình tiếng Anh và tiếng Trung giao tiếp cho sinh viên và người đi làm.

- Trang chủ: https://ces-training.github.io/anh-trung-thuc-chien/
- Bài tập tuần 1: https://ces-training.github.io/anh-trung-thuc-chien/tuan-1/

## Sửa nội dung
- Thông tin liên hệ, ngân hàng, giá, địa chỉ nhận form: khối `SITE_CONFIG` cuối file `index.html`.
- Ảnh: thay file cùng tên trong thư mục `images/`.

## Giọng đọc mẫu (Gemini)

- Danh sách câu cần đọc: `tools/audio-list.json` (220 câu, có tên nhân vật để chọn giọng).
- Workflow **Tạo giọng đọc Gemini** (tab Actions) gọi Gemini TTS, lưu mp3 vào `tuan-1/audio/` và tự cập nhật trang.
- Cần secret `GEMINI_API_KEY` (Settings → Secrets and variables → Actions).
- Câu nào chưa có file thì trang tự dùng giọng đọc của trình duyệt.
- Đổi giọng nhân vật: sửa `VOICES` trong `tools/make_audio.py`, rồi chạy workflow với `redo = all`.
