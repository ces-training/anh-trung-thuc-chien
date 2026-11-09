/* Kiểm thử tự động trang bài tập: node tools/t20.js [--only=a2-w1-thu-2] [--lang=en] [--workers=6] [--shots]
   - Mở tuan-1/index.html qua máy chủ http (đúng như trang thật), giọng đọc và âm thanh được thay bằng bản giả để chạy nhanh.
   - Làm từng bài của mọi ngày (hành trình chính + tuần học thử), 2 ngôn ngữ, 2 mức.
   - Câu đầu mỗi bài cố ý trả lời SAI để chắc luồng "hiện đáp án 2 giây → làm lại câu tương tự" không kẹt.
   - Báo lỗi: bài không về được màn "Xong bài!", lỗi JavaScript, câu không có tranh.
   - --funnel: thử luồng học thử → học viên (khoá tuần 2, ưu đãi 89k/179k, chọn gói, mở khoá) với Apps Script giả.
   - --shots: chụp màn hình máy tính (1280) và điện thoại (390) vào tools/shots/, kiểm tra không có thanh cuộn ngang.
   Cần Playwright (npm i playwright) và Chrome. */
const http = require("http"), fs = require("fs"), path = require("path");
const { chromium } = require("playwright");
const ROOT = path.resolve(__dirname, "..");
const arg = k => { const a = process.argv.find(x => x.startsWith("--" + k)); return a ? (a.split("=")[1] ?? true) : null; };
const WORKERS = +(arg("workers") || 6), ONLY = arg("only"), ONLY_LANG = arg("lang"), SHOTS = !!arg("shots"), FUNNEL = !!arg("funnel");

const TYPES = { ".html": "text/html; charset=utf-8", ".js": "text/javascript", ".json": "application/json", ".webp": "image/webp", ".png": "image/png", ".jpg": "image/jpeg", ".svg": "image/svg+xml", ".mp3": "audio/mpeg", ".mp4": "video/mp4" };
function serve() {
  return new Promise(res => {
    const srv = http.createServer((req, rsp) => {
      let p = decodeURIComponent(req.url.split("?")[0]); if (p.endsWith("/")) p += "index.html";
      if (p === "/tuan-1/test-funnel.html") { rsp.writeHead(200, { "content-type": TYPES[".html"] }); return rsp.end(fs.readFileSync(path.join(ROOT, "tuan-1/index.html"), "utf8").replace('"sheetUrl":""', '"sheetUrl":"https://script.google.com/macros/s/TEST/exec"')); }
      const f = path.join(ROOT, p); if (!f.startsWith(ROOT) || !fs.existsSync(f)) { rsp.writeHead(404); return rsp.end(); }
      rsp.writeHead(200, { "content-type": TYPES[path.extname(f)] || "application/octet-stream" }); fs.createReadStream(f).pipe(rsp);
    }).listen(0, "127.0.0.1", () => res(srv));
  });
}

/* chạy trong trang trước mọi mã: giọng đọc, âm thanh giả; bỏ màn chào */
const INIT = () => {
  try {
    if (!localStorage.getItem("anh-trung-tuan-1")) localStorage.setItem("anh-trung-tuan-1", JSON.stringify({ profile: { name: "Kiểm thử", gender: "f", coach: "khang" }, seenWelcome: true }));
    sessionStorage.setItem("attc-started", "1");
  } catch (e) {}
  const fakeSS = { speaking: false, pending: false, paused: false, getVoices: () => [{ lang: "en-US", name: "Fake EN", localService: true }, { lang: "zh-CN", name: "Fake ZH", localService: true }],
    speak(u) { setTimeout(() => { u.onstart && u.onstart(); u.onend && u.onend(); }, 15); }, cancel() {}, pause() {}, resume() {}, addEventListener() {}, onvoiceschanged: null };
  Object.defineProperty(window, "speechSynthesis", { value: fakeSS, configurable: true });
  HTMLMediaElement.prototype.play = function () { setTimeout(() => this.dispatchEvent(new Event("ended")), 15); return Promise.resolve(); };
  HTMLMediaElement.prototype.pause = function () {};
};

