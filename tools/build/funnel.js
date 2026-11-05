/* ============ HỌC THỬ → HỌC VIÊN: mã học viên, ưu đãi học thử, chọn gói, mở khoá từ tuần 2 ============ */
/* Cấu hình (Apps Script, ngân hàng, Zalo, giá) lấy từ tools/site.json khi dựng trang. */
const fmtVND = n => Number(n || 0).toLocaleString("vi-VN").replace(/,/g, ".") + "đ";
const PLANS = [
  { k: "online", name: "Online", sub: "Tự học với AI, theo nhịp của bạn", month: SITE.prices.online.month, term: SITE.prices.online.term, has: ["Mở toàn bộ bài trên web từ tuần 2", "Đóng vai với AI, chấm phát âm và thanh điệu", "1 buổi Weekend Live mỗi tháng"] },
  { k: "member", name: "Thành viên", sub: "Trọn vòng học, sửa, nói thật mỗi tuần", month: SITE.prices.member.month, term: SITE.prices.member.term, best: true, has: ["Mọi thứ trong gói Online", "Lớp nhóm online 6–8 người mỗi tuần", "4 buổi Weekend Live mỗi tháng, đủ 3 trạm", "Phiếu nhận xét cá nhân sau mỗi buổi"] },
  { k: "vip", name: "VIP", sub: "Có người kèm cho mục tiêu lớn", month: SITE.prices.vip.month, term: SITE.prices.vip.term, has: ["Mọi thứ trong gói Thành viên", "2 buổi kèm 1-1 mỗi tháng", "Luyện phỏng vấn xin việc, học bổng, visa theo hồ sơ thật"] }
];
const LIVE_STATIONS = ["Trạm 1 · Tiếng Anh: phỏng vấn xin việc", "Trạm 2 · Tiếng Trung: đàm phán với nhà cung cấp", "Trạm 3 · Ba bên: làm cầu nối"];
const OFFER = {
  class: { kind: "lop-nhom", title: "Lớp nhóm online với giáo viên", price: SITE.trial.class, full: 0,
    lead: "Tối thứ 4, 6–8 người. Giáo viên sửa đúng những lỗi bạn hay sai trên web, rồi cả lớp tập kịch bản cho cuối tuần." },
  live: { kind: "weekend-live", title: "Weekend Live", price: SITE.trial.live, full: SITE.trial.liveFull,
    lead: "Một buổi chiều nói với người thật: giao lưu với cộng đồng, người nước ngoài, xoay vòng 3 trạm và nhận phiếu nhận xét riêng. Có đồ uống." }
};
/* mã học viên: tạo một lần, đi kèm mọi dữ liệu gửi về Sheet */
function meId() { S.me = S.me || {}; if (!S.me.id) { S.me.id = "HV" + Date.now().toString(36).slice(-4).toUpperCase() + Math.random().toString(36).slice(2, 5).toUpperCase(); save(); } return S.me.id; }
const newCode = () => "AT" + Date.now().toString(36).slice(-5).toUpperCase() + Math.floor(Math.random() * 36).toString(36).toUpperCase();
const _sendSheet = sendSheet;
sendSheet = function (row) {
  S.me = S.me || {};
  if (row.name) S.me.name = row.name; if (row.contact) S.me.contact = row.contact;
  return _sendSheet(Object.assign({ id: meId(), name: S.me.name || (S.profile && S.profile.name) || "", contact: S.me.contact || "", time: new Date().toISOString() }, row));
};
const track = (type, data) => sendSheet(Object.assign({ type }, data || {}));
/* ngày học kế tiếp theo thứ trong tuần (3 = thứ 4, 6 = thứ 7) */
function nextDow(dow) { const d = new Date(); d.setHours(12); const add = (dow - d.getDay() + 7) % 7; d.setDate(d.getDate() + add); return d; }
const ddmm = d => String(d.getDate()).padStart(2, "0") + "/" + String(d.getMonth() + 1).padStart(2, "0");

