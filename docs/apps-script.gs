/**
 * Anh – Trung Thực Chiến · nhận dữ liệu từ web, ghi Google Sheet, báo admin qua Zalo OA "Học viện đa ngữ CES".
 * Cách cài: xem docs/HUONG-DAN-SHEET-ZALO.md (khoảng 20 phút, làm một lần).
 *
 * Web gửi về đây:
 *   - trang chủ (form đăng ký): đơn "dang-ky"
 *   - trang học: placement (kiểm tra đầu vào), production (bài nói, viết sau kiểm tra đầu vào; tệp ghi âm lưu vào Drive), waitlist (chờ lớp), seen (vào học, mỗi ngày 1 lần),
 *     day (xong một ngày học), order (đặt lớp nhóm 89k, vé Weekend Live 179k, mua gói), paid_claim (bấm "Tôi đã chuyển khoản")
 * Web hỏi lại (GET ?a=status): học viên đã được kích hoạt gói chưa, đơn nào đã thu tiền.
 *
 * Admin chỉ cần: đổi cột "Trạng thái" của đơn sang "Đã thu" khi thấy tiền về. Web của học viên tự mở khoá.
 *
 * Thuộc tính tập lệnh (Cài đặt dự án → Thuộc tính tập lệnh), KHÔNG dán vào mã:
 *   ZALO_APP_ID, ZALO_SECRET_KEY, ZALO_REFRESH_TOKEN  (lấy ở developers.zalo.me, xem hướng dẫn)
 *   ZALO_ADMIN_IDS   user_id Zalo của admin (nhiều người thì cách nhau dấu phẩy)
 *   ADMIN_EMAIL      email dự phòng khi Zalo không gửi được
 */

const TZ = "Asia/Ho_Chi_Minh";
const SHEETS = {
  hv: ["Mã HV", "Họ tên", "Zalo/SĐT", "Email", "Ngôn ngữ", "Lộ trình", "Trình độ", "Lần đầu", "Lần cuối", "Bài đã xong", "Ngày học đã xong", "Gói", "Hạn gói", "Đã nhắc bỏ học", "Ghi chú"],
  don: ["Thời gian", "Mã đơn", "Mã HV", "Họ tên", "Zalo/SĐT", "Loại", "Nội dung", "Số tiền", "Lịch", "Trạng thái", "Ngày thu", "Nguồn", "Ghi chú"],
  dauvao: ["Thời gian", "Mã HV", "Họ tên", "Liên hệ", "Ngôn ngữ", "Mục tiêu", "Chứng chỉ muốn đạt", "Tự đánh giá", "Trình độ xếp", "Lộ trình", "Điểm", "Theo kỹ năng", "Độ tin cậy", "Thời gian làm (phút)", "Ước lượng theo kỹ năng", "Từng câu"],
  noiviet: ["Thời gian", "Mã HV", "Họ tên", "Liên hệ", "Ngôn ngữ", "Trình độ tạm xếp", "Đề nói", "Bài nói (link Drive)", "Số giây", "Đề viết", "Bài viết", "Giáo viên chốt mức", "Ghi chú giáo viên"],
  cho: ["Thời gian", "Mã HV", "Họ tên", "Liên hệ", "Ngôn ngữ", "Lộ trình chờ"],
  log: ["Thời gian", "Loại", "Nội dung", "Kết quả"]
};
const NAMES = { hv: "Học viên", don: "Đơn hàng", dauvao: "Kiểm tra đầu vào", noiviet: "Nói viết đầu vào", cho: "Đăng ký chờ", log: "Nhật ký" };
const STATUS = ["Chờ chuyển khoản", "Đã báo chuyển", "Đã thu", "Huỷ"];
const TYPE_NAME = { "lop-nhom": "Lớp nhóm học thử", "weekend-live": "Vé Weekend Live học thử", "goi": "Gói học", "dang-ky": "Đăng ký ở trang chủ" };

/* ================= nhận dữ liệu ================= */
function doPost(e) {
  const lock = LockService.getScriptLock(); lock.waitLock(20000);
  try {
    let d = {};
    try { d = JSON.parse((e.postData && e.postData.contents) || "{}"); } catch (x) { d = {}; }
    if (!d.type && e.parameter && e.parameter.code) d = Object.assign({ type: "landing" }, e.parameter); // form trang chủ
    const t = d.type || "";
    if (t === "placement") onPlacement(d);
    else if (t === "production") onProduction(d);
    else if (t === "waitlist") onWaitlist(d);
    else if (t === "seen") upsertHV(d, { seen: true });
    else if (t === "day") upsertHV(d, { day: d.day, doneN: d.doneN });
    else if (t === "order") onOrder(d);
    else if (t === "paid_claim") onPaidClaim(d);
    else if (t === "landing") onLanding(d);
    return out({ ok: true });
  } catch (err) {
    log("lỗi", String(err), "doPost");
    return out({ ok: false });
  } finally { lock.releaseLock(); }
}

