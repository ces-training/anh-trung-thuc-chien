/* ============ TUẦN NÂNG CAO (Trung HSK3 → HSK4, Anh B2): Nói dài, Nghe điền, dạng U/W/V nâng cao, bính âm chỉ ở từ mới ============ */
Object.assign(PTS, { X: 20, Y: 10 });
Object.assign(COURSE_MINS, { X: 5, Y: 3 });
Object.assign(TINT, { X: "sun", Y: "green" });
Object.assign(TYPE_ICON, { X: TYPE_ICON.C || TYPE_ICON.E, Y: TYPE_ICON.B || TYPE_ICON.E });
const ADV_RULES = {
  Y: "Nghe cả đoạn (bấm Nghe, nghe 1–2 lần), rồi điền từng ô của ghi chú. Đáp án là đúng từ, số trong bài nghe, thường không quá 3 từ.",
  X: "Đọc đề và các ý gợi ý, chuẩn bị 1 phút (ghi vài từ khoá), rồi nói liền 1–2 phút. Xong thì nghe lại giọng mình, tự chấm theo danh sách và so với bài mẫu.",
  U: { zh: "Hai từ gần nghĩa thường khác nhau ở loại từ (động từ hay tính từ) và từ đi kèm. Đọc cả câu, xem chỗ trống cần loại từ nào rồi mới chọn.", en: "Biến đổi từ: xem chỗ trống cần loại từ gì (danh từ, động từ, tính từ, trạng từ) dựa vào từ đứng trước và sau, rồi chọn dạng đúng." },
  W: "Tìm câu mở đoạn (giới thiệu chủ đề), rồi nối các câu bằng từ nối và đại từ (因为…所以, 但是, 这/它; however, this, as a result). Câu kết thường có kết luận hoặc kết quả.",
  V: { zh: "Viết theo 4 bước: đọc bài mẫu, điền khung, tự viết bài của bạn, tự kiểm tra. Đếm chữ Hán để bài đủ độ dài như đề yêu cầu.", en: "Viết theo 4 bước: đọc bài mẫu, điền khung, tự viết bài của bạn, tự kiểm tra theo tiêu chí band (ý, mạch lạc, từ vựng, ngữ pháp)." }
};
const ADV_HOW = {
  Y: ["Bấm Nghe cả đoạn, nghe 1–2 lần, ghi nhanh số và tên riêng.", "Điền từng ô (tiếng Trung: chọn đáp án đúng).", "Sai thì xem đáp án, cuối bài làm lại câu tương tự."],
  X: ["Đọc đề, các ý cần nói và cụm hữu ích; chuẩn bị 1 phút.", "Bấm 🎤 và nói liền 1–2 phút theo đồng hồ.", "Nghe lại, tự chấm theo danh sách, rồi so với bài mẫu."],
  U: ["Đọc cả câu và nghĩa trong ngoặc.", "Xem chỗ trống cần loại từ nào, chọn từ đúng.", "Sai thì đọc giải thích về khác nhau giữa các từ."],
  W: ["Đọc hết các câu trước.", "Chạm các câu theo đúng thứ tự thành một đoạn văn.", "Bấm Kiểm tra; câu viền đỏ là sai chỗ."],
  V: ["Bước 1: đọc và nghe bài mẫu.", "Bước 2: điền khung, Bước 3: tự viết bài của bạn.", "Bước 4: tự kiểm tra theo danh sách, so với bài mẫu."]
};
const ADV_TIPS = {
  Y: ["Đọc các ô trước khi nghe để đoán loại thông tin cần điền (số, ngày, tên).", "Đáp án hay được nhắc lại hoặc sửa lại trong bài: nghe đến hết câu."],
  X: ["Mỗi ý nói 2–3 câu: ý chính, lý do, ví dụ.", "Dùng từ nối để bài nói liền mạch; đừng dừng lâu để tìm từ, dùng cách nói đơn giản hơn.", "Nghe lại bản ghi, ghi 1 lỗi muốn sửa rồi nói lại lần hai."],
  U: ["Học từ theo cụm (提高质量, 增加数量; make a decision, significantly better), không học từ lẻ."],
  W: ["Gạch chân từ nối và đại từ: chúng cho biết câu nào đứng trước, câu nào đứng sau."],
  V: ["Lập dàn ý 3 dòng trước khi viết.", "Đọc lại một lượt chỉ để soát ngữ pháp, một lượt chỉ để soát từ nối."]
};
const ADV_NAME = { zh: { T: "Thẻ nghe", Q: "Nghe chọn nghĩa", S: "Nghe cảnh", B: "Nghe hiểu", Y: "Nghe điền", C: "Nhại theo", P: "Mẫu câu", I: "Hội thoại", X: "Nói dài", U: "Từ gần nghĩa", E: "Từ vựng", G: "Ngữ pháp", J: "Đọc", H: "Dạng đề HSK4", W: "Sắp xếp đoạn", V: "Viết theo dạng đề" },
  en: { T: "Thẻ nghe", Q: "Nghe chọn nghĩa", S: "Nghe cảnh", B: "Nghe hiểu", Y: "Nghe điền", C: "Nhại theo", P: "Mẫu câu", I: "Hội thoại", X: "Nói dài", U: "Biến đổi từ", E: "Từ vựng", G: "Ngữ pháp", J: "Đọc", H: "Dạng đề IELTS, TOEIC", W: "Sắp xếp đoạn", V: "Viết theo dạng đề" } };