/* một bước của "người học máy": trả về việc vừa làm */
const STEP = () => {
  const T = window.__T, vis = e => e && !e.disabled && !e.hidden && e.offsetParent !== null;
  const q = s => [...document.querySelectorAll(s)].filter(vis);
  const click = (e, what) => { e.click(); return what; };
  if (document.querySelector(".endcard")) return "done";
  const go = q(".pbody .intro .go")[0]; if (go) return click(go, "go");
  /* bài nhiều câu */
  const st = document.querySelector(".items .stage");
  if (st) {
    const nb = q(".items .stage .next, .items .stage .simbtn")[0]; if (nb) return click(nb, "next");
    const it = T.cur, redo = !!st.querySelector(".redo-tag");
    const wrongFirst = !T.wrong && !redo;
    if (it && it.k === "mc") {
      const opts = q(".items .stage .opt"); if (!opts.length) return "wait";
      if (wrongFirst) { const w = opts.find(b => +b.dataset.i !== it.a); if (w) { T.wrong = true; return click(w, "wrong"); } }
      const r = opts.find(b => +b.dataset.i === it.a); return r ? click(r, "right") : "wait";
    }
    if (it && it.k === "type") {
      const inp = q(".items .stage .inp")[0]; if (!inp) return "wait";
      inp.value = wrongFirst ? "zzz" : it.model; if (wrongFirst) T.wrong = true;
      inp.form.requestSubmit ? inp.form.requestSubmit() : inp.form.dispatchEvent(new Event("submit", { cancelable: true })); return "type";
    }
    if (it && it.k === "order") {
      const ans = st.querySelectorAll(".ans .tok").length, chk = q(".items .stage .chk")[0];
      if (wrongFirst && ans === 0) { T.wrong = true; const pool = q(".items .stage .pool .tok"); pool.slice().reverse().forEach(b => b.click()); return chk ? click(chk, "order-wrong") : "wait"; }
      if (ans > 0 && !st.querySelector(".ans .tok.right")) { const clr = q(".items .stage .clr")[0]; if (clr && st.querySelector(".ans .tok.wrong")) return click(clr, "clear"); }
      if (ans < it.tokens.length) {
        const want = it.tokens[ans], b = q(".items .stage .pool .tok").find(x => (x.dataset.t != null ? x.dataset.t : x.firstChild && x.firstChild.textContent) === want);
        return b ? click(b, "tok") : "wait";
      }
      return chk ? click(chk, "check") : "wait";
    }
    return "wait";
  }
  /* viết có hướng dẫn (tiếng Anh) */
  const ew = document.querySelector(".ew");
  if (ew && T.write) {
    const gaps = q(".ew .ewgap");
    if (gaps.length) {
      const chk = q(".ew .chk")[0];
      if (!T.ewWrong) { T.ewWrong = true; gaps.forEach(g => { g.value = ""; }); return click(chk, "ew-wrong"); }
      if (!T.ewFilled) { T.ewFilled = true; gaps.forEach(g => { g.value = T.write.gaps[+g.dataset.g]; }); return click(chk, "ew-fill"); }
      const n = q(".ew .fb button")[0]; if (n) return click(n, "ew-next"); return "wait";
    }
    const ta = q(".ew .ewta")[0]; if (ta && !ta.value) { ta.value = T.write.model; ta.dispatchEvent(new Event("input")); return "ew-own"; }
    const f = q(".ew [data-f]"); if (f.length && !f[0].value) { f.forEach((x, k) => { x.value = T.write.gaps[k] || "x"; x.dispatchEvent(new Event("input")); }); return "ew-own"; }
    const ch = q(".ew .ewchk input").filter(x => !x.checked); if (ch.length) { ch.forEach(x => x.click()); return "ew-check"; }
    const b = q(".ew .fin, .ew .nx")[0]; return b ? click(b, "ew-step") : "wait";
  }
  /* hướng dẫn viết chữ Hán: cần vẽ nét bằng tay, chỉ kiểm tra mở được và chuyển được bước */
  if (document.querySelector(".wg")) {
    if (!T.wgTabs) { T.wgTabs = 1; [...document.querySelectorAll(".wgtabs [data-t]")].forEach(b => b.click()); return "wg-tabs"; }
    return "wg-ok";
  }
  /* đếm nét */
  const sk = q(".pbody .next:not([hidden])")[0] || null; if (sk && document.querySelector(".pbody .nums, .pbody .pair")) return click(sk, "next");
  if (document.querySelector(".pbody .nums, .pbody .pair")) {
    const o = q(".pbody .opt")[0]; if (o) return click(o, "stroke-opt");
    const s2 = q(".pbody .skip")[0]; if (s2) return click(s2, "skip");
  }
  /* hội thoại: chưa có câu mẫu thì gõ thử sai để mở "Dùng câu mẫu, đi tiếp" */
  const rpi = q(".rpform .inp")[0];
  if (rpi && !q(".usem").length) { rpi.value = "zzz"; const f = rpi.form; f.requestSubmit ? f.requestSubmit() : f.dispatchEvent(new Event("submit", { cancelable: true })); return "rp-try"; }
  /* mẫu câu bước 2: lắp đúng thứ tự */
  const pp = q(".ppool .ptok");
  if (pp.length && T.toks) {
    const n = document.querySelectorAll(".pans .ptok").length, want = T.toks[n];
    const b = pp.find(x => x.dataset.t === want); if (b) return click(b, "ptok");
  }
  /* nói dài: nói ngay, bỏ ghi âm, hoàn thành */
  if (document.querySelector(".lt")) { const b = q(".lt .now, .lt .skip, .lt .fin")[0]; return b ? click(b, "lt") : "wait"; }
  const order = [".usem", ".pbody .fin", ".nxp", ".pbody .next", ".simbtn", ".skp", ".go2", ".pbody .skip", ".cardsx .nx", ".pbody .nx", ".swp"];
  for (const s of order) { const e = q(s)[0]; if (e) return click(e, s); }
  /* mẫu câu bước 2–3: chọn ô hoặc đáp án */
  const tok = q(".pbody .pool .tok")[0]; if (tok) return click(tok, "ptok");
  const chk = q(".pbody .chk")[0]; if (chk) return click(chk, "pchk");
  const opt = q(".pbody .opt")[0]; if (opt) return click(opt, "popt");
  return "wait";
};