/* web hỏi trạng thái: ?a=status&id=AT…&code=AT… */
function doGet(e) {
  const p = e.parameter || {};
  if (p.a !== "status") return out({ ok: true, app: "anh-trung" });
  const sh = sheet("don"), rows = sh.getDataRange().getValues().slice(1);
  const H = SHEETS.don, c = k => H.indexOf(k);
  let id = String(p.id || "").trim();
  const code = String(p.code || "").trim().toUpperCase();
  if (code) { const r = rows.find(r => String(r[c("Mã đơn")]).toUpperCase() === code); if (!r) return out({ ok: false, error: "Không tìm thấy mã này" }); if (!id || r[c("Mã HV")]) id = r[c("Mã HV")] || code; }
  const mine = rows.filter(r => (id && r[c("Mã HV")] === id) || (code && String(r[c("Mã đơn")]).toUpperCase() === code));
  const orders = mine.map(r => ({ code: r[c("Mã đơn")], type: r[c("Loại")], item: r[c("Nội dung")], status: r[c("Trạng thái")], amount: r[c("Số tiền")] }));
  let plan = "", until = 0;
  mine.forEach(r => {
    if (r[c("Trạng thái")] !== "Đã thu") return;
    const type = r[c("Loại")], item = String(r[c("Nội dung")] || "");
    if (!isPlan(type, item)) return;
    const paidAt = new Date(r[c("Ngày thu")] || r[c("Thời gian")]), days = /16 tuần|term/.test(item) ? 112 : 31;
    const u = paidAt.getTime() + days * 864e5;
    if (u > until) { until = u; plan = item; }
  });
  return out({ ok: true, id, plan, until, active: until > Date.now(), orders });
}

