/* ============ CES CONNECT: hỏi admin, lời mời liên hệ, thống kê lượt vào (dùng chung trang chủ và trang học) ============
   Trang gọi CESConnect.init({ endpoint, zaloUrl, hotline, page: "trang-chu" | "trang-hoc", sections: [...id], ctx: () => ({...}) }).
   - Mã khách ẩn danh "atc-vid" lưu trên trình duyệt, dùng chung hai trang (cùng tên miền). Không ghi tên, số điện thoại
     trừ khi người dùng tự gửi form.
   - Mỗi lượt xem trang gửi 1 dòng "visit" (cập nhật khi rời trang, cùng mã lượt): nguồn, thiết bị, thời gian ở trang, độ cuộn,
     mục đã đọc (thấy ≥ 4 giây), màn đã mở (trang học), nút đã bấm, lời mời đã hiện, đã bấm.
   - Form "Hỏi CES": gửi dòng "contact" (Sheet tab Liên hệ + Zalo admin). Lời mời (nudge) hiện tối đa 1 lần mỗi loại, tắt được. */
(function () {
  const LS = {
    get(k, d) { try { const v = localStorage.getItem(k); return v == null ? d : JSON.parse(v); } catch (e) { return d; } },
    set(k, v) { try { localStorage.setItem(k, JSON.stringify(v)); } catch (e) {} }
  };
  const rid = p => p + Date.now().toString(36).slice(-5).toUpperCase() + Math.random().toString(36).slice(2, 6).toUpperCase();
  const esc = s => String(s == null ? "" : s).replace(/[&<>"]/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" })[c]);
  let C = {}, sess = null, sent = false, shownNow = false;

  function visitor() {
    let v = LS.get("atc-vid"); if (!v) { v = rid("K"); LS.set("atc-vid", v); LS.set("atc-vfirst", new Date().toISOString()); }
    return v;
  }
  function post(row, beacon) {
    if (!C.endpoint) { const q = LS.get("atc-outbox", []); q.push(row); LS.set("atc-outbox", q.slice(-30)); return false; }
    const body = JSON.stringify(row);
    try {
      if (beacon && navigator.sendBeacon) return navigator.sendBeacon(C.endpoint, new Blob([body], { type: "text/plain;charset=utf-8" }));
      fetch(C.endpoint, { method: "POST", mode: "no-cors", keepalive: body.length < 60000, headers: { "Content-Type": "text/plain;charset=utf-8" }, body });
      return true;
    } catch (e) { return false; }
  }

  /* ---------- thống kê một lượt xem ---------- */
  function startSession() {
    const qs = {}; try { new URLSearchParams(location.search).forEach((v, k) => qs[k] = v); } catch (e) {}
    const n = (LS.get("atc-visits", 0) || 0) + 1; LS.set("atc-visits", n);
    let ref = ""; try { ref = document.referrer ? new URL(document.referrer).hostname : ""; } catch (e) {}
    if (ref === location.hostname) ref = "(trong web)";
    sess = { sid: rid("L"), start: Date.now(), active: 0, lastAct: Date.now(), maxScroll: 0, read: {}, seenMs: {}, screens: [], clicks: [], nudges: {},
      src: qs.utm_source || ref || "(gõ trực tiếp)", camp: qs.utm_campaign || "", nth: n,
      device: /Mobi|Android|iPhone/i.test(navigator.userAgent) ? "Điện thoại" : /iPad|Tablet/i.test(navigator.userAgent) ? "Máy tính bảng" : "Máy tính",
      inApp: /Zalo|FBAN|FBAV|Messenger|Instagram/i.test(navigator.userAgent) ? "trong app " + ((navigator.userAgent.match(/Zalo|FBAN|FBAV|Messenger|Instagram/i) || [""])[0]) : "" };
    /* thời gian thật sự xem: chỉ tính khi tab đang mở và có thao tác trong 60 giây gần nhất */
    const act = () => { sess.lastAct = Date.now(); };
    ["scroll", "click", "keydown", "touchstart", "mousemove"].forEach(e => addEventListener(e, act, { passive: true }));
    setInterval(() => { if (document.visibilityState === "visible" && Date.now() - sess.lastAct < 60000) sess.active += 5; }, 5000);
    addEventListener("scroll", () => { const h = document.documentElement, p = Math.round((h.scrollTop + innerHeight) / Math.max(h.scrollHeight, 1) * 100); if (p > sess.maxScroll) sess.maxScroll = Math.min(p, 100); }, { passive: true });
    /* mục đã đọc: phần tử có id trong C.sections, thấy ≥ 50% trong ≥ 4 giây */
    if (window.IntersectionObserver && C.sections && C.sections.length) {
      const on = {};
      const io = new IntersectionObserver(es => es.forEach(e => { const id = e.target.id; if (e.isIntersecting) on[id] = Date.now(); else if (on[id]) { sess.seenMs[id] = (sess.seenMs[id] || 0) + Date.now() - on[id]; delete on[id]; } }), { threshold: [0.35] });
      C.sections.forEach(id => { const el = document.getElementById(id); if (el) io.observe(el); });
      setInterval(() => { const t = Date.now(); Object.keys(on).forEach(id => { const ms = (sess.seenMs[id] || 0) + t - on[id]; if (ms >= 4000) sess.read[id] = Math.round(ms / 1000); }); Object.keys(sess.seenMs).forEach(id => { if (sess.seenMs[id] >= 4000) sess.read[id] = Math.round(sess.seenMs[id] / 1000); }); }, 2000);
    }
    /* trang học: màn đã mở theo hash (#lo-trinh, #chon-goi…) */
    const scr = () => { const h = (location.hash || "#trang-chu").replace(/^#/, "").split("/")[0] || "trang-chu"; const k = /^w\d|^[a-z]+\d?-thu-\d|^d-/.test(h) ? "bài học" : h; if (sess.screens[sess.screens.length - 1] !== k) sess.screens.push(k); };
    if (C.page === "trang-hoc") { scr(); addEventListener("hashchange", scr); }
    /* nút đã bấm: phần tử có data-track */
    document.addEventListener("click", e => { const t = e.target.closest && e.target.closest("[data-track]"); if (t) sess.clicks.push(t.getAttribute("data-track")); }, true);
    const flush = () => { if (document.visibilityState === "hidden") sendVisit(true); };
    document.addEventListener("visibilitychange", flush); addEventListener("pagehide", () => sendVisit(true));
    setTimeout(() => sendVisit(false), 8000); // ghi lượt sớm (người thoát nhanh vẫn được tính), cập nhật khi rời trang
  }
  function visitRow() {
    const ctx = C.ctx ? (() => { try { return C.ctx() || {}; } catch (e) { return {}; } })() : {};
    return { type: "visit", sid: sess.sid, vid: visitor(), hv: ctx.id || "", page: C.page, first: LS.get("atc-vfirst", ""), nth: sess.nth, src: sess.src, camp: sess.camp,
      device: sess.device + (sess.inApp ? " · " + sess.inApp : ""), secs: Math.max(sess.active, Math.min(Math.round((Date.now() - sess.start) / 1000), 8)), scroll: sess.maxScroll,
      read: Object.entries(sess.read).map(([k, v]) => `${k} ${v}s`).join(", "), screens: sess.screens.join(" → "), clicks: [...new Set(sess.clicks)].join(", "),
      nudges: Object.entries(sess.nudges).map(([k, v]) => `${k}:${v}`).join(", "), learn: ctx.learn || "" };
  }
  function sendVisit(beacon) { if (!sess) return; post(visitRow(), beacon); sent = true; }

  /* ---------- form Hỏi CES ---------- */
  const TOPICS = ["Tư vấn gói học trả phí", "Lớp nhóm, Weekend Live", "Lộ trình, trình độ của tôi", "Doanh nghiệp, đăng ký nhóm", "Lỗi kỹ thuật trên web", "Khác"];
  function css() {
    if (document.getElementById("cesc-css")) return;
    const s = document.createElement("style"); s.id = "cesc-css";
    s.textContent = `.cesc-fab{position:fixed;right:max(14px,env(safe-area-inset-right,0px));bottom:calc(16px + env(safe-area-inset-bottom,0px));z-index:60;display:inline-flex;align-items:center;gap:8px;min-height:48px;padding:0 18px;border-radius:999px;border:0;background:#0E1730;color:#fff;font:700 16px/1 "Be Vietnam Pro",system-ui,sans-serif;box-shadow:0 8px 24px -8px rgba(14,23,48,.5);cursor:pointer}
.cesc-fab:focus-visible,.cesc-box button:focus-visible,.cesc-box a:focus-visible{outline:3px solid #FFD43B;outline-offset:2px}
.cesc-fab.low{bottom:calc(84px + env(safe-area-inset-bottom,0px))}
.cesc-back{position:fixed;inset:0;z-index:70;background:rgba(14,23,48,.55);display:flex;align-items:flex-end;justify-content:center;padding:12px}
@media(min-width:640px){.cesc-back{align-items:center}}
.cesc-box{background:#fff;color:#0E1730;border-radius:20px;width:100%;max-width:460px;max-height:calc(100dvh - 24px);overflow:auto;padding:20px;font:400 16px/1.5 "Be Vietnam Pro",system-ui,sans-serif;box-shadow:0 20px 50px rgba(0,0,0,.3)}
.cesc-box h2{margin:0 0 4px;font-size:22px;line-height:1.25}.cesc-box p{margin:0 0 10px;color:#515B70}
.cesc-box label{display:flex;flex-direction:column;gap:4px;font-weight:700;font-size:15px;margin:10px 0 0}
.cesc-box input,.cesc-box select,.cesc-box textarea{font:500 16px "Be Vietnam Pro",system-ui,sans-serif;color:#0E1730;background:#F5F6FA;border:1.5px solid #DDE2EC;border-radius:12px;padding:10px 12px;width:100%;box-sizing:border-box}
.cesc-box textarea{min-height:90px;resize:vertical}.cesc-box .tick{flex-direction:row;align-items:flex-start;gap:8px;font-weight:500;color:#515B70}
.cesc-box .tick input{width:20px;height:20px;flex:none;margin-top:2px}
.cesc-row{display:flex;flex-wrap:wrap;gap:8px;margin-top:14px}.cesc-row .cesc-btn{flex:1 1 auto}
.cesc-btn{display:inline-flex;align-items:center;justify-content:center;min-height:46px;padding:0 16px;border-radius:12px;border:1.5px solid #DDE2EC;background:#fff;color:#0E1730;font:700 16px "Be Vietnam Pro",system-ui,sans-serif;text-decoration:none;cursor:pointer}
.cesc-btn.pri{background:#D3271E;border-color:#D3271E;color:#fff}.cesc-btn.zalo{background:#0068FF;border-color:#0068FF;color:#fff}
.cesc-err{color:#B42318;font-weight:600;min-height:1.2em;margin-top:8px}
.cesc-nudge{position:fixed;left:50%;transform:translateX(-50%);bottom:calc(16px + env(safe-area-inset-bottom,0px));z-index:65;width:min(520px,calc(100% - 24px));background:#0E1730;color:#fff;border-radius:18px;padding:14px 16px;font:500 16px/1.45 "Be Vietnam Pro",system-ui,sans-serif;box-shadow:0 14px 34px -10px rgba(14,23,48,.6)}
.cesc-nudge.low{bottom:calc(84px + env(safe-area-inset-bottom,0px))}
.cesc-nudge b{display:block;font-size:17px;margin-bottom:2px}.cesc-nudge .cesc-row{margin-top:10px}.cesc-nudge .cesc-btn{min-height:42px}
.cesc-nudge .cesc-btn.ghost{background:transparent;color:#fff;border-color:rgba(255,255,255,.35)}
@media (prefers-color-scheme: dark){:root:not([data-theme="light"]) .cesc-box{background:#131B31;color:#EEF2FA}:root:not([data-theme="light"]) .cesc-box p{color:#A9B3C7}:root:not([data-theme="light"]) .cesc-box input,:root:not([data-theme="light"]) .cesc-box select,:root:not([data-theme="light"]) .cesc-box textarea{background:#0B1020;color:#EEF2FA;border-color:#283553}:root:not([data-theme="light"]) .cesc-btn:not(.pri):not(.zalo){background:#18223C;color:#EEF2FA;border-color:#283553}}
:root[data-theme="dark"] .cesc-box{background:#131B31;color:#EEF2FA}:root[data-theme="dark"] .cesc-box p{color:#A9B3C7}:root[data-theme="dark"] .cesc-box input,:root[data-theme="dark"] .cesc-box select,:root[data-theme="dark"] .cesc-box textarea{background:#0B1020;color:#EEF2FA;border-color:#283553}`;
    document.head.appendChild(s);
  }
  function open(opt) {
    opt = opt || {}; css(); closeNudge();
    const me = LS.get("atc-me", {}), back = document.createElement("div"); back.className = "cesc-back"; back.setAttribute("role", "dialog"); back.setAttribute("aria-modal", "true"); back.setAttribute("aria-labelledby", "cesc-h");
    const topic = opt.topic && TOPICS.includes(opt.topic) ? opt.topic : TOPICS[0];
    back.innerHTML = `<div class="cesc-box"><h2 id="cesc-h">${esc(opt.title || "Hỏi CES")}</h2><p>${esc(opt.lead || "Để lại Zalo, tư vấn viên CES nhắn hoặc gọi bạn trong giờ làm việc (thường trong 24 giờ). Miễn phí, không bắt buộc đăng ký.")}</p>
      <form novalidate><label>Họ tên<input name="name" autocomplete="name" value="${esc(me.name || "")}" required></label>
      <label>Số Zalo hoặc điện thoại<input name="contact" inputmode="tel" autocomplete="tel" value="${esc(me.contact || "")}" required></label>
      <label>Bạn muốn hỏi về<select name="topic">${TOPICS.map(t => `<option${t === topic ? " selected" : ""}>${t}</option>`).join("")}</select></label>
      <label>Câu hỏi của bạn (không bắt buộc)<textarea name="msg" placeholder="${esc(opt.placeholder || "Ví dụ: Mình đi làm, tối mới rảnh, nên chọn gói nào?")}"></textarea></label>
      <label>Liên hệ lúc nào tiện<select name="when"><option>Lúc nào cũng được</option><option>Buổi sáng</option><option>Buổi trưa</option><option>Buổi tối</option><option>Chỉ nhắn Zalo, đừng gọi</option></select></label>
      <input name="web" tabindex="-1" autocomplete="off" style="position:absolute;left:-9999px" aria-hidden="true">
      <label class="tick"><input type="checkbox" name="ok" ${me.contact ? "checked" : ""}> Tôi đồng ý để CES liên hệ tư vấn về khóa học.</label>
      <div class="cesc-err" role="alert"></div>
      <div class="cesc-row"><button class="cesc-btn pri" type="submit">Gửi cho CES</button><button class="cesc-btn" type="button" data-x>Đóng</button></div>
      ${C.zaloUrl ? `<div class="cesc-row"><a class="cesc-btn zalo" href="${esc(C.zaloUrl)}" target="_blank" rel="noopener" data-track="zalo-trong-form">Hoặc nhắn thẳng Zalo OA</a></div>` : ""}</form></div>`;
    document.body.appendChild(back);
    const f = back.querySelector("form"), F = n => f.elements.namedItem(n), err = back.querySelector(".cesc-err"), close = () => { back.remove(); removeEventListener("keydown", onKey); if (opt.onClose) opt.onClose(); };
    const onKey = e => { if (e.key === "Escape") close(); }; addEventListener("keydown", onKey);
    back.addEventListener("click", e => { if (e.target === back || e.target.hasAttribute("data-x")) close(); });
    setTimeout(() => (F("name").value ? F("msg") : F("name")).focus(), 50);
    if (sess) sess.clicks.push("mở form: " + (opt.source || "nút Hỏi CES"));
    f.addEventListener("submit", ev => {
      ev.preventDefault(); err.textContent = "";
      const name = F("name").value.trim(), contact = F("contact").value.trim(), digits = contact.replace(/[^\d]/g, "");
      if (!name) { err.textContent = "Bạn nhập họ tên giúp CES nhé."; return F("name").focus(); }
      if (digits.length < 9) { err.textContent = "Số Zalo hoặc điện thoại chưa đúng (ít nhất 9 chữ số)."; return F("contact").focus(); }
      if (!F("ok").checked) { err.textContent = "Bạn đánh dấu đồng ý để CES liên hệ nhé."; return F("ok").focus(); }
      if (F("web").value) return close();
      LS.set("atc-me", { name, contact });
      const ctx = C.ctx ? (() => { try { return C.ctx() || {}; } catch (e) { return {}; } })() : {};
      const ok = post({ type: "contact", time: new Date().toISOString(), vid: visitor(), id: ctx.id || "", hv: ctx.id || "", name, contact, topic: F("topic").value, msg: F("msg").value.trim().slice(0, 1500), when: F("when").value,
        source: opt.source || "nút Hỏi CES", page: C.page, learn: ctx.learn || "", visits: LS.get("atc-visits", 1), first: LS.get("atc-vfirst", "") });
      if (sess) sess.clicks.push("gửi form: " + (opt.source || "nút Hỏi CES"));
      LS.set("atc-contacted", new Date().toISOString());
      if (opt.onSent) opt.onSent({ name, contact, topic: F("topic").value }); if (C.onSent) C.onSent({ name, contact, topic: F("topic").value });
      back.querySelector(".cesc-box").innerHTML = `<h2>${ok ? "Đã gửi, cảm ơn bạn!" : "Đã lưu câu hỏi"}</h2><p>${ok ? `CES sẽ liên hệ ${esc(name.split(/\s+/).pop())} qua số ${esc(contact)} (${esc(F("when").value.toLowerCase())}).` : "Web chưa kết nối được với CES nên chưa gửi đi. " + (C.zaloUrl || C.hotline ? "Bạn nhắn Zalo hoặc gọi để được trả lời ngay nhé." : "Bạn thử lại sau nhé.")}</p>
        <div class="cesc-row">${C.zaloUrl ? `<a class="cesc-btn zalo" href="${esc(C.zaloUrl)}" target="_blank" rel="noopener">Nhắn Zalo OA</a>` : ""}${C.hotline ? `<a class="cesc-btn" href="tel:${esc(C.hotline.replace(/\s/g, ""))}">Gọi ${esc(C.hotline)}</a>` : ""}<button class="cesc-btn" type="button" data-x>Xong</button></div>`;
    });
    return back;
  }

  /* ---------- lời mời (mỗi loại hiện 1 lần, mỗi lượt xem tối đa 1 lời mời) ---------- */
  let nudgeEl = null;
  function closeNudge() { if (nudgeEl) { nudgeEl.remove(); nudgeEl = null; } }
  function nudge(id, o) {
    const seen = LS.get("atc-nudges", {});
    if (seen[id] || shownNow || LS.get("atc-contacted") || document.querySelector(".cesc-back")) return false;
    css(); shownNow = true; seen[id] = new Date().toISOString(); LS.set("atc-nudges", seen); if (sess) sess.nudges[id] = "hiện";
    nudgeEl = document.createElement("div"); nudgeEl.className = "cesc-nudge" + (C.low ? " low" : ""); nudgeEl.setAttribute("role", "status");
    nudgeEl.innerHTML = `<b>${esc(o.title)}</b>${esc(o.text)}<div class="cesc-row"><button type="button" class="cesc-btn pri" data-go>${esc(o.cta || "Để lại Zalo, CES gọi tư vấn")}</button><button type="button" class="cesc-btn ghost" data-no>Để sau</button></div>`;
    document.body.appendChild(nudgeEl);
    nudgeEl.querySelector("[data-go]").onclick = () => { if (sess) sess.nudges[id] = "bấm"; closeNudge(); open(Object.assign({ source: "lời mời: " + id }, o.form || {})); };
    nudgeEl.querySelector("[data-no]").onclick = () => { if (sess) sess.nudges[id] = "tắt"; closeNudge(); };
    return true;
  }

  function init(cfg) {
    C = Object.assign({}, cfg); visitor();
    css();
    if (C.fab !== false) {
      const b = document.createElement("button"); b.type = "button"; b.className = "cesc-fab" + (C.low ? " low" : ""); b.setAttribute("data-track", "nút Hỏi CES");
      b.innerHTML = `<svg viewBox="0 0 24 24" width="20" height="20" aria-hidden="true"><path d="M4 5h16v11H8l-4 4z" fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round"/></svg>Hỏi CES`;
      b.onclick = () => open({ source: "nút Hỏi CES (" + (C.page === "trang-hoc" ? (location.hash || "#trang-chu") : "trang chủ") + ")" });
      document.body.appendChild(b);
    }
    startSession();
    /* gửi lại những dòng đã lưu khi chưa có địa chỉ nhận (bản xem thử) — bỏ qua, chỉ giữ trên máy */
  }
  window.CESConnect = { init, open, nudge, track: k => sess && sess.clicks.push(k), visitor, row: () => sess && visitRow(), topics: TOPICS,
    readSecs: id => (sess && sess.read[id]) || 0, activeSecs: () => (sess ? sess.active : 0), contacted: () => !!LS.get("atc-contacted") };
})();