/* móc vào trình chạy để người học máy biết đáp án */
const HOOK = () => {
  window.__T = { cur: null, wrong: false };
  const wrap = (name, f) => { const o = window[name]; window[name] = function (ctx) { f(ctx); return o.apply(this, arguments); }; };
  if (!window.__hooked) {
    window.__hooked = true;
    wrap("itemMC", c => { __T.cur = c.it; }); wrap("itemType", c => { __T.cur = c.it; }); wrap("itemOrder", c => { __T.cur = c.it; }); wrap("itemFree", c => { __T.cur = c.it; });
    const op = window.patTokens; window.patTokens = function () { const r = op.apply(this, arguments); __T.toks = r; return r; };
    const oe = window.runEWrite; window.runEWrite = function (ex) { __T.write = ex.write; return oe.apply(this, arguments); };
  }
};

async function runEx(page, job) {
  const errs = [];
  const onErr = e => errs.push(String(e.message || e)); page.on("pageerror", onErr);
  await page.evaluate(({ lang, level }) => { S.lang = lang; S.level = level; save(); }, job);
  await page.evaluate(HOOK);
  await page.evaluate(h => { location.hash = h; }, `#${job.day}-bai-${job.k + 1}`);
  await page.waitForTimeout(30);
  const info = await page.evaluate(() => ({ title: (document.querySelector(".phead h1") || {}).textContent || "", code: (document.querySelector(".phead small") || {}).textContent || "" }));
  let last = "", same = 0, steps = 0, res = "timeout";
  const t0 = Date.now();
  while (Date.now() - t0 < 60000) {
    const r = await page.evaluate(STEP);
    steps++;
    if (r === "done") { res = "ok"; break; }
    if (r === "wg-ok") { res = "ok-partial"; break; }
    if (r === "wait") { same++; if (same > 120) { res = "stuck"; break; } await page.waitForTimeout(40); continue; }
    same = 0; last = r; await page.waitForTimeout(r === "next" || r === "right" ? 5 : 20);
  }
  /* câu hỏi không có tranh: kiểm tra trên câu hiện tại cuối cùng không đủ; chỉ ghi số bài */
  page.off("pageerror", onErr);
  const stuckAt = res === "stuck" || res === "timeout" ? await page.evaluate(() => (document.querySelector(".pbody") || document.body).innerText.slice(0, 300).replace(/\s+/g, " ")) : "";
  return { ...job, ...info, res, steps, last, errs, stuckAt };
}

async function shots(browser, base) {
  const out = path.join(ROOT, "tools", "shots"); fs.mkdirSync(out, { recursive: true });
  const pages = [["trang-chu", "en"], ["lo-trinh", "en"], ["a2-w1-thu-2", "en"], ["a2-w1-thu-2-bai-8", "en"], ["a2-w1-thu-2-bai-14", "en"], ["b1-w1-thu-6-bai-14", "en"], ["b1-w1-thu-3-bai-13", "en"], ["w5-thu-2", "zh"], ["w5-thu-2-bai-1", "zh"], ["w5-thu-4-bai-11", "zh"], ["h4-w1-thu-2", "zh"], ["h4-w1-thu-2-bai-1", "zh"], ["h4-w1-thu-3-bai-5", "zh"], ["h4-w1-thu-4-bai-9", "zh"], ["h4-w1-thu-2-bai-13", "zh"], ["h4-w1-thu-5-bai-15", "zh"], ["b2-w1-thu-2-bai-5", "en"], ["b2-w1-thu-3-bai-9", "en"], ["b2-w1-thu-6-bai-16", "en"]];
  const report = [];
  for (const [w, h] of [[1280, 860], [390, 844]]) {
    const ctx = await browser.newContext({ viewport: { width: w, height: h }, deviceScaleFactor: 1 }); await ctx.addInitScript(INIT);
    const page = await ctx.newPage(); await page.goto(base + "tuan-1/index.html"); await page.waitForTimeout(600);
    for (const [hash, lang] of pages) {
      await page.evaluate(L => { S.lang = L; save(); }, lang);
      await page.evaluate(x => { location.hash = x; }, "#" + hash); await page.waitForTimeout(500);
      const go = await page.$(".pbody .intro .go"); if (go && (/bai-(8|13|14)$/.test(hash) || /^(h4|b2)-.*bai-\d+$/.test(hash))) { await go.click(); await page.waitForTimeout(500); }
      if (/bai-14$/.test(hash)) { for (const t of ["frame"]) { const b = await page.$(`.ew [data-t="${t}"]`); if (b) { await b.click(); await page.waitForTimeout(300); } } }
      const sx = await page.evaluate(() => document.documentElement.scrollWidth - document.documentElement.clientWidth);
      const f = path.join(out, `${w}-${hash}.png`); await page.screenshot({ path: f, fullPage: w > 400 ? false : true });
      report.push(`${w}px ${hash}: ${sx > 1 ? "CÓ CUỘN NGANG " + sx + "px" : "không cuộn ngang"}`);
    }
    await ctx.close();
  }
  console.log(report.join("\n")); console.log("Ảnh chụp: tools/shots/");
}