/* ================= xử lý từng loại ================= */
function onPlacement(d) {
  sheet("dauvao").appendRow([now(), d.id || "", d.name, d.contact, d.lang, d.goal, d.cert, d.self, d.level, d.track, d.score, d.skills, d.trust || "", d.mins || "", d.skLv || ""].map(clip).concat([String(d.items || "").slice(0, 4000)]));
  upsertHV(d, { name: d.name, contact: d.contact, lang: d.lang, track: d.track, level: d.level });
  zalo(`🆕 Có người mới làm kiểm tra đầu vào\n${d.name} · ${d.contact}\n${d.lang}: ${d.level} → ${d.track}${d.trust && d.trust !== "Tin cậy" ? "\n⚠️ " + d.trust + " → nên gọi kiểm tra lại 5 phút" : ""}\nMục tiêu: ${d.goal || "-"}\nMã HV: ${d.id || "-"}\n👉 Nhắn Zalo chào và mời học thử trong 24 giờ.`);
}
/* bài nói, viết sau kiểm tra đầu vào: tệp ghi âm lưu vào thư mục Drive riêng (chỉ chủ Sheet xem được), link ghi vào Sheet */
function onProduction(d) {
  let link = "";
  if (d.audio && String(d.audio).indexOf("base64,") > 0) {
    try {
      const b64 = String(d.audio).split("base64,")[1], mime = d.mime || "audio/webm", ext = /mp4|aac|m4a/.test(mime) ? "m4a" : /ogg/.test(mime) ? "ogg" : "webm";
      const it = DriveApp.getFoldersByName("CES · Bài nói đầu vào"), folder = it.hasNext() ? it.next() : DriveApp.createFolder("CES · Bài nói đầu vào");
      const f = folder.createFile(Utilities.newBlob(Utilities.base64Decode(b64), mime, `${Utilities.formatDate(new Date(), TZ, "yyyy-MM-dd HH.mm")} ${d.name || ""} ${d.lang || ""}.${ext}`));
      link = f.getUrl();
    } catch (x) { log("lỗi", "lưu ghi âm: " + x, d.name); }
  }
  sheet("noiviet").appendRow([now(), d.id || "", d.name, d.contact, d.lang, d.level, d.sayPrompt, link, d.secs || "", d.writePrompt, String(d.text || "").slice(0, 3000), "", ""].map(v => typeof v === "string" ? v.slice(0, 3000) : v));
  zalo(`🎙️ Bài nói, viết đầu vào cần chấm\n${d.name} · ${d.contact}\n${d.lang}: tạm xếp ${d.level}\n${link ? "Ghi âm " + (d.secs || "?") + " giây" : "Không có ghi âm"} · ${d.text ? "có bài viết" : "không có bài viết"}\n→ Nghe, đọc ở tab "Nói viết đầu vào", ghi mức chốt rồi nhắn học viên.`);
}
function onWaitlist(d) {
  sheet("cho").appendRow([now(), d.id || "", d.name, d.contact, d.lang, d.track].map(clip));
  const n = sheet("cho").getDataRange().getValues().filter(r => r[5] === d.track).length;
  zalo(`⏳ Đăng ký chờ lớp: ${d.track}\n${d.name} · ${d.contact}\nĐã có ${n} người chờ lộ trình này${n >= 6 ? " → ĐỦ 6 NGƯỜI, có thể mở lớp." : "."}`);
}
function onOrder(d) {
  sheet("don").appendRow([now(), d.code, d.id || "", d.name, d.contact, d.kind, d.item, d.amount, d.when || "", STATUS[0], "", "web", ""].map(clip));
  upsertHV(d, { name: d.name, contact: d.contact });
  setStatusRule();
  zalo(`🧾 Đơn mới ${d.code}: ${TYPE_NAME[d.kind] || d.kind}\n${d.item} · ${money(d.amount)}${d.when ? "\nLịch: " + d.when : ""}\n${d.name} · ${d.contact}\n👉 Học viên sẽ nhắn OA kèm mã ${d.code}: hướng dẫn thanh toán; thu xong thì đổi Trạng thái thành "Đã thu" trong Sheet.`);
}
function onPaidClaim(d) {
  const sh = sheet("don"), v = sh.getDataRange().getValues(), H = SHEETS.don;
  for (let i = 1; i < v.length; i++) if (v[i][H.indexOf("Mã đơn")] === d.code && v[i][H.indexOf("Trạng thái")] === STATUS[0]) sh.getRange(i + 1, H.indexOf("Trạng thái") + 1).setValue(STATUS[1]);
  zalo(`💸 ${d.name || "Học viên"} báo đã thanh toán đơn ${d.code} (${money(d.amount)}).\n👉 Kiểm tra tài khoản, đúng thì đổi Trạng thái thành "Đã thu".`);
}
function onLanding(d) {
  const plan = { test: "Làm bài test miễn phí", online: "Gói Online", member: "Gói Thành viên", vip: "Gói VIP", ticket: "Vé lẻ Weekend Live", b2b: "Lớp doanh nghiệp" }[d.plan] || d.plan;
  const item = plan + (d.billing ? (d.billing === "term" ? " · 16 tuần" : " · theo tháng") : "");
  sheet("don").appendRow([now(), d.code, "", d.name, d.phone + (d.email ? " · " + d.email : ""), "dang-ky", item, d.amount || "", d.schedule || "", d.plan === "test" || d.plan === "b2b" ? "" : STATUS[0], "", "trang chủ" + (d.utm_source ? " · " + d.utm_source : ""), `${d.language} · ${d.goal}`].map(clip));
  setStatusRule();
  zalo(`📝 Đăng ký ở trang chủ ${d.code}: ${item}${d.amount ? " · " + money(d.amount) : ""}\n${d.name} · ${d.phone}${d.email ? " · " + d.email : ""}\n${d.language || ""} · ${d.goal || ""} · giờ ${d.schedule || "-"}\n👉 Gọi hoặc nhắn Zalo trong giờ làm việc.`);
}

/* học viên: một dòng mỗi người, cập nhật lần cuối vào học */
function upsertHV(d, o) {
  if (!d.id) return;
  const sh = sheet("hv"), H = SHEETS.hv, c = k => H.indexOf(k) + 1;
  const f = sh.createTextFinder(d.id).matchEntireCell(true).findNext();
  let r = f ? f.getRow() : 0;
  if (!r) { sh.appendRow([d.id, o.name || d.name || "", o.contact || d.contact || "", d.email || "", o.lang || d.lang || "", o.track || "", o.level || "", now(), now()].map(clip)); r = sh.getLastRow(); }
  const set = (k, v) => { if (v !== undefined && v !== "") sh.getRange(r, c(k)).setValue(clip(v)); };
  set("Lần cuối", now());
  set("Họ tên", o.name); set("Zalo/SĐT", o.contact); set("Ngôn ngữ", o.lang); set("Lộ trình", o.track); set("Trình độ", o.level);
  if (o.doneN !== undefined) set("Bài đã xong", o.doneN);
  if (o.day) { const old = String(sh.getRange(r, c("Ngày học đã xong")).getValue() || ""); if (old.indexOf(o.day) < 0) set("Ngày học đã xong", (old ? old + ", " : "") + o.day); }
}