/* trạng thái gói và đơn: hỏi Apps Script, lưu trên máy */
function planActive() { return !!(S.plan && S.plan.until > Date.now()); }
function orderOf(kind) { return (S.orders || []).filter(o => o.kind === kind && o.status !== "Huỷ").slice(-1)[0] || null; }
async function refreshStatus(code) {
  if (!SITE.sheetUrl) return { ok: false, offline: true };
  try {
    const r = await fetch(SITE.sheetUrl + "?a=status&id=" + encodeURIComponent(meId()) + (code ? "&code=" + encodeURIComponent(code) : ""), { cache: "no-store" });
    const j = await r.json(); if (!j.ok) return j;
    if (j.active) S.plan = { name: j.plan, until: j.until };
    S.orders = S.orders || [];
    (j.orders || []).forEach(o => { const m = S.orders.find(x => x.code === o.code); if (m) m.status = o.status; else S.orders.push({ code: o.code, kind: o.type !== "dang-ky" ? o.type : /^Gói/.test(o.item) ? "goi" : /Weekend/.test(o.item) ? "weekend-live" : "khac", item: o.item, amount: o.amount, status: o.status }); });
    S.statusAt = Date.now(); save(); return j;
  } catch (e) { return { ok: false }; }
}
/* khoá từ tuần 2 của hành trình chính; tuần học thử và tuần 1 luôn mở */
function locked(d) { return !TEACHER && d && !d.demo && (d.week || 1) >= 2 && !planActive(); }

