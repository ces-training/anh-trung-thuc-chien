# Cài Google Sheet và báo Zalo cho admin (làm một lần, khoảng 20 phút)

Sau khi cài, mọi thứ học viên làm trên web (kiểm tra đầu vào, đặt lớp nhóm, giữ vé Weekend Live, mua gói, nghỉ học) tự ghi vào Google Sheet, và admin nhận tin Zalo từ OA **Học viện đa ngữ CES**.

## A. Google Sheet và Apps Script
1. Tạo một Google Sheet mới, đặt tên "Học viên Anh – Trung".
2. Vào **Tiện ích mở rộng → Apps Script**. Xoá mã mẫu, dán toàn bộ file `docs/apps-script.gs`, bấm **Lưu**.
3. Quay lại Sheet, tải lại trang. Trên thanh menu có mục **CES** → bấm **1. Cài đặt**, cấp quyền khi Google hỏi.
   Sheet sẽ có 5 bảng: Học viên, Đơn hàng, Kiểm tra đầu vào, Đăng ký chờ, Nhật ký. Lịch nhắc 8 giờ sáng mỗi ngày được bật.
4. Trong Apps Script: **Triển khai → Tùy chọn triển khai mới → Ứng dụng web**.
   Thực thi với tư cách: **Tôi**. Ai có quyền truy cập: **Bất kỳ ai**. Bấm Triển khai, chép **URL ứng dụng web** (dạng `https://script.google.com/macros/s/…/exec`).
5. Gửi URL này cho Claude (hoặc tự dán vào `"sheetUrl"` trong `tools/site.json`, rồi chạy `python3 tools/deploy.py "Nối Google Sheet"`). Trang chủ và trang học dùng chung URL này.

Sau này sửa mã Apps Script: **Triển khai → Quản lý các bản triển khai → biểu tượng bút → Phiên bản: Phiên bản mới → Triển khai**. Làm vậy thì URL giữ nguyên.

## B. Nối Zalo OA "Học viện đa ngữ CES"
Cần người có quyền quản trị OA.
1. Vào developers.zalo.me, đăng nhập bằng Zalo của quản trị viên OA. **Tạo ứng dụng mới**, rồi ở mục **Official Account** liên kết ứng dụng với OA Học viện đa ngữ CES và cấp quyền gửi tin cho OA.
2. Ở **Thông tin ứng dụng**, chép **ID ứng dụng** và **Khóa bí mật của ứng dụng**.
3. Lấy **Refresh Token** lần đầu bằng công cụ API Explorer của Zalo (chọn loại token của OA, bấm lấy token): kết quả có Access Token và Refresh Token. Chép Refresh Token.
4. Trong Apps Script, bấm biểu tượng bánh răng **Cài đặt dự án → Thuộc tính tập lệnh → Thêm thuộc tính**, thêm lần lượt:

   | Tên | Giá trị |
   |---|---|
   | `ZALO_APP_ID` | ID ứng dụng |
   | `ZALO_SECRET_KEY` | Khóa bí mật |
   | `ZALO_REFRESH_TOKEN` | Refresh Token vừa lấy |
   | `ADMIN_EMAIL` | email nhận báo dự phòng |

   Không dán các mã này vào file mã hay gửi qua chat công khai.
5. Mỗi admin muốn nhận báo: dùng Zalo cá nhân nhắn một tin bất kỳ vào OA. Sau đó trong Sheet bấm **CES → 2. Tìm user_id Zalo của admin**, chép các user_id hiện ra vào thuộc tính `ZALO_ADMIN_IDS` (nhiều người thì cách nhau dấu phẩy).
6. Bấm **CES → 3. Gửi thử tin Zalo**. Admin nhận được tin "Thử kết nối" là xong. Kết quả từng lần gửi ghi ở bảng **Nhật ký**.

### Quy định của Zalo cần nhớ
- Qua API, OA chỉ gửi được tin tư vấn cho người đã tương tác với OA trong **7 ngày** gần nhất; trong **48 giờ** kể từ lần tương tác cuối thì **miễn phí**.
- Vì vậy mỗi sáng 8 giờ admin nhận tin "Việc hôm nay": **trả lời tin đó một chữ bất kỳ** để Zalo tiếp tục gửi miễn phí.
- Khi Zalo không gửi được (quá hạn tương tác, token lỗi), tin được gửi vào `ADMIN_EMAIL`.
- Refresh Token chỉ dùng được một lần và có hạn khoảng 3 tháng; mã tự đổi token mới mỗi lần gửi. Nếu ngừng dùng quá lâu và Nhật ký báo lỗi token, làm lại bước B3–B4.

## C. Admin nhận gì, làm gì

| Tin Zalo | Việc của admin |
|---|---|
| 🆕 Có người mới làm kiểm tra đầu vào | Nhắn Zalo chào, mời học thử trong 24 giờ |
| 🧾 Đơn mới (lớp nhóm 89k, Weekend Live 179k, gói học) | Chờ tiền về đúng nội dung mã đơn |
| 💸 Học viên báo đã chuyển khoản | Kiểm tra tài khoản; đúng thì ở bảng **Đơn hàng** đổi **Trạng thái** thành **Đã thu** |
| 📝 Đăng ký ở trang chủ | Gọi hoặc nhắn Zalo trong giờ làm việc |
| ⏳ Đăng ký chờ lớp (báo khi đủ 6 người) | Gom lớp, báo ngày mở |
| ☀️ Việc hôm nay (8 giờ sáng) | Người học thử nghỉ 2 ngày, đơn chưa thu quá 1 ngày, danh sách lớp nhóm theo ca (thứ 3, thứ 4), danh sách Weekend Live theo trạm (thứ 5, thứ 6), gói sắp hết hạn |

Đổi **Trạng thái** thành **Đã thu** là đủ: học viên mở web là gói tự kích hoạt (mở từ tuần 2), đơn lớp nhóm và Weekend Live hiện "Đã thu". Học viên dùng máy khác thì nhập mã đơn ở trang **Chọn gói**.

## D. Ngân hàng (mã QR chuyển khoản)
Điền vào `tools/site.json`, mục `"bank"`: mã ngân hàng theo VietQR (ví dụ `"VCB"`), số tài khoản, tên chủ tài khoản; điền `"zalo"`, `"hotline"`. Chạy lại `python3 tools/deploy.py "Cập nhật ngân hàng"`. Trang chủ và trang học cùng hiện mã QR có sẵn số tiền và nội dung là mã đơn.

## Lưu ý
- Khoá từ tuần 2 là khoá trên trình duyệt: đủ cho học viên thông thường, nhưng người rành kỹ thuật vẫn xem được nội dung trong mã trang. Muốn khoá chặt cần chuyển bài học lên máy chủ có đăng nhập.
- Tiến độ học vẫn lưu trên trình duyệt; Sheet chỉ nhận các mốc (vào học, xong ngày, đặt chỗ, thanh toán).
