/* Kiểm thử tự động trang bài tập: node tools/t20.js [--only=a2-w1-thu-2] [--lang=en] [--workers=6] [--shots]
   - Mở tuan-1/index.html qua máy chủ http (đúng như trang thật), giọng đọc và âm thanh được thay bằng bản giả để chạy nhanh.
   - Làm từng bài của mọi ngày (hành trình chính + tuần học thử), 2 ngôn ngữ, 2 mức.
   - Câu đầu mỗi bài cố ý trả lời SAI để chắc luồng "hiện đáp án 2 giây → làm lại câu tương tự" không kẹt.
   - Báo lỗi: bài không về được màn "Xong bài!", lỗi JavaScript, câu không có tranh.
   - --shots: chụp màn hình máy tính (1280) và điện thoại (390) vào tools/shots/, kiểm tra không có thanh cuộn ngang.
   Cần Playwright (npm i playwright) và Chrome. */
const http = require("http"), fs = require("fs"), path = require("path");
const { chromium } = require("playwright");
const ROOT = path.resolve(__dirname, "..");
const arg = k => { const a = process.argv.find(x => x.startsWith("--" + k)); return a ? (a.split("=")[1] ?? true) : null; };
const WORKERS = +(arg("workers") || 6), ONLY = arg("only"), ONLY_LANG = arg("lang"), SHOTS = !!arg("shots");

const TYPES = { ".html": "text/html; charset=utf-8", ".js": "text/javascript", ".json": "application/json", ".webp": "image/webp", ".png": "image/png", ".jpg": "image/jpeg", ".svg": "image/svg+xml", ".mp3": "audio/mpeg", ".mp4": "video/mp4" };
function serve() {
  return new Promise(res => {
    const srv = http.createServer((req, rsp) => {
      let p = decodeURIComponent(req.url.split("?")[0]); if (p.endsWith("/")) p += "index.html";
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
        const want = it.tokens[ans], b = q(".items .stage .pool .tok").find(x => x.firstChild && x.firstChild.textContent === want);
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
  const pages = [["trang-chu", "en"], ["lo-trinh", "en"], ["a2-w1-thu-2", "en"], ["a2-w1-thu-2-bai-8", "en"], ["a2-w1-thu-2-bai-14", "en"], ["b1-w1-thu-6-bai-14", "en"], ["b1-w1-thu-3-bai-13", "en"], ["w5-thu-2", "zh"], ["w5-thu-2-bai-1", "zh"], ["w5-thu-4-bai-11", "zh"]];
  const report = [];
  for (const [w, h] of [[1280, 860], [390, 844]]) {
    const ctx = await browser.newContext({ viewport: { width: w, height: h }, deviceScaleFactor: 1 }); await ctx.addInitScript(INIT);
    const page = await ctx.newPage(); await page.goto(base + "tuan-1/index.html"); await page.waitForTimeout(600);
    for (const [hash, lang] of pages) {
      await page.evaluate(L => { S.lang = L; save(); }, lang);
      await page.evaluate(x => { location.hash = x; }, "#" + hash); await page.waitForTimeout(500);
      const go = await page.$(".pbody .intro .go"); if (go && /bai-(8|13|14)$/.test(hash)) { await go.click(); await page.waitForTimeout(500); }
      if (/bai-14$/.test(hash)) { for (const t of ["frame"]) { const b = await page.$(`.ew [data-t="${t}"]`); if (b) { await b.click(); await page.waitForTimeout(300); } } }
      const sx = await page.evaluate(() => document.documentElement.scrollWidth - document.documentElement.clientWidth);
      const f = path.join(out, `${w}-${hash}.png`); await page.screenshot({ path: f, fullPage: w > 400 ? false : true });
      report.push(`${w}px ${hash}: ${sx > 1 ? "CÓ CUỘN NGANG " + sx + "px" : "không cuộn ngang"}`);
    }
    await ctx.close();
  }
  console.log(report.join("\n")); console.log("Ảnh chụp: tools/shots/");
}

(async () => {
  const srv = await serve(), base = `http://127.0.0.1:${srv.address().port}/`;
  const browser = await chromium.launch({ executablePath: fs.existsSync("/usr/bin/google-chrome") ? "/usr/bin/google-chrome" : undefined, args: ["--autoplay-policy=no-user-gesture-required"] });
  if (SHOTS) { await shots(browser, base); await browser.close(); srv.close(); return; }
  /* danh sách bài lấy từ chính trang */
  const ctx0 = await browser.newContext(); await ctx0.addInitScript(INIT); const p0 = await ctx0.newPage();
  await p0.goto(base + "tuan-1/index.html"); await p0.waitForTimeout(500);
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
    const page = await ctx.newPage(); await page.goto(base + "tuan-1/index.html"); await page.waitForTimeout(400);
    while (ji < jobs.length) { const j = jobs[ji++]; try { results.push(await runEx(page, j)); } catch (e) { results.push({ ...j, res: "crash", errs: [String(e)] }); await page.goto(base + "tuan-1/index.html"); } }
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