/* ---------- thẻ ưu đãi, biểu mẫu đặt chỗ, khung chuyển khoản ---------- */
function payBox(o) {
  const bank = SITE.bank || {}, hasBank = bank.id && bank.account;
  const qr = hasBank ? `https://img.vietqr.io/image/${encodeURIComponent(bank.id)}-${encodeURIComponent(bank.account)}-compact2.png?amount=${o.amount}&addInfo=${encodeURIComponent(o.code)}&accountName=${encodeURIComponent(bank.name || "")}` : "";
  const st = o.status || "Chờ chuyển khoản", paid = st === "Đã thu";
  return `<div class="paybox${paid ? " paid" : ""}" data-code="${esc(o.code)}">
    <p class="eyebrow">${paid ? "Đã xác nhận" : "Thanh toán"}</p>
    <p><b>${esc(o.item)}</b>${o.when ? ` · ${esc(o.when)}` : ""}</p>
    <p class="payamt">${fmtVND(o.amount)} <span class="pill ${paid ? "ok" : "go"}">${paid ? ICON.check + " Đã thu" : esc(st)}</span></p>
    ${paid ? `<p class="small">CES đã nhận tiền. ${o.kind === "goi" ? "Gói học đã mở, bạn vào học tuần 2 được rồi." : "Hẹn gặp bạn ở buổi học! CES sẽ nhắn Zalo lịch và link."}</p>` : `
    ${qr ? `<img class="qr" src="${qr}" alt="Mã QR chuyển khoản" width="220" height="220" loading="lazy">` : ""}
    <p class="small">Mã đơn của bạn: <b class="code">${esc(o.code)}</b>${hasBank ? ` · Nội dung chuyển khoản: <b>${esc(o.code)}</b> · ${esc(bank.name || "")}` : ""}</p>
    ${hasBank ? "" : `<p class="small">Nhắn <b>Zalo ${esc(SITE.zalo || "OA Học viện đa ngữ CES")}</b> kèm mã đơn <b>${esc(o.code)}</b>, CES sẽ hướng dẫn thanh toán và giữ chỗ cho bạn.</p>`}
    <div class="row">${!hasBank && SITE.zaloUrl ? `<a class="btn primary small" href="${esc(SITE.zaloUrl)}" target="_blank" rel="noopener">Nhắn Zalo OA</a>` : ""}<button type="button" class="btn ${!hasBank && SITE.zaloUrl ? "ghost" : "primary"} small claim"${st === "Đã báo chuyển" ? " disabled" : ""}>${st === "Đã báo chuyển" ? "Đã báo CES, chờ xác nhận" : "Tôi đã thanh toán"}</button><button type="button" class="btn ghost small chk">Kiểm tra trạng thái</button></div>`}
  </div>`;
}
function bindPay(root, rerender) {
  root.querySelectorAll(".paybox").forEach(b => {
    const code = b.dataset.code, o = (S.orders || []).find(x => x.code === code); if (!o) return;
    const cl = $(".claim", b); if (cl) cl.onclick = () => { o.status = "Đã báo chuyển"; save(); track("paid_claim", { code, amount: o.amount }); toast("Đã báo CES. Bạn sẽ nhận xác nhận qua Zalo OA."); rerender(); };
    const ck = $(".chk", b); if (ck) ck.onclick = async () => { ck.disabled = true; ck.textContent = "Đang kiểm tra…"; const j = await refreshStatus(); if (j.offline) toast("Trang chưa kết nối hệ thống của CES. CES sẽ xác nhận qua Zalo."); rerender(); };
  });
}
function contactFields() {
  const me = S.me || {}, P = S.place || {};
  return `<label class="fl">Họ tên<input class="inp" name="nm" autocomplete="name" value="${esc(me.name || P.name || (S.profile && S.profile.name !== "bạn" ? S.profile.name : "") || "")}"></label>
    <label class="fl">Số Zalo hoặc điện thoại<input class="inp" name="ct" inputmode="tel" autocomplete="tel" value="${esc(me.contact || P.contact || "")}"></label>`;
}
function readContact(f) {
  const nm = f.querySelector('[name="nm"]').value.trim(), ct = f.querySelector('[name="ct"]').value.trim();
  if (!nm) return { err: "Bạn nhập họ tên giúp CES nhé." };
  if (ct.replace(/\D/g, "").length < 9 && !/@/.test(ct)) return { err: "Số Zalo hoặc điện thoại cần ít nhất 9 chữ số." };
  S.me = S.me || {}; S.me.name = nm; S.me.contact = ct; return { nm, ct };
}
function placeOrder(kind, item, amount, when) {
  const o = { code: newCode(), kind, item, amount, when: when || "", status: "Chờ chuyển khoản", at: Date.now() };
  S.orders = (S.orders || []).concat([o]); save();
  track("order", { code: o.code, kind, item, amount, when: o.when });
  return o;
}
function offerSection(key) {
  const f = OFFER[key], o = orderOf(f.kind);
  const date = key === "class" ? nextDow(3) : nextDow(6);
  const head = `<p class="eyebrow">Ưu đãi học thử</p><h2>${esc(f.title)} · ${key === "class" ? "tối thứ 4" : "thứ 7"} ${ddmm(date)}</h2><p>${esc(f.lead)}</p>
    <p class="offprice"><b>${fmtVND(f.price)}</b>${f.full ? ` <s>${fmtVND(f.full)}</s> <span class="pill star">Giảm ${Math.round((1 - f.price / f.full) * 100)}%</span>` : ` <span class="muted small">giá học thử, chỉ một lần</span>`}</p>`;
  if (o) return `<section class="card2 offer" data-off="${key}">${head}${payBox(o)}</section>`;
  const pick = key === "class"
    ? `<fieldset class="fl"><legend>Chọn ca</legend><div class="seg big wrapseg">${SITE.classSlots.map((s, i) => `<button type="button" data-v="${esc(s)}" aria-pressed="${i === 0}">${esc(s)}</button>`).join("")}</div></fieldset>
       <fieldset class="fl"><legend>Lớp</legend><div class="seg big"><button type="button" data-l="Tiếng Anh" aria-pressed="${S.lang === "en"}">Tiếng Anh</button><button type="button" data-l="Tiếng Trung" aria-pressed="${S.lang === "zh"}">Tiếng Trung</button></div></fieldset>`
    : `<fieldset class="fl"><legend>Trạm bạn muốn bắt đầu (cả buổi bạn xoay vòng đủ 3 trạm)</legend><div class="seg big wrapseg col">${LIVE_STATIONS.map((s, i) => `<button type="button" data-v="${esc(s)}" aria-pressed="${(S.lang === "zh" ? 1 : 0) === i}">${esc(s)}</button>`).join("")}</div></fieldset>`;
  return `<section class="card2 offer" data-off="${key}">${head}<form class="offform" novalidate>${pick}${contactFields()}<p class="err small" role="alert"></p>
    <button type="submit" class="btn primary huge">${key === "class" ? "Đặt chỗ lớp nhóm" : "Giữ vé Weekend Live"} · ${fmtVND(f.price)}</button></form></section>`;
}
function bindOffers(root, rerender) {
  root.querySelectorAll(".offer").forEach(sec => {
    const key = sec.dataset.off, f = OFFER[key], form = $(".offform", sec);
    if (!form) return;
    form.querySelectorAll(".seg").forEach(g => g.querySelectorAll("button").forEach(b => b.onclick = () => g.querySelectorAll("button").forEach(x => x.setAttribute("aria-pressed", x === b))));
    form.onsubmit = e => {
      e.preventDefault();
      const c = readContact(form), err = $(".err", form); if (c.err) { err.textContent = c.err; return; }
      const v = (form.querySelector("[data-v][aria-pressed=true]") || {}).dataset, lg = (form.querySelector("[data-l][aria-pressed=true]") || {}).dataset;
      const date = ddmm(key === "class" ? nextDow(3) : nextDow(6));
      const item = key === "class" ? `Lớp nhóm ${(lg && lg.l) || ""} học thử` : `Weekend Live học thử · ${(v && v.v) || ""}`;
      placeOrder(f.kind, item, f.price, key === "class" ? `Thứ 4 ${date}, ${(v && v.v) || ""}` : `Thứ 7 ${date}`);
      toast("Đã giữ chỗ cho bạn. Nhắn Zalo OA kèm mã đơn để thanh toán.");
      rerender();
    };
  });
  bindPay(root, rerender);
}