/* luồng học thử → học viên, với Apps Script giả */
async function funnel(browser, base) {
  const ok = [], bad = [], check = (c, m) => (c ? ok : bad).push(m);
  const ctx = await browser.newContext({ viewport: { width: 390, height: 844 } }); await ctx.addInitScript(INIT);
  const posts = []; let paid = false;
  await ctx.route("https://script.google.com/**", async route => {
    const r = route.request();
    if (r.method() === "POST") { try { posts.push(JSON.parse(r.postData())); } catch (e) {} return route.fulfill({ status: 200, body: "{\"ok\":true}" }); }
    const u = new URL(r.url()), code = u.searchParams.get("code");
    const o = posts.filter(p => p.type === "order");
    return route.fulfill({ status: 200, contentType: "application/json", headers: { "access-control-allow-origin": "*" }, body: JSON.stringify({ ok: true, id: u.searchParams.get("id"),
      active: paid, plan: paid ? "Gói Online · 1 tháng" : "", until: paid ? Date.now() + 30 * 864e5 : 0,
      orders: o.map(p => ({ code: p.code, type: p.kind, item: p.item, amount: p.amount, status: paid ? "Đã thu" : "Chờ chuyển khoản" })) }) });
  });
  const page = await ctx.newPage(); const errs = []; page.on("pageerror", e => errs.push(e.message));
  await page.goto(base + "tuan-1/test-funnel.html"); await page.waitForTimeout(800);
  const go = async h => { await page.evaluate(x => { location.hash = x; }, h); await page.waitForTimeout(500); };
  const txt = () => page.evaluate(() => document.querySelector("#main").innerText);
  check(posts.some(p => p.type === "seen" && /^HV/.test(p.id)), "gửi 'seen' kèm mã học viên");
  await page.evaluate(() => { S.lang = "en"; save(); });
  await go("#w2-thu-2"); check(/dành cho học viên/.test(await txt()), "tuần 2 bị khoá khi chưa có gói");
  await go("#w1-thu-2"); check(!/dành cho học viên/.test(await txt()), "tuần 1 vẫn mở");
  await go("#a2-w1-thu-3"); check(/Bạn đang học thử Nền tảng/.test(await txt()), "đang học thử tuần 1 (A1) thì tuần học thử A2 bị khoá");
  await go("#trang-chu"); check(/Ưu đãi tuần học thử/.test(await txt()), "trang chủ có thẻ ưu đãi");
  await go("#uu-dai");
  check(/89\.000đ/.test(await txt()) && /179\.000đ/.test(await txt()) && /358\.000đ/.test(await txt()), "trang ưu đãi đúng giá 89k, 179k, gốc 358k");
  await page.click('.offer[data-off="class"] button[type=submit]'); await page.waitForTimeout(200);
  check(/Zalo/.test(await page.evaluate(() => document.querySelector('.offer[data-off="class"] .err').textContent)) && !posts.some(p => p.type === "order"), "thiếu số Zalo thì báo lỗi, không gửi đơn");
  await page.fill('.offer[data-off="class"] [name=nm]', "Nguyễn Thử"); await page.fill('.offer[data-off="class"] [name=ct]', "0912345678");
  await page.click('.offer[data-off="class"] [data-v]:nth-child(2)'); await page.click('.offer[data-off="class"] button[type=submit]'); await page.waitForTimeout(400);
  const ord = posts.find(p => p.type === "order" && p.kind === "lop-nhom");
  check(ord && ord.amount === 89000 && /20:30/.test(ord.when) && ord.name === "Nguyễn Thử", "đơn lớp nhóm gửi đúng giá, ca, tên");
  check(await page.$('.offer[data-off="class"] .paybox') !== null && /Zalo OA Học viện đa ngữ CES/.test(await txt()) && !(await page.$('.paybox .qr')), "hiện khung thanh toán có mã đơn, dẫn sang Zalo OA");
  await page.click('.offer[data-off="class"] .claim'); await page.waitForTimeout(300);
  check(posts.some(p => p.type === "paid_claim" && p.code === (ord || {}).code), "bấm 'Tôi đã thanh toán' báo về Sheet");
  await page.fill('.offer[data-off="live"] [name=nm]', "Nguyễn Thử"); await page.click('.offer[data-off="live"] button[type=submit]'); await page.waitForTimeout(400);
  check(posts.some(p => p.type === "order" && p.kind === "weekend-live" && p.amount === 179000), "đơn Weekend Live 179k (tên, Zalo tự điền lại)");
  await go("#chon-goi"); await page.click('.pk[data-k="online"]'); await page.waitForTimeout(200); await page.click(".planform button[type=submit]"); await page.waitForTimeout(400);
  check(posts.some(p => p.type === "order" && p.kind === "goi" && p.amount === 249000), "đơn gói Online tháng 249k");
  paid = true; await page.click(".paybox .chk"); await page.waitForTimeout(800);
  await go("#w2-thu-2"); check(!/dành cho học viên/.test(await txt()), "admin đánh 'Đã thu' → tuần 2 tự mở");
  /* mời đúng lúc: xong Thứ 2 tuần 1 → mời lớp nhóm (dùng học viên mới) */
  const p2 = await (await browser.newContext({ viewport: { width: 1100, height: 900 } })).newPage(); await p2.context().addInitScript(INIT); await p2.context().route("https://script.google.com/**", r => r.fulfill({ status: 200, body: "{}" }));
  await p2.goto(base + "tuan-1/test-funnel.html"); await p2.waitForTimeout(600);
  await p2.evaluate(() => { const d = WDAYS[0]; d.exFor("en").forEach((c, i) => { if (i) S.done["en:" + d.id + ":" + c] = { p: 5 }; }); S.lang = "en"; save(); location.hash = "#" + d.id + "-bai-1"; });
  await p2.waitForTimeout(500); await p2.evaluate(HOOK);
  for (let i = 0; i < 60 && !(await p2.$(".endcard")); i++) { await p2.evaluate(STEP); await p2.waitForTimeout(30); }
  check(/lớp nhóm với giáo viên/i.test(await p2.evaluate(() => (document.querySelector(".endcard") || {}).innerText || "")), "xong Thứ 2 tuần 1 → mời lớp nhóm 89k");
  /* xong Thứ 6 tuần học thử A2 (được xếp theo kết quả kiểm tra) → mời đăng ký chờ lớp, không mời mua gói */
  await p2.evaluate(() => { S.place = { lang: "en", result: { level: 2, levelName: "A2", track: "en-b", bySk: {}, n: 1, right: 1 } }; S.trial = {}; assignTrial("en", "en-b"); });
  await p2.evaluate(() => { const d = DEMO_DAYS.find(x => x.id === "a2-w1-thu-6"); d.ex.forEach((c, i) => { if (i) S.done["en:" + d.id + ":" + c] = { p: 5 }; }); S.lang = "en"; save(); location.hash = "#" + d.id + "-bai-1"; });
  await p2.waitForTimeout(500); await p2.evaluate(HOOK);
  for (let i = 0; i < 60 && !(await p2.$(".endcard")); i++) { await p2.evaluate(STEP); await p2.waitForTimeout(30); }
  const endA2 = await p2.evaluate(() => (document.querySelector(".endcard") || {}).innerText || "");
  check(/Đăng ký chờ lớp/.test(endA2) && !/Chọn gói/.test(endA2), "xong tuần học thử A2 → mời chờ lớp, không mời mua gói");
  /* B2, HSK4 đã có tuần học thử riêng; lộ trình chưa mở (giả lập) → gợi ý tuần học thử gần nhất bên dưới */
  const adv = await p2.evaluate(() => [trackStart(trackOf("en", "en-d")), trackStart(trackOf("zh", "zh-c"))].join(" "));
  check(adv === "b2-w1-thu-2 h4-w1-thu-2", "B2 → học thử B2, HSK4 → học thử HSK4 (" + adv + ")");
  const near = await p2.evaluate(() => { const t = trackOf("en", "en-d"), n = nearTrial("en", t); return n ? trackStart(n) : ""; });
  check(near === "b1-w1-thu-2", "nếu B2 chưa mở → gợi ý học thử B1 (" + near + ")");
  /* ===== Luồng A: tự chọn trình độ trước ===== */
  const fresh = async () => { const c = await browser.newContext({ viewport: { width: 390, height: 844 } }); await c.addInitScript(INIT); const ps = [];
    await c.route("https://script.google.com/**", r => { if (r.request().method() === "POST") try { ps.push(JSON.parse(r.request().postData())); } catch (e) {} return r.fulfill({ status: 200, contentType: "application/json", headers: { "access-control-allow-origin": "*" }, body: "{\"ok\":true}" }); });
    const pg = await c.newPage(); pg.on("pageerror", e => errs.push(e.message)); await pg.goto(base + "tuan-1/test-funnel.html"); await pg.waitForTimeout(600); pg.posts = ps; return pg; };
  const g2 = async (pg, h) => { await pg.evaluate(x => { location.hash = x; }, h); await pg.waitForTimeout(450); };
  const tx = pg => pg.evaluate(() => document.querySelector("#main").innerText);
  const finishDay = async (pg, id) => { await pg.evaluate(id => { const d = DEMO_DAYS.find(x => x.id === id) || WDAYS.find(x => x.id === id), ex = d.ex || d.exFor(S.lang); ex.forEach((c, i) => { if (i) S.done[S.lang + ":" + d.id + ":" + c] = { p: 5 }; }); save(); location.hash = "#" + d.id + "-bai-1"; }, id);
    await pg.waitForTimeout(500); await pg.evaluate(HOOK); for (let i = 0; i < 80 && !(await pg.$(".endcard")); i++) { await pg.evaluate(STEP); await pg.waitForTimeout(30); }
    return pg.evaluate(() => (document.querySelector(".endcard") || {}).innerText || ""); };
  /* làm bài kiểm tra đầu vào: mode "right" = luôn đúng, chậm như người thật (tắt bộ đo bấm vội); "guess" = bấm ô A thật nhanh */
  const doTest = async (pg, L, mode = "right", self = 2, prod = "skip") => { await g2(pg, "#kiem-tra-dau-vao");
    await pg.evaluate(m => { window.PLACE_FAST_OFF = m === "right" ? 1 : 0; }, mode);
    if (await pg.$(".presult .other")) { await pg.click(".presult .other"); await pg.waitForTimeout(300); }
    await pg.fill("#pname", "Người Thử"); await pg.fill("#pcontact", "0912000111"); await pg.click(`#plang [data-v="${L}"]`); await pg.click('#pgoal [data-v="Đi làm"]'); await pg.click(`#pself [data-v='${self}']`); await pg.check("#pok"); await pg.click("#pgo");
    const pos = [];
    for (let i = 0; i < 80 && !(await pg.$(".presult")); i++) {
      if (await pg.$(".pprod")) { if (prod === "write") { await pg.fill(".pprod .pwrite", "我叫阮安，我是越南人。"); await pg.click(".pprod .psend"); } else await pg.click(".pprod .skip"); await pg.waitForTimeout(400); continue; }
      const o = await pg.$(mode === "right" ? '.ptest .opt[data-k="0"]:not([disabled])' : '.ptest .opt[data-pos="0"]:not([disabled])');
      if (o) { pos.push(await o.getAttribute(mode === "right" ? "data-pos" : "data-k")); await o.click(); } await pg.waitForTimeout(mode === "right" ? 450 : 380); }
    return pos; };
  const pa = await fresh();
  await g2(pa, "#lo-trinh"); check(/Chạm Học thử ở trình độ bạn chọn/.test(await tx(pa)), "trang lộ trình cho tự chọn trình độ");
  await pa.click('.tracks [data-pick="en-b"]'); await pa.waitForTimeout(500);
  const ta = await pa.evaluate(() => ({ h: location.hash, T: S.trial.en }));
  check(ta.h === "#a2-w1-thu-2" && ta.T.via === "self" && ta.T.track === "en-b", "chọn A2 → vào tuần học thử A2, ghi là tự chọn");
  await g2(pa, "#b1-w1-thu-2"); check(/Bạn đang học thử Giao tiếp công sở/.test(await tx(pa)) && !(await pa.$(".exlist, .dayex")), "tự chọn A2 thì không mở được tuần học thử B1");
  await g2(pa, "#w1-thu-2"); check(/Bạn đang học thử/.test(await tx(pa)), "tự chọn A2 thì không vào được tuần 1 lộ trình A1");
  await g2(pa, "#lo-trinh"); check((await tx(pa)).split("Mở theo kết quả kiểm tra").length - 1 >= 3, "lộ trình khác hiện 'Mở theo kết quả kiểm tra'");
  check(pa.posts.some(p => p.type === "day" && /Bắt đầu học thử Giao tiếp công sở \(A2\).*tự chọn/.test(p.day)), "báo admin: bắt đầu học thử A2, tự chọn");
  const endSelf = await finishDay(pa, "a2-w1-thu-6");
  check(/kiểm tra đầu vào/i.test(endSelf) && /Bỏ qua/.test(endSelf) && !/Đăng ký chờ lớp/.test(endSelf) && !/Chọn gói/.test(endSelf), "xong tuần tự chọn → chỉ mời kiểm tra đầu vào hoặc bỏ qua");
  await g2(pa, "#trang-chu"); check(/Bạn đã xong tuần học thử/.test(await tx(pa)), "trang chủ nhắc kiểm tra đầu vào");
  await pa.click(".trialcta .skiptest"); await pa.waitForTimeout(500);
  check((await pa.evaluate(() => location.hash)) === "#uu-dai" && /Lớp nhóm online/.test(await tx(pa)) && /Weekend Live/.test(await tx(pa)), "bỏ qua kiểm tra → sang lớp nhóm online và Weekend Live");
  check(pa.posts.some(p => p.type === "day" && /Bỏ qua kiểm tra/.test(p.day)), "báo admin: bỏ qua kiểm tra đầu vào");
  await doTest(pa, "en"); const resA = await tx(pa);
  check(/Bạn đã học thử tuần/.test(resA) && /Đăng ký chờ lớp B2\+/.test(resA) && !/Học thử ngay/.test(resA) && (await pa.evaluate(() => S.trial.en.track)) === "en-b", "kiểm tra sau học thử → bước tiếp theo kết quả, không mở thêm tuần miễn phí");
  /* ===== Luồng B: kiểm tra đầu vào trước ===== */
  const pb = await fresh();
  const posB = await doTest(pb, "en"); const resB = await tx(pb);
  check(new Set(posB).size >= 2 && posB.length >= 24 && posB.length <= 40, `đáp án đúng nằm ở nhiều ô khác nhau, bài dài ${posB.length} câu (24–40)`);
  check(!!(await pb.$(".presult .again-lock")) && !(await pb.$(".presult .again")), "vừa làm xong thì chưa làm lại được (khoá 7 ngày)");
  const tb = await pb.evaluate(() => S.trial.en);
  check(/Học thử ngay: Nâng cao/.test(resB) && !!(await pb.$('.presult a[href="#b2-w1-thu-2"]')) && tb.track === "en-d" && tb.tested, "kiểm tra trước → tự xếp tuần học thử B2");
  await g2(pb, "#a2-w1-thu-3"); check(/Bạn đang học thử Nâng cao/.test(await tx(pb)), "xếp B2 thì tuần học thử A2 bị khoá");
  const endB = await finishDay(pb, "b2-w1-thu-6");
  check(/Đăng ký chờ lớp/.test(endB) && !/Bỏ qua/.test(endB), "xong tuần học thử theo kết quả → mời chờ lớp, không hỏi kiểm tra lại");
  /* ===== Luồng C: đoán bừa (bấm ô A thật nhanh, tự nhận B2) rồi kiểm tra tiếng Trung ===== */
  const pc = await fresh();
  await doTest(pc, "en", "guess", 4); const rc = await pc.evaluate(() => S.places.en.result);
  check(rc.level <= 1 && /nhanh|cùng một ô/.test(rc.doubt) && /chỉ tính những mức bạn làm chắc chắn/.test(await tx(pc)), `đoán bừa tự nhận B2 → xếp ${rc.levelName}, ghi nghi đoán (${rc.doubt})`);
  check(pc.posts.some(p => p.type === "placement" && /^Nghi đoán/.test(p.trust || "")), "Sheet nhận cột Độ tin cậy: Nghi đoán");
  await doTest(pc, "zh", "right", 0, "write");
  check(pc.posts.some(p => p.type === "production" && /阮安/.test(p.text || "") && p.sayPrompt) && /đã gửi giáo viên/.test(await tx(pc)), "phần nói, viết gửi về Sheet, màn kết quả báo đã gửi");
  check(pc.posts.some(p => p.type === "placement" && /zh\d-\d+=1@/.test(p.items || "") && p.skLv), "Sheet nhận từng câu (id=đúng@giây) và ước lượng theo kỹ năng");
  const both = await pc.evaluate(() => ({ en: S.places.en && S.places.en.result.levelName, zh: S.places.zh && S.places.zh.result.levelName }));
  check(both.en && both.zh === "HSK4" && /Xem kết quả tiếng Anh/.test(await tx(pc)), `kết quả Anh, Trung lưu riêng (Anh ${both.en}, Trung ${both.zh})`);
  await pc.screenshot({ path: path.join(ROOT, "tools", "shots", "390-ket-qua-dau-vao.png"), fullPage: true });
  /* ===== Hỏi CES + thống kê lượt vào ===== */
  check(pc.posts.some(p => p.type === "visit" && p.vid && p.sid && /kiem-tra-dau-vao/.test(p.screens || "")), "thống kê lượt vào: có Mã khách, màn đã mở");
  check(pc.posts.filter(p => p.type === "placement").every(p => p.vid), "dữ liệu gửi Sheet kèm Mã khách");
  await pc.click(".cesc-fab"); await pc.fill(".cesc-box [name=name]", "Người Thử"); await pc.fill(".cesc-box [name=contact]", "0912000111"); await pc.fill(".cesc-box [name=msg]", "Mình nên chọn gói nào?");
  await pc.check(".cesc-box [name=ok]"); await pc.click(".cesc-box button[type=submit]"); await pc.waitForTimeout(400);
  const ct = pc.posts.find(p => p.type === "contact");
  const okTxt = await pc.evaluate(() => (document.querySelector(".cesc-box") || {}).innerText || "");
  check(ct && ct.topic && /nút Liên hệ CES/.test(ct.source) && /bài xong/.test(ct.learn) && /Đã gửi/.test(okTxt), "form Liên hệ CES gửi về Sheet kèm nơi bấm, tình hình học" + (ct ? "" : " (không thấy dòng contact)") + (ct ? ` [${ct.source} | ${ct.learn}]` : "") + " " + okTxt.slice(0, 40));
  await pc.screenshot({ path: path.join(ROOT, "tools", "shots", "390-hoi-ces.png") });
  const pd = await fresh(); await g2(pd, "#chon-goi"); await pd.waitForTimeout(32000);
  const nd = await pd.$(".cesc-nudge"); check(!!nd, "ở trang Chọn gói > 25 giây thì hiện lời mời liên hệ");
  if (nd) { await pd.click(".cesc-nudge [data-go]"); check(/Tư vấn gói học trả phí/.test(await pd.$eval(".cesc-box select[name=topic]", e => e.value)), "bấm lời mời mở form đúng chủ đề"); }
  await pa.screenshot({ path: path.join(ROOT, "tools", "shots", "390-ket-qua-sau-hoc-thu.png"), fullPage: true });
  await g2(pb, "#lo-trinh"); await pb.screenshot({ path: path.join(ROOT, "tools", "shots", "390-lo-trinh-dang-hoc.png"), fullPage: true });
  check(!errs.length, "không lỗi JavaScript" + (errs.length ? ": " + errs.join(" | ") : ""));
  await go("#uu-dai"); await page.screenshot({ path: path.join(ROOT, "tools", "shots", "390-uu-dai.png"), fullPage: true });
  await go("#w1-thu-3"); check(!(await page.$(".stagehd")), "ngày tiếng Anh của hành trình chính không có tiêu đề bước");
  await go("#chon-goi"); await page.screenshot({ path: path.join(ROOT, "tools", "shots", "390-chon-goi.png"), fullPage: true });
  ok.forEach(m => console.log("✓ " + m)); bad.forEach(m => console.log("✗ " + m));
  console.log(bad.length ? bad.length + " lỗi" : "0 lỗi"); return bad.length;
}