/* admin đổi Trạng thái → ghi Ngày thu (trình kích hoạt đơn giản, không cần cài) */
function onEdit(e) {
  const sh = e.range.getSheet(); if (sh.getName() !== NAMES.don) return;
  const H = SHEETS.don, col = H.indexOf("Trạng thái") + 1;
  if (e.range.getColumn() !== col || e.range.getRow() < 2) return;
  if (e.value === "Đã thu") sh.getRange(e.range.getRow(), H.indexOf("Ngày thu") + 1).setValue(now());
}

/* ================= nhắc hằng ngày (8:00) ================= */
function nhacHangNgay() {
  const lines = [], today = new Date(), dow = Number(Utilities.formatDate(today, TZ, "u")); // 1 = Thứ 2 … 7 = Chủ nhật
  /* 1. người học thử bỏ học 2 ngày */
  const sh = sheet("hv"), v = sh.getDataRange().getValues(), H = SHEETS.hv, c = k => H.indexOf(k);
  const active = activePlans();
  const quiet = [];
  for (let i = 1; i < v.length; i++) {
    const r = v[i], last = r[c("Lần cuối")] ? new Date(r[c("Lần cuối")]) : null; if (!last || !r[c("Zalo/SĐT")]) continue;
    const days = Math.floor((today - last) / 864e5), mark = Utilities.formatDate(last, TZ, "dd/MM");
    if (days >= 2 && days <= 14 && !active[r[c("Mã HV")]] && r[c("Đã nhắc bỏ học")] !== mark) {
      quiet.push(`• ${r[c("Họ tên")] || r[c("Mã HV")]} · ${r[c("Zalo/SĐT")]} · nghỉ ${days} ngày · đã xong ${r[c("Ngày học đã xong")] || "chưa ngày nào"}`);
      sh.getRange(i + 1, c("Đã nhắc bỏ học") + 1).setValue(mark);
    }
  }
  if (quiet.length) lines.push(`😴 Học thử nhưng nghỉ 2 ngày trở lên (nhắn kéo lại):\n${quiet.slice(0, 15).join("\n")}`);
  /* 2. đơn chờ quá 1 ngày */
  const dv = sheet("don").getDataRange().getValues(), D = SHEETS.don, dc = k => D.indexOf(k);
  const wait = dv.slice(1).filter(r => (r[dc("Trạng thái")] === STATUS[0] || r[dc("Trạng thái")] === STATUS[1]) && today - new Date(r[dc("Thời gian")]) > 864e5);
  if (wait.length) lines.push(`🧾 ${wait.length} đơn chưa thu tiền quá 1 ngày:\n${wait.slice(0, 10).map(r => `• ${r[dc("Mã đơn")]} · ${r[dc("Họ tên")]} · ${r[dc("Nội dung")]} · ${r[dc("Trạng thái")]}`).join("\n")}`);
  /* 3. lớp nhóm tối thứ 4 (báo vào Thứ 3, Thứ 4) và Weekend Live (báo vào Thứ 5, Thứ 6) */
  const paid = dv.slice(1).filter(r => r[dc("Trạng thái")] === "Đã thu" && new Date(r[dc("Thời gian")]) > new Date(today - 10 * 864e5));
  const group = (type, key) => { const g = {}; paid.filter(r => r[dc("Loại")] === type).forEach(r => { const k = String(r[dc(key)] || "-"); g[k] = (g[k] || 0) + 1; }); return Object.entries(g).map(([k, n]) => `• ${k}: ${n} người`).join("\n"); };
  if (dow === 2 || dow === 3) { const g = group("lop-nhom", "Lịch"); if (g) lines.push(`👩‍🏫 Lớp nhóm học thử tuần này (xếp lớp, gửi link cho GV):\n${g}`); }
  if (dow === 4 || dow === 5) { const g = group("weekend-live", "Nội dung"); if (g) lines.push(`🎤 Weekend Live thứ 7 (chốt trạm, báo host và người nước ngoài):\n${g}`); }
  /* 4. gói sắp hết hạn trong 3 ngày */
  const soon = Object.entries(active).filter(([, a]) => a.until - today < 3 * 864e5).map(([id, a]) => `• ${a.name} · ${a.contact} · ${a.plan} · hết hạn ${Utilities.formatDate(new Date(a.until), TZ, "dd/MM")}`);
  if (soon.length) lines.push(`⏰ Gói sắp hết hạn (mời gia hạn):\n${soon.join("\n")}`);
  zalo(lines.length ? `☀️ Việc hôm nay ${Utilities.formatDate(today, TZ, "dd/MM")}\n\n${lines.join("\n\n")}\n\n(Trả lời tin này để Zalo tiếp tục gửi báo miễn phí.)` : `☀️ ${Utilities.formatDate(today, TZ, "dd/MM")}: không có việc cần xử lý. (Trả lời tin này để Zalo tiếp tục gửi báo miễn phí.)`);
}
function activePlans() {
  const dv = sheet("don").getDataRange().getValues(), D = SHEETS.don, dc = k => D.indexOf(k), m = {};
  dv.slice(1).forEach(r => {
    if (r[dc("Trạng thái")] !== "Đã thu" || !isPlan(r[dc("Loại")], r[dc("Nội dung")]) || !r[dc("Mã HV")]) return;
    const until = new Date(r[dc("Ngày thu")] || r[dc("Thời gian")]).getTime() + (/16 tuần/.test(r[dc("Nội dung")]) ? 112 : 31) * 864e5;
    if (until > Date.now() && (!m[r[dc("Mã HV")]] || m[r[dc("Mã HV")]].until < until)) m[r[dc("Mã HV")]] = { until, plan: r[dc("Nội dung")], name: r[dc("Họ tên")], contact: r[dc("Zalo/SĐT")] };
  });
  return m;
}