/* ---------- trang Ưu đãi học thử ---------- */
function viewOffers(main) {
  const draw = () => {
    main.innerHTML = "";
    main.appendChild(el(`<div class="roomv">
      ${roomHead("room-live", "Học thử", "Ưu đãi cho tuần học thử", "Một tuần trên web miễn phí. Thêm một buổi lớp nhóm với giáo viên và một buổi Weekend Live để thử trọn vòng học: web dạy, lớp nhóm sửa, cuối tuần nói thật.")}
      ${offerSection("class")}${offerSection("live")}
      <section class="card2"><h2>Học tiếp từ tuần 2</h2><p>Hết tuần học thử, chọn một gói để mở tiếp các tuần sau.</p><a class="btn primary" href="#chon-goi">Xem các gói học</a></section></div>`));
    bindOffers(main, draw); applyPhotos(main);
  };
  draw();
}

/* ---------- trang Chọn gói ---------- */
function viewPlans(main) {
  let bill = S.bill || "month", pick = null;
  const draw = () => {
    const mine = orderOf("goi");
    main.innerHTML = "";
    main.appendChild(el(`<div class="roomv">
      ${roomHead("room-career", "Học tiếp", planActive() ? "Gói học của bạn đang mở" : "Chọn gói để học tiếp từ tuần 2", planActive() ? `${esc(S.plan.name || "Gói học")} còn hạn đến ${ddmm(new Date(S.plan.until))}.` : "Tuần 1 và các tuần học thử luôn mở. Từ tuần 2, bài học mở cho học viên có gói.")}
      ${mine && mine.status !== "Đã thu" ? `<section class="card2">${payBox(mine)}</section>` : ""}
      <section class="card2"><div class="seg" role="group" aria-label="Kỳ thanh toán"><button type="button" data-b="month" aria-pressed="${bill === "month"}">Theo tháng</button><button type="button" data-b="term" aria-pressed="${bill === "term"}">Trọn 16 tuần · tiết kiệm hơn</button></div>
        <div class="plans">${PLANS.map(p => `<div class="plan${p.best ? " best" : ""}${pick === p.k ? " on" : ""}">${p.best ? `<span class="pill star">Được chọn nhiều nhất</span>` : ""}<h3>${esc(p.name)}</h3><p class="small muted">${esc(p.sub)}</p>
          <p class="payamt">${fmtVND(bill === "term" ? p.term : p.month)}<small> / ${bill === "term" ? "16 tuần" : "tháng"}</small></p>
          <ul class="facts small">${p.has.map(h => `<li>${esc(h)}</li>`).join("")}</ul><button type="button" class="btn ${p.best ? "primary" : "ghost"} pk" data-k="${p.k}">Chọn gói ${esc(p.name)}</button></div>`).join("")}</div>
        ${pick ? `<form class="planform" novalidate><p><b>Gói ${esc(PLANS.find(p => p.k === pick).name)} · ${bill === "term" ? "16 tuần" : "1 tháng"}</b></p>${contactFields()}<p class="err small" role="alert"></p><button type="submit" class="btn primary huge">Đăng ký gói · ${fmtVND(bill === "term" ? PLANS.find(p => p.k === pick).term : PLANS.find(p => p.k === pick).month)}</button></form>` : ""}</section>
      <section class="card2"><h2>Đã có mã đăng ký?</h2><p class="small">Mã ở trang chủ, hoặc mã đơn bạn đặt trên máy khác.</p>
        <form class="codeform row" novalidate><input class="inp" name="code" placeholder="Ví dụ: AT1K2M3P" autocapitalize="characters" aria-label="Mã đăng ký"><button type="submit" class="btn primary">Kiểm tra mã</button></form><p class="codemsg small" role="status"></p></section></div>`));
    main.querySelectorAll("[data-b]").forEach(b => b.onclick = () => { bill = b.dataset.b; S.bill = bill; save(); draw(); });
    main.querySelectorAll(".pk").forEach(b => b.onclick = () => { pick = b.dataset.k; draw(); const f = $(".planform", main); if (f) f.scrollIntoView({ behavior: "smooth", block: "center" }); });
    const pf = $(".planform", main);
    if (pf) pf.onsubmit = e => { e.preventDefault(); const c = readContact(pf); if (c.err) { $(".err", pf).textContent = c.err; return; }
      const p = PLANS.find(x => x.k === pick); placeOrder("goi", `Gói ${p.name} · ${bill === "term" ? "16 tuần" : "1 tháng"}`, bill === "term" ? p.term : p.month); pick = null; draw(); scrollTo(0, 0); };
    $(".codeform", main).onsubmit = async e => {
      e.preventDefault(); const code = e.target.code.value.trim().toUpperCase(), msg = $(".codemsg", main); if (!code) { msg.textContent = "Bạn nhập mã giúp CES nhé."; return; }
      msg.textContent = "Đang kiểm tra…"; const j = await refreshStatus(code);
      if (j.offline) msg.textContent = "Trang chưa kết nối hệ thống của CES. Nhắn Zalo CES kèm mã để được mở.";
      else if (!j.ok) msg.textContent = j.error || "Chưa kiểm tra được, bạn thử lại sau ít phút.";
      else if (j.active) { toast("Gói học đã mở!"); draw(); }
      else msg.textContent = "Đã thấy mã, nhưng CES chưa xác nhận thanh toán. Bạn sẽ được mở ngay khi CES xác nhận.";
    };
    bindPay(main, draw); applyPhotos(main);
  };
  draw();
}

