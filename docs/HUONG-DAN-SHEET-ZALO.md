# Cài Google Sheet và báo Zalo cho admin (làm một lần, khoảng 20 phút)

Sau khi cài, mọi thứ học viên làm trên web (kiểm tra đầu vào, đặt lớp nhóm, giữ vé Weekend Live, mua gói, nghỉ học) tự ghi vào Google Sheet, và admin nhận tin Zalo từ OA **Học viện đa ngữ CES**.

## A. Google Sheet và Apps Script
1. Tạo một Google Sheet mới, đặt tên "Học viên Anh – Trung".
2. Vào **Tiện ích mở rộng → Apps Script**. Xoá mã mẫu, dán toàn bộ file `docs/apps-script.gs`, bấm **Lưu**.
3. Quay lại Sheet, tải lại trang. Trên thanh menu có mục **CES** → bấm **1. Cài đặt**, cấp quyền khi Google hỏi.
   Sheet sẽ có các bảng: Học viên, Đơn hàng, Kiểm tra đầu vào, Nói viết đầu vào, Liên hệ, Lượt truy cập, Đăng ký chờ, Nhật ký (bảng Tổng quan tạo khi bấm CES → Cập nhật bảng Tổng quan). Lịch nhắc 8 giờ sáng mỗi ngày được bật.
   Google sẽ hỏi thêm quyền **Google Drive**: để lưu tệp ghi âm phần nói của bài kiểm tra đầu vào vào thư mục "CES · Bài nói đầu vào" (chỉ chủ Sheet xem được).
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
| 🧾 Đơn mới (lớp nhóm 89k, Weekend Live 179k, gói học) | Học viên sẽ nhắn OA kèm mã đơn: hướng dẫn thanh toán |
| 💸 Học viên báo đã thanh toán | Kiểm tra tiền về; đúng thì ở bảng **Đơn hàng** đổi **Trạng thái** thành **Đã thu** |
| 📝 Đăng ký ở trang chủ | Gọi hoặc nhắn Zalo trong giờ làm việc |
| ⏳ Đăng ký chờ lớp (báo khi đủ 6 người) | Gom lớp, báo ngày mở |
| ☀️ Việc hôm nay (8 giờ sáng) | Người học thử nghỉ 2 ngày, đơn chưa thu quá 1 ngày, danh sách lớp nhóm theo ca (thứ 3, thứ 4), danh sách Weekend Live theo trạm (thứ 5, thứ 6), gói sắp hết hạn |

Đổi **Trạng thái** thành **Đã thu** là đủ: học viên mở web là gói tự kích hoạt (mở từ tuần 2), đơn lớp nhóm và Weekend Live hiện "Đã thu". Học viên dùng máy khác thì nhập mã đơn ở trang **Chọn gói**.

## D. Zalo OA để học viên liên hệ
Trang không hiện số tài khoản. Mỗi đơn có một mã; học viên bấm **Nhắn Zalo OA** và gửi mã đơn, CES hướng dẫn thanh toán ngay trong Zalo.
Dán đường dẫn của OA (dạng `https://zalo.me/…`, lấy ở OA Manager → Chia sẻ OA) vào `"zaloUrl"` trong `tools/site.json`, rồi chạy `python3 tools/deploy.py "Thêm Zalo OA"`. Trang chủ và trang học cùng hiện nút nhắn OA.
(Nếu sau này muốn hiện mã QR chuyển khoản, điền mục `"bank"` trong cùng file.)

## Lưu ý
- Khoá từ tuần 2 là khoá trên trình duyệt: đủ cho học viên thông thường, nhưng người rành kỹ thuật vẫn xem được nội dung trong mã trang. Muốn khoá chặt cần chuyển bài học lên máy chủ có đăng nhập.
- Tiến độ học vẫn lưu trên trình duyệt; Sheet chỉ nhận các mốc (vào học, xong ngày, đặt chỗ, thanh toán).


## Bài kiểm tra đầu vào: đọc kết quả, chấm phần nói viết, thống kê câu hỏi
- Bảng **Kiểm tra đầu vào**: mỗi lượt một dòng. Cột **Độ tin cậy** ghi "Nghi đoán …" khi học viên bấm quá nhanh hoặc chọn cùng một ô nhiều câu liền: nên gọi kiểm tra lại 5 phút. Cột **Ước lượng theo kỹ năng** chỉ để tham khảo. Cột **Từng câu** dùng cho thống kê (đừng sửa).
- Bảng **Nói viết đầu vào**: giáo viên bấm link nghe bài nói, đọc bài viết, rồi điền **Giáo viên chốt mức** và ghi chú. Nhắn học viên trong 24 giờ.
- **Thống kê câu hỏi** (sau khoảng 50–100 lượt): trong bảng Kiểm tra đầu vào chọn Tệp → Tải xuống → CSV, rồi chạy `python3 tools/placement_stats.py tệp.csv`. Kết quả ghi ra `tools/placement-stats.md`: câu quá dễ, quá khó, nhiều người chọn "chưa biết", hoặc người giỏi lại hay sai (độ phân biệt thấp) → sửa hoặc thay câu đó trong `tools/course/placement.json` (câu mới dùng id mới).

## Liên hệ "Liên hệ CES" và thống kê lượt vào
- Cả trang chủ và trang học có nút **Liên hệ CES** (biểu tượng tin nhắn xanh) (góc phải dưới). Học viên để lại tên, Zalo, chủ đề, câu hỏi, giờ tiện liên hệ → bảng **Liên hệ** + tin Zalo cho admin (kèm "Gửi từ đâu" và "Tình hình học": đã học bao nhiêu bài, học thử gì, kết quả đầu vào). Admin đổi cột **Trạng thái** (Chưa liên hệ / Đã nhắn/gọi / Đã chốt gói / Không nhu cầu). Người chưa liên hệ được nhắc trong tin 8 giờ sáng.
- **Lời mời liên hệ** tự hiện ở các điểm mấu chốt, mỗi loại 1 lần, có nút "Để sau", không hiện nữa khi người đó đã gửi form: trang chủ (đọc Học phí ≥ 8 giây, mở ≥ 2 câu Hỏi đáp, xem ≥ 2 phút); trang học (ở trang Chọn gói/Ưu đãi ≥ 25 giây, xong tuần học thử, học ≥ 8 bài hoặc ≥ 3 ngày). Ngoài ra có nút Hỏi CES ở kết quả kiểm tra đầu vào, trang Chọn gói, Ưu đãi, tuần bị khoá.
- Bảng **Lượt truy cập**: mỗi lượt xem một dòng, ẩn danh (Mã khách ngẫu nhiên, không có tên trừ khi người đó tự gửi form): nguồn, thiết bị, thời gian xem thật, độ cuộn, mục đã đọc (thấy ≥ 4 giây), màn đã mở, nút đã bấm, lời mời đã hiện/bấm/tắt. Cùng Mã khách = cùng một người (trên cùng trình duyệt), nối được với Mã HV khi họ vào trang học.
- Bảng **Tổng quan** (tự cập nhật 8 giờ sáng, hoặc menu CES → Cập nhật bảng Tổng quan): số người vào trang chủ, đọc học phí, vào trang học, mở bài, xem trang giá, làm kiểm tra đầu vào, hỏi CES, đăng ký, đã thu tiền (7 ngày / 30 ngày / tất cả); mục nào được đọc nhiều; màn nào được mở; lời mời nào hiệu quả; nguồn truy cập. Sáng thứ Hai Zalo admin nhận một dòng tóm tắt tuần.