/* ================= Zalo OA ================= */
function zaloToken() {
  const P = PropertiesService.getScriptProperties();
  const exp = Number(P.getProperty("ZALO_ACCESS_EXP") || 0), tok = P.getProperty("ZALO_ACCESS_TOKEN");
  if (tok && exp > Date.now() + 60000) return tok;
  const lock = LockService.getDocumentLock(); lock.waitLock(20000);
  try {
    const e2 = Number(P.getProperty("ZALO_ACCESS_EXP") || 0), t2 = P.getProperty("ZALO_ACCESS_TOKEN");
    if (t2 && e2 > Date.now() + 60000) return t2; /* lượt khác vừa làm mới xong */
    const appId = P.getProperty("ZALO_APP_ID"), secret = P.getProperty("ZALO_SECRET_KEY"), refresh = P.getProperty("ZALO_REFRESH_TOKEN");
    if (!appId || !secret || !refresh) throw new Error("Chưa điền ZALO_APP_ID, ZALO_SECRET_KEY, ZALO_REFRESH_TOKEN");
    const r = UrlFetchApp.fetch("https://oauth.zaloapp.com/v4/oa/access_token", {
      method: "post", headers: { secret_key: secret }, muteHttpExceptions: true,
      payload: { app_id: appId, grant_type: "refresh_token", refresh_token: refresh }
    });
    const j = JSON.parse(r.getContentText() || "{}");
    if (!j.access_token) throw new Error("Không làm mới được token Zalo: " + r.getContentText().slice(0, 200));
    /* refresh token chỉ dùng được một lần: lưu ngay cái mới */
    P.setProperties({ ZALO_ACCESS_TOKEN: j.access_token, ZALO_REFRESH_TOKEN: j.refresh_token || refresh, ZALO_ACCESS_EXP: String(Date.now() + Number(j.expires_in || 3600) * 1000) });
    return j.access_token;
  } finally { lock.releaseLock(); }
}
function zalo(text) {
  const P = PropertiesService.getScriptProperties(), ids = String(P.getProperty("ZALO_ADMIN_IDS") || "").split(",").map(s => s.trim()).filter(Boolean);
  let ok = 0, why = "";
  try {
    if (!ids.length) throw new Error("Chưa điền ZALO_ADMIN_IDS");
    const tok = zaloToken();
    ids.forEach(id => {
      const r = UrlFetchApp.fetch("https://openapi.zalo.me/v3.0/oa/message/cs", { method: "post", contentType: "application/json", headers: { access_token: tok }, muteHttpExceptions: true,
        payload: JSON.stringify({ recipient: { user_id: id }, message: { text: String(text).slice(0, 1900) } }) });
      const j = JSON.parse(r.getContentText() || "{}"); if (j.error === 0) ok++; else why = (j.message || r.getContentText()).slice(0, 200);
    });
  } catch (err) { why = String(err.message || err); }
  if (!ok) {
    const mail = P.getProperty("ADMIN_EMAIL");
    if (mail) try { MailApp.sendEmail(mail, "[Anh – Trung] " + String(text).split("\n")[0].slice(0, 80), text + "\n\n(Zalo chưa gửi được: " + why + ")"); } catch (e) {}
  }
  log("zalo", String(text).split("\n")[0], ok ? `đã gửi ${ok}/${ids.length}` : "LỖI: " + why);
}