/* ---------- học thử: mỗi ngôn ngữ một tuần miễn phí, theo đúng một lộ trình ----------
   Kiểm tra đầu vào trước → tự xếp tuần học thử theo kết quả.
   Tự chọn trình độ trước → học xong tuần đó mới được mời kiểm tra đầu vào; không tự chọn tuần học thử khác.
   Từ chối kiểm tra → chuyển sang lớp nhóm online với giáo viên và Weekend Live (#uu-dai). */
function trialOf(L) { const T = (S.trial || {})[L]; return T && T.track ? T : null; }
const dayLang = d => d.demo ? d.lang : S.lang;
const dayTrack = d => d.demo ? d.track : (dayLang(d) === "zh" ? "zh-a" : "en-a");
function tested(L) { const T = trialOf(L); return !!((T && T.tested) || (S.place && S.place.result && S.place.lang === L)); }
function trialUsed(L) { const T = trialOf(L); return !!(T && T.done); }
function setTrial(L, tid, via) {
  if (!tid || !trackOf(L, tid)) return;
  S.trial = S.trial || {}; const T = S.trial[L], t = trackOf(L, tid);
  if (T && T.track === tid) { if (via === "test") T.tested = true; save(); return; }
  S.trial[L] = { track: tid, via, tested: via === "test" || !!(T && T.tested), used: (T ? T.used : []).filter(x => x !== tid).concat([tid]), done: false, at: Date.now() }; save();
  track("day", { day: `Bắt đầu học thử ${t.name} (${t.lv}) · ${L === "zh" ? "Trung" : "Anh"} · ${via === "test" ? "theo kết quả kiểm tra" : "tự chọn"}`, doneN: Object.keys(S.done).length });
}
/* gọi từ bài kiểm tra đầu vào: chưa học xong tuần học thử thì chuyển sang tuần đúng kết quả; học xong rồi thì giữ nguyên */
function assignTrial(L, tid) {
  const t = trackOf(L, tid), go = t && trackStart(t) ? t : t && nearTrial(L, t); if (!go) return;
  const T = trialOf(L);
  if (T && T.done) { T.tested = true; save(); return; }
  setTrial(L, go.id, "test");
}
function trialDays(L, t) { return t.demo ? DEMO_DAYS.filter(x => x.demo === t.demo) : WDAYS.filter(x => (x.week || 1) === 1 && /thu-\d$/.test(x.id)); }
function trialNext(L, t) { const ds = trialDays(L, t), d = ds.find(x => !S.daily[L + x.id]); return d ? d.id : trackStart(t); }
/* bước tiếp sau khi xong tuần học thử */
function nextStepHTML(L) {
  if (!tested(L)) return `<div class="row"><a class="btn primary huge" href="#kiem-tra-dau-vao">${ICON.play} Làm bài kiểm tra đầu vào</a><a class="btn ghost skiptest" href="#uu-dai">Bỏ qua, xem lớp với giáo viên và Weekend Live</a></div>`;
  return `<div class="row"><a class="btn primary huge" href="#kiem-tra-dau-vao">${ICON.play} Xem kết quả và bước tiếp theo</a><a class="btn ghost" href="#uu-dai">Lớp nhóm online, Weekend Live</a></div>`;
}
function bindSkip(root) { root.querySelectorAll(".skiptest").forEach(a => a.addEventListener("click", () => { const L = S.lang, T = trialOf(L); if (T && !T.skipped) { T.skipped = true; save(); track("day", { day: "Bỏ qua kiểm tra đầu vào → mời lớp nhóm, Weekend Live", doneN: Object.keys(S.done).length }); } })); }
/* kết quả kiểm tra khi đã dùng tuần học thử: không mở thêm tuần miễn phí, chuyển sang bước tiếp */
function afterTrialHTML(L, t) {
  const cur = trackOf(L, trialOf(L).track), same = cur.id === t.id;
  return `<div class="note">Bạn đã học thử tuần <b>${esc(cur.name)} (${esc(cur.lv)})</b>. ${same ? "Kết quả kiểm tra khớp với trình độ bạn đã chọn." : `Kết quả kiểm tra xếp bạn vào lộ trình <b>${esc(t.name)} (${esc(t.lv)})</b>.`}</div>
    <div class="row">${t.status === "open" ? `<a class="btn primary huge" href="#chon-goi">${ICON.play} Chọn gói học ${esc(t.name)}</a>` : `<button type="button" class="btn primary wl">Đăng ký chờ lớp ${esc(t.lv)}</button>`}<a class="btn ghost" href="#uu-dai">Lớp nhóm online với giáo viên, Weekend Live</a></div>`;
}
/* ngày của lộ trình khác khi đang học thử */
function viewTrialLock(main, d, T) {
  const L = dayLang(d), cur = trackOf(L, T.track), want = trackOf(L, dayTrack(d));
  main.appendChild(el(`<div class="roomv">
    ${roomHead("journey-" + S.lang, d.wlabel || d.label, `Bạn đang học thử ${cur.name} (${cur.lv})`, `Mỗi bạn được học thử miễn phí một tuần theo một trình độ. Tuần ${want.name} (${want.lv}) chỉ mở khi kết quả kiểm tra đầu vào xếp bạn vào trình độ này.`)}
    <section class="card2">${T.done ? nextStepHTML(L) : `<div class="row"><a class="btn primary huge" href="#${trialNext(L, cur)}">${ICON.play} Tiếp tục học thử ${esc(cur.name)}</a>${tested(L) ? "" : `<a class="btn ghost" href="#kiem-tra-dau-vao">Làm bài kiểm tra đầu vào</a>`}</div>`}</section></div>`));
  bindSkip(main); applyPhotos(main);
}