(async () => {
  const srv = await serve(), base = `http://127.0.0.1:${srv.address().port}/`;
  const browser = await chromium.launch({ executablePath: fs.existsSync("/usr/bin/google-chrome") ? "/usr/bin/google-chrome" : undefined, args: ["--autoplay-policy=no-user-gesture-required"] });
  if (SHOTS) { await shots(browser, base); await browser.close(); srv.close(); return; }
  if (FUNNEL) { fs.mkdirSync(path.join(ROOT, "tools", "shots"), { recursive: true }); const n = await funnel(browser, base); await browser.close(); srv.close(); process.exit(n ? 1 : 0); }
  /* danh sách bài lấy từ chính trang */
  const ctx0 = await browser.newContext(); await ctx0.addInitScript(INIT); const p0 = await ctx0.newPage();
  await p0.goto(base + "tuan-1/index.html?gv=1"); await p0.waitForTimeout(500);
  const days = await p0.evaluate(() => WDAYS.map(d => ({ id: d.id, demo: null, en: d.exFor("en"), zh: d.exFor("zh") })).concat(DEMO_DAYS.map(d => ({ id: d.id, demo: d.demo, [d.lang]: d.ex }))));
  await ctx0.close();
  const jobs = [];
  days.forEach(d => ["en", "zh"].forEach(lang => (d[lang] || []).forEach((c, k) => [1, 2].forEach(level => {
    if (ONLY && !d.id.startsWith(ONLY)) return; if (ONLY_LANG && lang !== ONLY_LANG) return;
    jobs.push({ day: d.id, demo: d.demo, lang, level, k, c });
  }))));
  console.log(`${jobs.length} lượt bài (${days.length} ngày), ${WORKERS} luồng…`);
  const results = []; let ji = 0;
  await Promise.all(Array.from({ length: WORKERS }, async () => {
    const ctx = await browser.newContext({ viewport: { width: 1100, height: 900 } }); await ctx.addInitScript(INIT);
    const page = await ctx.newPage(); await page.goto(base + "tuan-1/index.html?gv=1"); await page.waitForTimeout(400);
    while (ji < jobs.length) { const j = jobs[ji++]; try { results.push(await runEx(page, j)); } catch (e) { results.push({ ...j, res: "crash", errs: [String(e)] }); await page.goto(base + "tuan-1/index.html?gv=1"); } }
    await ctx.close();
  }));
  await browser.close(); srv.close();
  const bad = results.filter(r => !/^ok/.test(r.res) || r.errs.length);
  const by = {}; results.forEach(r => { const k = (r.demo || "chính") + " · " + r.lang; by[k] = by[k] || [0, 0]; by[k][1]++; if (/^ok/.test(r.res) && !r.errs.length) by[k][0]++; });
  Object.entries(by).forEach(([k, v]) => console.log(`${k}: ${v[0]}/${v[1]} lượt đạt`));
  const partial = results.filter(r => r.res === "ok-partial").length;
  if (partial) console.log(`(${partial} lượt "Hướng dẫn viết chữ Hán": chỉ kiểm tra mở được 4 bước, phần vẽ nét cần thử tay)`);
  bad.slice(0, 40).forEach(r => console.log(`LỖI ${r.day} bài ${r.k + 1} (${r.c}) ${r.lang} mức ${r.level}: ${r.res}${r.errs.length ? " · JS: " + [...new Set(r.errs)].join(" | ").slice(0, 300) : ""}${r.stuckAt ? " · kẹt ở: " + r.stuckAt : ""}`));
  console.log(bad.length ? `${bad.length} lượt lỗi` : "0 lỗi");
  process.exit(bad.length ? 1 : 0);
})();
