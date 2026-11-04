/**
 * Nhận kết quả bài kiểm tra đầu vào và đăng ký chờ lớp từ web Anh – Trung Thực Chiến.
 * Cách cài (5 phút):
 * 1. Tạo một Google Sheet mới, đặt tên "Đầu vào Anh – Trung".
 * 2. Mở Tiện ích mở rộng → Apps Script, xoá mã mẫu, dán toàn bộ file này, bấm Lưu.
 * 3. Bấm Triển khai → Tùy chọn triển khai mới → loại "Ứng dụng web":
 *    Thực thi với tư cách: Tôi · Ai có quyền truy cập: Bất kỳ ai → Triển khai → cấp quyền.
 * 4. Sao chép "URL ứng dụng web" (dạng https://script.google.com/macros/s/.../exec) gửi cho Claude
 *    để dán vào SHEET_URL trong placement.js.
 */
const HEAD = {
  placement: ["Thời gian", "Họ tên", "Liên hệ", "Ngôn ngữ", "Mục tiêu", "Chứng chỉ muốn đạt", "Tự đánh giá", "Trình độ xếp", "Lộ trình", "Điểm", "Theo kỹ năng"],
  waitlist: ["Thời gian", "Họ tên", "Liên hệ", "Ngôn ngữ", "Lộ trình chờ"]
};
function doPost(e) {
  const d = JSON.parse(e.postData.contents || "{}");
  const type = d.type === "waitlist" ? "waitlist" : "placement";
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const name = type === "waitlist" ? "Đăng ký chờ" : "Kiểm tra đầu vào";
  const sh = ss.getSheetByName(name) || ss.insertSheet(name);
  if (sh.getLastRow() === 0) { sh.appendRow(HEAD[type]); sh.setFrozenRows(1); }
  const row = type === "waitlist"
    ? [new Date(d.time), d.name, d.contact, d.lang, d.track]
    : [new Date(d.time), d.name, d.contact, d.lang, d.goal, d.cert, d.self, d.level, d.track, d.score, d.skills];
  sh.appendRow(row.map(v => (typeof v === "string" ? v.slice(0, 500) : v)));
  return ContentService.createTextOutput("ok");
}