/* ---------- ngày bị khoá ---------- */
function viewLocked(main, d) {
  const L = dayLang(d);
  if (trialUsed(L) && !tested(L)) {
    main.appendChild(el(`<div class="roomv">${roomHead("journey-" + S.lang, d.wlabel || d.label, "Bạn đã xong tuần học thử", "Làm bài kiểm tra đầu vào 10–15 phút để CES xếp đúng lộ trình cho bạn, rồi học tiếp.")}<section class="card2">${nextStepHTML(L)}</section></div>`));
    bindSkip(main); applyPhotos(main); return;
  }
  main.appendChild(el(`<div class="roomv">
    ${roomHead("journey-" + S.lang, d.wlabel || d.label, `Tuần ${d.week} dành cho học viên`, "Bạn đã học xong tuần học thử. Chọn một gói để mở tiếp tuần " + d.week + " và các tuần sau. Bài tuần 1 vẫn mở để bạn ôn lại.")}
    <section class="card2"><div class="row"><a class="btn primary huge" href="#chon-goi">${ICON.play} Chọn gói học tiếp</a><a class="btn ghost" href="#uu-dai">Ưu đãi lớp nhóm và Weekend Live</a></div>
    <p class="small muted">Đã đăng ký và chuyển khoản? Vào Chọn gói, bấm Kiểm tra trạng thái hoặc nhập mã đăng ký.</p></section></div>`));
  applyPhotos(main);
  if (SITE.sheetUrl && (!S.statusAt || Date.now() - S.statusAt > 60000)) refreshStatus().then(() => { if (!locked(d)) render(); });
}
function gateDay(main, d, run) {
  if (locked(d)) return viewLocked(main, d);
  if (!TEACHER && !planActive()) {
    const L = dayLang(d), T = trialOf(L), tid = dayTrack(d);
    if (!T) setTrial(L, tid, tested(L) ? "test" : "self");
    else if (!T.used.includes(tid)) return viewTrialLock(main, d, T);
  }
  return run();
}
const _viewDay = viewDay; viewDay = function (main, d) { return gateDay(main, d, () => _viewDay(main, d)); };
const _viewPlayer = viewPlayer; viewPlayer = function (main, d, k) { return gateDay(main, d, () => _viewPlayer(main, d, k)); };

