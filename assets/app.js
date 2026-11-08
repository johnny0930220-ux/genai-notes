// 生成式 AI 課程筆記：搜尋、手機目錄、深淺色、本頁目錄高亮
(function () {
  var prefix = window.SITE_PREFIX || "";
  var root = document.documentElement;

  // 深淺色：記住使用者的選擇（存不了也沒關係）
  try {
    var saved = localStorage.getItem("theme");
    if (saved) root.setAttribute("data-theme", saved);
  } catch (e) {}
  var themeBtn = document.querySelector(".theme-btn");
  if (themeBtn) themeBtn.addEventListener("click", function () {
    var dark = root.getAttribute("data-theme")
      ? root.getAttribute("data-theme") === "dark"
      : matchMedia("(prefers-color-scheme: dark)").matches;
    var next = dark ? "light" : "dark";
    root.setAttribute("data-theme", next);
    try { localStorage.setItem("theme", next); } catch (e) {}
  });

  // 手機版目錄
  var menuBtn = document.querySelector(".menu-btn");
  if (menuBtn) menuBtn.addEventListener("click", function () {
    var open = document.body.classList.toggle("nav-open");
    menuBtn.setAttribute("aria-expanded", open ? "true" : "false");
  });

  // 搜尋：比對標題、摘要、關鍵字、內文
  var q = document.getElementById("q");
  var box = document.getElementById("results");
  var index = window.SEARCH_INDEX || [];
  function esc(s) { return s.replace(/[&<>"]/g, function (c) { return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]; }); }
  function search(term) {
    term = term.trim().toLowerCase();
    if (!term) { box.hidden = true; box.innerHTML = ""; return; }
    var hits = [];
    index.forEach(function (d) {
      var score = 0;
      if (d.t.toLowerCase().indexOf(term) > -1) score += 5;
      if (d.k.join(" ").toLowerCase().indexOf(term) > -1) score += 4;
      if (d.s.toLowerCase().indexOf(term) > -1) score += 2;
      var pos = d.x.toLowerCase().indexOf(term);
      if (pos > -1) score += 1;
      if (score) hits.push({ d: d, score: score, pos: pos });
    });
    hits.sort(function (a, b) { return b.score - a.score; });
    if (!hits.length) { box.innerHTML = '<li class="empty">找不到「' + esc(term) + '」</li>'; box.hidden = false; return; }
    box.innerHTML = hits.slice(0, 8).map(function (h) {
      var snip = h.pos > -1 ? h.d.x.substr(Math.max(0, h.pos - 18), 60) : h.d.s;
      return '<li><a href="' + prefix + h.d.u + '">' + esc(h.d.t) + "<small>" + esc(snip) + "</small></a></li>";
    }).join("");
    box.hidden = false;
  }
  if (q) {
    q.addEventListener("input", function () { search(q.value); });
    q.addEventListener("keydown", function (e) {
      if (e.key === "Escape") { q.value = ""; search(""); }
      if (e.key === "Enter") { var a = box.querySelector("a"); if (a) location.href = a.href; }
    });
    document.addEventListener("keydown", function (e) {
      if (e.key === "/" && document.activeElement !== q) { e.preventDefault(); q.focus(); }
    });
  }

  // 本頁目錄：捲動時標出目前段落
  var links = Array.prototype.slice.call(document.querySelectorAll(".toc a"));
  if (links.length && "IntersectionObserver" in window) {
    var map = {};
    links.forEach(function (a) { map[a.getAttribute("href").slice(1)] = a; });
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        if (en.isIntersecting) {
          links.forEach(function (a) { a.classList.remove("on"); });
          var a = map[en.target.id];
          if (a) a.classList.add("on");
        }
      });
    }, { rootMargin: "0px 0px -70% 0px" });
    Object.keys(map).forEach(function (id) {
      var el = document.getElementById(id);
      if (el) io.observe(el);
    });
  }
})();