const advDay = () => { const r = parseRoute(); return r.d && r.d.adv ? r.d : null; };
const _typeName = typeName;
typeName = function (c) { const d = advDay(); if (d && ADV_NAME[S.lang][c]) return "Bước " + ZH_STAGE[c] + " · " + ADV_NAME[S.lang][c]; return _typeName(c); };
const _tipsFor = tipsFor;
tipsFor = function (code) { const d = advDay(); return d && ADV_TIPS[code] ? ADV_TIPS[code] : _tipsFor(code); };
/* cách làm: playerShell đọc HOW_ZH / HOW_EN / HOW theo mã bài, nên thêm vào đó khi đang ở tuần nâng cao */
function advRule(code) { const r = ADV_RULES[code]; return r && typeof r === "object" ? r[S.lang] : r; }
const _buildEx = buildEx;
buildEx = function (day, code) {
  const ex = _buildEx(day, code), d = cday(S.lang, day);
  if (d && d.adv) { const r = advRule(code[0]); if (r) ex.rule = r; ex.advHow = ADV_HOW[code[0]] || null; }
  return ex;
};

/* bính âm chỉ hiện ở từ mới của tuần nâng cao tiếng Trung */
const NEWW = new Set();
DEMO_KEYS.forEach(k => { const W = COURSE_DEMO[k]; if (W.lang === "zh" && W.adv) W.days.forEach(d => d.cards.forEach(c => String(c.w).split(/\s*\/\s*|\s+/).forEach(w => w && NEWW.add(w)))); });
const PYNEW = () => document.documentElement.dataset.pymode === "new";
const _glossHTML = glossHTML;
glossHTML = function (text, noPy) {
  const h = _glossHTML(text, noPy);
  return NEWW.size ? h.replace(/<span class="rw" data-w="([^"]+)"/g, (m, w) => NEWW.has(w) ? `<span class="rw nw" data-w="${w}"` : m) : h;
};
/* tra từ ở mọi chữ Hán mới hiện ra (kể cả chữ trong nút: chỉ rê chuột mới hiện bong bóng) */
try {
  new MutationObserver(() => {
    document.querySelectorAll("#main .rw:not([data-gb])").forEach(w => {
      w.dataset.gb = 1; const inChip = !!w.closest("button,.tok,.ptok,.opt");
      w.addEventListener("mouseenter", () => showGloss(w));
      w.addEventListener("mouseleave", () => setTimeout(() => { if (GTIP && !GTIP.matches(":hover")) GTIP.hidden = true; }, 300));
      if (!inChip) w.addEventListener("click", e => { e.stopPropagation(); showGloss(w); });
    });
  }).observe(document.getElementById("main"), { childList: true, subtree: true });
} catch (e) {}