/* ---------- sau mỗi ngày học: gửi tiến độ và mời đúng lúc ---------- */
const _finishEx = finishEx;
finishEx = function (ex, d, k, sum, body) {
  const before = !!S.daily[S.lang + d.id];
  _finishEx(ex, d, k, sum, body);
  if (before || !S.daily[S.lang + d.id]) return;
  const doneN = Object.keys(S.done).length;
  track("day", { day: (d.wlabel || d.label) + (S.lang === "zh" ? " · Trung" : " · Anh"), doneN });
  const trial = d.demo || (d.week || 1) === 1, card = $(".endcard", body), L = dayLang(d), T = trialOf(L);
  if (trial && d.idx === 4 && T && T.used.includes(dayTrack(d)) && !T.done) { T.done = true; save(); }
  if (!trial || !card || planActive()) return;
  let html = "";
  if (d.idx === 4 && !tested(L)) {
    /* học thử theo trình độ tự chọn: xong tuần thì mời kiểm tra đầu vào; từ chối thì sang lớp nhóm, Weekend Live */
    card.insertAdjacentHTML("beforeend", `<div class="offmini"><b>Bạn đã xong tuần học thử!</b><span>Bước tiếp theo: làm bài kiểm tra đầu vào 10–15 phút để CES xếp đúng lộ trình cho bạn.</span>${nextStepHTML(L)}</div>`);
    bindSkip(card); return;
  }
  if (d.idx === 0 && !orderOf("lop-nhom")) html = `<div class="offmini"><b>Tối thứ 4 có lớp nhóm với giáo viên</b><span>Giáo viên sửa đúng lỗi bạn hay sai. Giá học thử ${fmtVND(SITE.trial.class)}.</span><a class="btn primary" href="#uu-dai">Giữ chỗ</a></div>`;
  else if (d.idx === 2 && !orderOf("weekend-live")) html = `<div class="offmini"><b>Thứ 7 này mang 3 câu khoá ra Weekend Live</b><span>Giao lưu với cộng đồng và người nước ngoài, có đồ uống. Vé học thử ${fmtVND(SITE.trial.live)} (giảm 50%).</span><a class="btn primary" href="#uu-dai">Giữ vé</a></div>`;
  else if (d.idx === 4 && d.demo) {
    /* tuần học thử HSK2, A2, B1 chưa có tuần 2: mời đăng ký chờ lớp của đúng lộ trình, chưa bán gói web */
    const t = trackOf(d.lang, d.track), done = S.waitDemo && S.waitDemo[d.demo];
    html = `<div class="offmini"><b>Bạn đã xong tuần học thử ${esc(t ? t.name + " (" + t.lv + ")" : "")}!</b><span>Lộ trình này đang mở lớp dần. Đăng ký chờ để CES báo bạn ngay khi có lớp, và thử lớp nhóm, Weekend Live với giá học thử.</span>
      <div class="row center"><button type="button" class="btn primary wlx"${done ? " disabled" : ""}>${done ? "Đã đăng ký chờ ✓" : "Đăng ký chờ lớp"}</button><a class="btn ghost" href="#uu-dai">Ưu đãi lớp nhóm, Weekend Live</a></div></div>`;
    card.insertAdjacentHTML("beforeend", html);
    const b = $(".wlx", card); if (b && !done) b.onclick = () => { S.waitDemo = Object.assign({}, S.waitDemo, { [d.demo]: true }); save(); sendSheet({ type: "waitlist", lang: d.lang === "zh" ? "Tiếng Trung" : "Tiếng Anh", track: t ? t.name + " (" + t.lv + ")" : d.demo }); b.disabled = true; b.textContent = "Đã đăng ký chờ ✓"; toast("CES sẽ báo bạn qua Zalo khi lớp mở."); };
    return;
  }
  else if (d.idx === 4) html = `<div class="offmini"><b>Bạn đã xong tuần học thử!</b><span>Chọn gói để học tiếp tuần 2 và các tuần sau.</span><a class="btn primary" href="#chon-goi">Chọn gói học tiếp</a></div>`;
  if (html) card.insertAdjacentHTML("beforeend", html);
};