/* ================= menu cho admin ================= */
function onOpen() {
  SpreadsheetApp.getUi().createMenu("CES")
    .addItem("1. Cài đặt (tạo bảng, nhắc 8 giờ sáng)", "caiDat")
    .addItem("2. Tìm user_id Zalo của admin", "timAdmin")
    .addItem("3. Gửi thử tin Zalo", "guiThu")
    .addItem("Chạy nhắc hằng ngày ngay", "nhacHangNgay").addToUi();
}
function caiDat() {
  Object.keys(SHEETS).forEach(k => sheet(k));
  setStatusRule();
  ScriptApp.getProjectTriggers().filter(t => t.getHandlerFunction() === "nhacHangNgay").forEach(t => ScriptApp.deleteTrigger(t));
  ScriptApp.newTrigger("nhacHangNgay").timeBased().atHour(8).nearMinute(5).everyDays(1).inTimezone(TZ).create();
  SpreadsheetApp.getUi().alert("Đã tạo các bảng và lịch nhắc 8 giờ sáng mỗi ngày.");
}
function timAdmin() {
  const r = UrlFetchApp.fetch("https://openapi.zalo.me/v2.0/oa/listrecentchat?data=" + encodeURIComponent(JSON.stringify({ offset: 0, count: 10 })), { headers: { access_token: zaloToken() }, muteHttpExceptions: true });
  const j = JSON.parse(r.getContentText() || "{}"), seen = {};
  (j.data || []).forEach(m => { if (m.src === 1 && m.from_id) seen[m.from_id] = m.from_display_name; });
  const list = Object.entries(seen).map(([id, n]) => `${n}: ${id}`);
  list.forEach(s => log("user_id", s, ""));
  SpreadsheetApp.getUi().alert(list.length ? "Người vừa nhắn OA (chép user_id vào ZALO_ADMIN_IDS):\n\n" + list.join("\n") : "Chưa thấy ai. Admin hãy nhắn một tin bất kỳ vào OA rồi chạy lại.\n" + r.getContentText().slice(0, 200));
}
function guiThu() { zalo("✅ Thử kết nối: web Anh – Trung sẽ báo admin qua tin này."); SpreadsheetApp.getUi().alert("Đã gửi. Xem kết quả ở bảng Nhật ký."); }

/* ================= tiện ích ================= */
function sheet(k) {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  let sh = ss.getSheetByName(NAMES[k]);
  if (!sh) sh = ss.insertSheet(NAMES[k]);
  if (sh.getLastRow() === 0) { sh.appendRow(SHEETS[k]); sh.setFrozenRows(1); sh.getRange(1, 1, 1, SHEETS[k].length).setFontWeight("bold"); }
  return sh;
}
function setStatusRule() {
  const sh = sheet("don"), col = SHEETS.don.indexOf("Trạng thái") + 1;
  sh.getRange(2, col, Math.max(sh.getMaxRows() - 1, 1), 1).setDataValidation(SpreadsheetApp.newDataValidation().requireValueInList(STATUS, true).setAllowInvalid(true).build());
}
function log(type, msg, res) { try { sheet("log").appendRow([now(), type, clip(msg), clip(res)]); } catch (e) {} }
const now = () => new Date();
const isPlan = (type, item) => type === "goi" || (type === "dang-ky" && /Gói (Online|Thành viên|VIP)/.test(String(item)));
const clip = v => (typeof v === "string" ? v.slice(0, 500) : v == null ? "" : v);
const money = n => n ? Number(n).toLocaleString("vi-VN") + "đ" : "";
function out(o) { return ContentService.createTextOutput(JSON.stringify(o)).setMimeType(ContentService.MimeType.JSON); }