/* ---------- X · Nói dài 1–2 phút ---------- */
function runLongturn(ex, body, finish) {
  const L = S.lang, zh = L === "zh", lt = ex.lt;
  let phase = "cue", prepT = null, speakT = null, secs = 0, url = null, said = "", recOn = false, rec = null, chunks = [], sr = null, ticks = 0;
  const txt = s => zh ? glossHTML(s, true) : `<span lang="en">${esc(s)}</span>`;
  const count = s => zh ? (String(s).match(/[一-鿿]/g) || []).length : (String(s).match(/[A-Za-z']+/g) || []).length;
  const box = el(`<div class="lt"><div class="ltbody"></div></div>`); body.appendChild(box);
  const lb = $(".ltbody", box);
  const clear = () => { clearInterval(prepT); clearInterval(speakT); prepT = speakT = null; };
  function stopRec() { recOn = false; try { sr && sr.stop(); } catch (e) {} if (rec && rec.state !== "inactive") { rec.onstop = () => { try { url = URL.createObjectURL(new Blob(chunks, { type: rec.mimeType || "audio/webm" })); } catch (e) {} if (phase === "check") draw(); }; try { rec.stop(); } catch (e) {} } }
  async function startRec() {
    chunks = []; said = ""; url = null; recOn = true;
    if (CAN_REC) { try { const s = await getMic(); rec = new MediaRecorder(s); rec.ondataavailable = e => e.data.size && chunks.push(e.data); rec.start(); } catch (e) { rec = null; } }
    if (SR_API) {
      const go = () => { if (!recOn) return; try { sr = new SR_API(); sr.lang = zh ? "zh-CN" : "en-US"; sr.continuous = true; sr.interimResults = false;
        sr.onresult = e => { for (let i = e.resultIndex; i < e.results.length; i++) if (e.results[i].isFinal) said += (zh ? "" : " ") + e.results[i][0].transcript; const t = $(".ltlive", lb); if (t) t.textContent = said.trim().slice(-160); };
        sr.onend = () => { if (recOn) go(); }; sr.onerror = () => {}; sr.start(); } catch (e) {} };
      go();
    }
    return !!(rec || SR_API);
  }
  function draw() {
    if (phase === "cue") {
      lb.innerHTML = `<div class="ewbox"><p class="eyebrow">Đề bài</p><p class="ltcue">${txt(lt.cue)}</p><p class="small muted">${esc(lt.cueVi)}</p>
        <p class="lab">Bạn nên nói</p><ul class="facts">${lt.points.map((p, i) => `<li>${txt(p)}${lt.pointsVi && lt.pointsVi[i] ? `<small class="muted"> · ${esc(lt.pointsVi[i])}</small>` : ""}</li>`).join("")}</ul>
        <details class="mini"><summary>💡 Cụm hữu ích</summary><ul class="ewhints">${lt.useful.map(u => `<li>${txt(u)}</li>`).join("")}</ul></details></div>
        <div class="ewbox"><p class="lab">Chuẩn bị <b class="ltclock">${lt.prep || 60}</b> giây · ghi vài từ khoá</p><textarea class="ewta ltnote" style="min-height:90px" placeholder="Từ khoá của bạn…" aria-label="Ghi chú chuẩn bị"></textarea></div>
        <div class="row center"><button type="button" class="btn primary huge prep">⏱ Bắt đầu chuẩn bị</button><button type="button" class="btn ghost now">Nói ngay →</button></div>`;
      $(".now", lb).onclick = () => { clear(); phase = "speak"; draw(); };
      $(".prep", lb).onclick = e => { e.target.disabled = true; let t = lt.prep || 60; prepT = setInterval(() => { t--; const c = $(".ltclock", lb); if (c) c.textContent = t; if (t <= 0) { clear(); phase = "speak"; draw(); } }, 1000); };
      return;
    }
    if (phase === "speak") {
      const [mn, mx] = lt.speak || [60, 120];
      lb.innerHTML = `<div class="ewbox"><p class="ltcue small">${txt(lt.cue)}</p><p class="ltclock big" aria-live="polite">0:00</p><p class="small muted">Nói ít nhất ${Math.round(mn / 60 * 10) / 10} phút, tối đa ${Math.round(mx / 60 * 10) / 10} phút. Thanh màu xanh khi đủ thời gian.</p>
        <div class="ltbar"><i></i></div><p class="ltlive small muted"></p></div>
        <div class="row center"><button type="button" class="btn primary huge mic">🎤 Bắt đầu nói</button><button type="button" class="btn ghost skip">Bỏ qua, xem bài mẫu →</button></div>
        <p class="small muted center ltnomic" hidden>Trình duyệt này chưa ghi âm được. Bạn vẫn nói to theo đồng hồ, rồi bấm Dừng để tự chấm.</p>`;
      const mic = $(".mic", lb);
      mic.onclick = async () => {
        if (speakT) { clear(); stopRec(); phase = "check"; draw(); return; }
        const ok = await startRec(); if (!ok) $(".ltnomic", lb).hidden = false;
        mic.textContent = "⏹ Dừng"; secs = 0;
        speakT = setInterval(() => { secs++; const c = $(".ltclock", lb); if (c) c.textContent = Math.floor(secs / 60) + ":" + String(secs % 60).padStart(2, "0"); const b = $(".ltbar i", lb); if (b) { b.style.width = Math.min(100, secs / mx * 100) + "%"; b.classList.toggle("ok", secs >= mn); } if (secs >= mx) { clear(); stopRec(); phase = "check"; draw(); } }, 1000);
      };
      $(".skip", lb).onclick = () => { clear(); stopRec(); phase = "check"; draw(); };
      return;
    }
    const n = count(said), links = lt.useful.filter(u => said && said.toLowerCase().includes(String(u).toLowerCase().replace(/[.…]+$/, "").split(/[ ,，…]/)[0]));
    lb.innerHTML = `<div class="ewbox"><p class="eyebrow">Bạn đã nói</p><p><b>${Math.floor(secs / 60)}:${String(secs % 60).padStart(2, "0")}</b>${said ? ` · khoảng ${n} ${zh ? "chữ" : "từ"} máy nghe được · dùng ${links.length}/${lt.useful.length} cụm hữu ích` : ""}</p>
        ${said ? `<p class="small muted">Máy nghe được: “${esc(said.trim().slice(0, 400))}”${said.length > 400 ? "…" : ""}</p>` : ""}
        ${url ? `<button type="button" class="btn ghost small mine">▶ Nghe lại giọng bạn</button>` : ""}
        ${secs && secs < (lt.speak || [60])[0] ? `<p class="note small">Gần được rồi! Lần sau thử nói thêm một ý với ví dụ để đủ ${(lt.speak || [60])[0]} giây.</p>` : ""}</div>
      <div class="ewbox"><h3>Tự chấm</h3><ul class="ewchk">${lt.check.map((c, k) => `<li><label><input type="checkbox" data-c="${k}"><span>${esc(c)}</span></label></li>`).join("")}</ul></div>
      <details class="ewbox" open><summary>Bài nói mẫu</summary><p class="ewmodel">${txt(lt.model)}</p><p class="small muted">${esc(lt.modelVi)}</p><button type="button" class="btn ghost small pm">${ICON.play} Nghe bài mẫu</button></details>
      <div class="row center"><button type="button" class="btn ghost again2">↻ Nói lại</button><button type="button" class="btn primary huge fin">Hoàn thành bài</button></div>`;
    const mine = $(".mine", lb); if (mine) mine.onclick = () => playURL(url);
    $(".pm", lb).onclick = () => say(lt.model, L);
    $(".again2", lb).onclick = () => { phase = "speak"; draw(); };
    $(".fin", lb).onclick = () => { ticks = lb.querySelectorAll(".ewchk input:checked").length; stopAudio();
      finish({ total: 1, first: secs >= (lt.speak || [60])[0] && ticks >= Math.ceil(lt.check.length / 2) ? 1 : 0, repair: 0, extra: `Nói ${secs} giây · tự chấm ${ticks}/${lt.check.length} mục` }); };
  }
  draw();
}
/* đặt chế độ bính âm theo ngày đang mở: tuần nâng cao tiếng Trung chỉ hiện bính âm ở từ mới */
(function () { const r0 = render; render = function () { const r = parseRoute(); document.documentElement.dataset.pymode = r.d && r.d.adv && r.d.lang === "zh" ? "new" : ""; r0(); }; })();