/* ---------- định tuyến: Ưu đãi, Chọn gói; thẻ ưu đãi ở trang chủ và phòng Weekend Live ---------- */
ROOMS["uu-dai"] = "offers"; ROOMS["chon-goi"] = "plans";
const _viewLive = viewLive;
viewLive = function (main) { _viewLive(main); if (planActive()) return; const m = $(".roomv", main); if (!m) return; m.insertAdjacentHTML("beforeend", offerSection("live")); bindOffers(m, () => { main.innerHTML = ""; viewLive(main); }); };
(function () {
  const r0 = render;
  render = function () {
    const r = parseRoute();
    if (r.v === "offers" || r.v === "plans") { stopAudio(); renderTop(); renderSide(); const main = $("#main"); main.innerHTML = ""; (r.v === "offers" ? viewOffers : viewPlans)(main); main.focus({ preventScroll: true }); scrollTo(0, 0); return; }
    r0();
    { const T = trialOf(S.lang), bt = $("#bn-today"), t = T && trackOf(S.lang, T.track); if (!TEACHER && T && !T.done && bt && t.demo) bt.href = "#" + trialNext(S.lang, t); }
    if (r.v === "home" && !planActive()) {
      const h = $("#main"), first = h && h.firstElementChild, oc = orderOf("lop-nhom"), ol = orderOf("weekend-live");
      if (first && (!oc || !ol)) first.insertAdjacentHTML("afterend", `<section class="card2 pcta"><div><h2>Ưu đãi tuần học thử</h2><p>Lớp nhóm với giáo viên ${fmtVND(SITE.trial.class)} · Weekend Live ${fmtVND(SITE.trial.live)} (giảm 50%, có đồ uống).</p></div><a class="btn primary" href="#uu-dai">Xem ưu đãi</a></section>`);
      const T = trialOf(S.lang), t = T && trackOf(S.lang, T.track);
      if (first && T && T.done && !tested(S.lang)) { first.insertAdjacentHTML("afterend", `<section class="card2 pcta trialcta"><div><h2>Bạn đã xong tuần học thử</h2><p>Làm bài kiểm tra đầu vào 10–15 phút để CES xếp đúng lộ trình cho bạn.</p></div>${nextStepHTML(S.lang)}</section>`); bindSkip(h); }
      else if (first && T && !T.done && t.demo) first.insertAdjacentHTML("afterend", `<section class="card2 pcta trialcta"><div><h2>Bạn đang học thử ${esc(t.name)} (${esc(t.lv)})</h2><p>${esc(t.note)}</p></div><a class="btn primary" href="#${trialNext(S.lang, t)}">${ICON.play} Tiếp tục học thử</a></section>`);
    }
  };
})();
/* mỗi ngày báo "đã vào học" một lần, để CES biết ai đang học, ai nghỉ */
(function () { const t = new Date().toDateString(); if (S.seenDay !== t && S.profile) { S.seenDay = t; save(); track("seen", { lang: S.lang === "zh" ? "Tiếng Trung" : "Tiếng Anh" }); } if (SITE.sheetUrl && ((S.orders || []).some(o => o.status !== "Đã thu") || (S.plan && S.plan.until < Date.now() + 864e5))) refreshStatus(); })();
