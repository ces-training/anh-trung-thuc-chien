/* Trang chủ: khởi động CES Connect (nút Hỏi CES, thống kê mục đã đọc, lời mời liên hệ). Được build2.py chèn vào index.html. */
(function () {
  var C = window.SITE_CONFIG || {};
  if (!window.CESConnect) return;
  /* đặt tên cho nút để thống kê "đã bấm gì" */
  Array.prototype.forEach.call(document.querySelectorAll("a.btn, button.btn"), function (b) { if (!b.getAttribute("data-track")) b.setAttribute("data-track", (b.textContent || "").trim().replace(/\s+/g, " ").slice(0, 40)); });
  CESConnect.init({ endpoint: C.formEndpoint, zaloUrl: C.zaloUrl, hotline: C.hotline, page: "trang-chu",
    sections: ["top", "cach-hoc", "weekend-live", "lo-trinh", "doanh-nghiep", "hoc-phi", "nguoi-sang-lap", "cam-nhan", "hoi-dap", "dang-ky", "lien-he"] });
  /* nút gửi câu hỏi ở chân trang */
  var w = document.querySelector("#lien-he .wrap");
  if (w) { var b = document.createElement("button"); b.type = "button"; b.className = "btn btn-primary"; b.textContent = "Gửi câu hỏi cho CES"; b.setAttribute("data-track", "chân trang: gửi câu hỏi"); b.style.margin = "12px 0";
    b.onclick = function () { CESConnect.open({ source: "chân trang trang chủ", topic: "Khác" }); }; w.insertBefore(b, w.querySelector("#bao-mat")); }
  /* lời mời: đọc học phí ≥ 8 giây · mở ≥ 2 câu hỏi đáp · ở trang ≥ 2 phút mà chưa đăng ký. Không hiện khi đang điền form. */
  var faq = 0;
  Array.prototype.forEach.call(document.querySelectorAll("#hoi-dap details"), function (d) {
    d.addEventListener("toggle", function () { if (!d.open) return; faq++; var s = d.querySelector("summary"); CESConnect.track("hỏi đáp: " + (s ? s.textContent.trim().slice(0, 40) : ""));
      if (faq >= 2) setTimeout(function () { ask("doc-hoi-dap", { title: "Câu hỏi của bạn chưa có ở đây?", text: "Gửi câu hỏi, CES trả lời qua Zalo trong giờ làm việc.", cta: "Gửi câu hỏi cho CES", form: { topic: "Khác", source: "lời mời: đọc hỏi đáp" } }); }, 1500); });
  });
  function busy() { var a = document.activeElement; return (a && a.closest && a.closest("form")) || !document.getElementById("done") || !document.getElementById("done").hidden; }
  function ask(id, o) { if (busy()) return; CESConnect.nudge(id, o); }
  setInterval(function () {
    if (document.visibilityState !== "visible") return;
    if (CESConnect.readSecs("hoc-phi") >= 8) ask("doc-hoc-phi", { title: "Chưa chắc gói nào hợp với bạn?", text: "Kể CES nghe mục tiêu và lịch của bạn, tư vấn viên gợi ý gói phù hợp trong 10 phút. Miễn phí, không bắt buộc đăng ký.", form: { topic: "Tư vấn gói học trả phí", source: "lời mời: đọc học phí" } });
    else if (CESConnect.activeSecs() >= 120) ask("o-lau-trang-chu", { title: "Bạn còn băn khoăn điều gì?", text: "Để lại Zalo, CES trả lời mọi câu hỏi về lộ trình, lịch học và học phí.", form: { topic: "Tư vấn gói học trả phí", source: "lời mời: xem trang chủ lâu" } });
  }, 3000);
})();
