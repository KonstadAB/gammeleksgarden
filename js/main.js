/* Gammeleksgården – gemensamt skript. Ingen extern beroende. */
(function () {
  "use strict";
  // Gamla länkar med index.html eller .html visas med ren adress.
  if (/\.html$/.test(location.pathname) && !/404\.html$/.test(location.pathname) && history.replaceState) history.replaceState(null, "", location.pathname.replace(/index\.html$/, "").replace(/\.html$/, "") + location.search + location.hash);
  // Texter som skrivs av skriptet. Översätts per språk via <script id="t"> i sidan.
  var T = { sending: "Skickar…", retry: "Försök igen", sendError: "Det gick inte att skicka just nu. Försök igen eller ring 073-505 24 45.", max: "Max", guest: "gäst", guests: "gäster", night: "natt", nights: "nätter", for: "för", chooseRoom: "Välj rum", copied: "Kopierat" };
  try { var tEl = document.getElementById("t"); if (tEl) { var tt = JSON.parse(tEl.textContent); for (var k in tt) T[k] = tt[k]; } } catch (e) {}
  var LOC = ({ sv: "sv-SE", en: "en-GB", da: "da-DK", nb: "nb-NO", fi: "fi-FI", de: "de-DE", nl: "nl-NL", fr: "fr-FR", es: "es-ES", it: "it-IT" })[document.documentElement.lang] || "sv-SE";

  var store = {
    get: function (k) { try { return JSON.parse(sessionStorage.getItem(k)); } catch (e) { return null; } },
    set: function (k, v) { try { sessionStorage.setItem(k, JSON.stringify(v)); } catch (e) {} }
  };

  // Meny på mobil
  var toggle = document.querySelector(".nav-toggle");
  var nav = document.getElementById("nav");
  if (toggle && nav) {
    toggle.addEventListener("click", function () {
      var open = nav.classList.toggle("open");
      toggle.setAttribute("aria-expanded", open ? "true" : "false");
    });
    // Esc stänger menyn och lämnar fokus på knappen
    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape" && nav.classList.contains("open")) { nav.classList.remove("open"); toggle.setAttribute("aria-expanded", "false"); toggle.focus(); }
    });
  }

  // Datumhjälp
  function iso(d) { return d.toISOString().slice(0, 10); }
  function addDays(d, n) { var x = new Date(d); x.setDate(x.getDate() + n); return x; }
  var today = new Date(); today.setHours(12, 0, 0, 0);

  // Bokningsrad (startsida m.fl.) → bokningssidan
  document.querySelectorAll("form.bookbar").forEach(function (f) {
    var a = f.querySelector("[name=arrive]"), d = f.querySelector("[name=depart]");
    var saved = store.get("geg-search");
    a.min = iso(today); d.min = iso(addDays(today, 1));
    a.value = (saved && saved.arrive >= iso(today)) ? saved.arrive : iso(addDays(today, 7));
    d.value = (saved && saved.depart > a.value) ? saved.depart : iso(addDays(new Date(a.value), 1));
    if (saved && saved.guests) f.querySelector("[name=guests]").value = saved.guests;
    a.addEventListener("change", function () {
      d.min = iso(addDays(new Date(a.value), 1));
      if (d.value <= a.value) d.value = d.min;
    });
    f.addEventListener("submit", function (e) {
      e.preventDefault();
      store.set("geg-search", { arrive: a.value, depart: d.value, guests: f.querySelector("[name=guests]").value });
      window.location.href = f.getAttribute("action");
    });
  });

  function alertBox(f, msg) {
    var p = f.querySelector(".form-error");
    if (!p) { p = document.createElement("p"); p.className = "form-error notice"; p.setAttribute("role", "alert"); f.appendChild(p); }
    p.textContent = msg;
  }

  // Förfrågningsformulär (företag, fest, kontakt)
  document.querySelectorAll("form[data-inquiry]").forEach(function (f) {
    f.addEventListener("submit", function (e) {
      e.preventDefault();
      if (!f.reportValidity()) return;
      var done = document.getElementById(f.getAttribute("data-inquiry"));
      var name = (f.querySelector("[name=namn]") || {}).value || "";
      var btn = f.querySelector("[type=submit]");
      function showDone() {
        if (!done) return;
        var n = done.querySelector("[data-name]");
        if (n) n.textContent = name.split(" ")[0] || "";
        f.hidden = true; done.hidden = false; done.focus();
      }
      // Skarp drift: skicka till formulärtjänsten (data-forms på <html>). Utan den är det förhandsläge och inget skickas.
      var endpoint = document.documentElement.getAttribute("data-forms");
      if (endpoint) {
        btn.disabled = true; btn.textContent = T.sending;
        fetch(endpoint, { method: "POST", headers: { "Accept": "application/json" }, body: new FormData(f) })
          .then(function (r) { if (!r.ok) throw new Error(r.status); showDone(); })
          .catch(function () { btn.disabled = false; btn.textContent = T.retry; alertBox(f, T.sendError); });
        return;
      }
      if (done) {
        var n = done.querySelector("[data-name]");
        if (n) n.textContent = name.split(" ")[0] || "";
        f.hidden = true; done.hidden = false; done.focus();
      }
    });
  });

  // Galleri: filter + ljuslåda
  var gallery = document.querySelector(".gallery");
  if (gallery) {
    var items = Array.prototype.slice.call(gallery.querySelectorAll("[data-cat]"));
    document.querySelectorAll(".filters button").forEach(function (b) {
      b.addEventListener("click", function () {
        document.querySelectorAll(".filters button").forEach(function (x) { x.setAttribute("aria-pressed", x === b ? "true" : "false"); });
        var c = b.getAttribute("data-filter");
        items.forEach(function (it) { it.hidden = !(c === "alla" || it.getAttribute("data-cat") === c); });
      });
    });
    var lb = document.getElementById("lightbox"), lbStage = lb && lb.querySelector(".lb-stage"), lbTitle = lb && lb.querySelector(".lb-title"), idx = 0;
    function visible() { return items.filter(function (it) { return !it.hidden; }); }
    function show(i) {
      var v = visible(); if (!v.length) return;
      idx = (i + v.length) % v.length;
      var src = v[idx].querySelector(".ph");
      lbStage.innerHTML = ""; var c = src.cloneNode(true); lbStage.appendChild(c);
      Array.prototype.forEach.call(c.querySelectorAll("img, source"), function (e) { e.setAttribute("sizes", "92vw"); e.removeAttribute("loading"); });
      lbTitle.textContent = v[idx].getAttribute("data-title") + "  ·  " + (idx + 1) + " / " + v.length;
    }
    items.forEach(function (it) {
      it.querySelector("button").addEventListener("click", function () { lb.hidden = false; show(visible().indexOf(it)); lb.querySelector(".lb-close").focus(); });
    });
    if (lb) {
      lb.querySelector(".lb-close").addEventListener("click", function () { lb.hidden = true; });
      lb.querySelector(".lb-prev").addEventListener("click", function () { show(idx - 1); });
      lb.querySelector(".lb-next").addEventListener("click", function () { show(idx + 1); });
      lb.addEventListener("click", function (e) { if (e.target === lb) lb.hidden = true; });
      document.addEventListener("keydown", function (e) {
        if (lb.hidden) return;
        if (e.key === "Escape") lb.hidden = true;
        if (e.key === "ArrowLeft") show(idx - 1);
        if (e.key === "ArrowRight") show(idx + 1);
      });
    }
  }

  // Bokningssidan
  var bk = document.getElementById("booking");
  if (bk) {
    var fa = document.getElementById("b-arrive"), fd = document.getElementById("b-depart"), fg = document.getElementById("b-guests");
    var s = store.get("geg-search");
    fa.min = iso(today);
    fa.value = (s && s.arrive >= iso(today)) ? s.arrive : iso(addDays(today, 7));
    fd.value = (s && s.depart > fa.value) ? s.depart : iso(addDays(new Date(fa.value), 1));
    fg.value = (s && s.guests) || "2";
    var want = (function () { try { return decodeURIComponent((location.hash || "").slice(1)); } catch (e) { return ""; } })();
    if (want) { var pre = document.querySelector('.room-opt input[value="' + want + '"]'); if (pre) pre.checked = true; }

    var fmt = new Intl.NumberFormat(LOC);
    var dfmt = new Intl.DateTimeFormat(LOC, { weekday: "short", day: "numeric", month: "short" });

    // data-price = lägsta pris för 1–2 / 3 / 4 gäster, t.ex. "795,995,1195".
    function priceFor(o, guests) {
      var p = o.getAttribute("data-price").split(",").map(function (x) { return parseInt(x, 10); });
      return p[Math.min(Math.max(guests - 2, 0), p.length - 1)];
    }
    function update() {
      if (fd.value <= fa.value) fd.value = iso(addDays(new Date(fa.value), 1));
      fd.min = iso(addDays(new Date(fa.value), 1));
      var nights = Math.max(1, Math.round((new Date(fd.value) - new Date(fa.value)) / 864e5));
      var guests = parseInt(fg.value, 10) || 1;
      store.set("geg-search", { arrive: fa.value, depart: fd.value, guests: String(guests) });
      document.querySelectorAll(".room-opt").forEach(function (o) {
        var cap = parseInt(o.getAttribute("data-cap"), 10);
        var input = o.querySelector("input");
        var tooSmall = guests > cap;
        o.classList.toggle("soldout", tooSmall);
        input.disabled = tooSmall;
        if (tooSmall && input.checked) input.checked = false;
        o.querySelector(".rp-note").textContent = tooSmall ? T.max + " " + cap + " " + T.guests : fmt.format(priceFor(o, guests) * nights) + " kr " + T.for + " " + nights + " " + (nights === 1 ? T.night : T.nights);
      });
      var sel = document.querySelector(".room-opt input:checked");
      if (!sel) { var first = document.querySelector(".room-opt input:not(:disabled)"); if (first) { first.checked = true; sel = first; } }
      var opt = sel && sel.closest(".room-opt");
      var price = opt ? priceFor(opt, guests) : 0;
      var total = price * nights;
      document.getElementById("s-dates").textContent = dfmt.format(new Date(fa.value)) + " – " + dfmt.format(new Date(fd.value));
      document.getElementById("s-nights").textContent = nights + " " + (nights === 1 ? T.night : T.nights);
      document.getElementById("s-guests").textContent = guests + " " + (guests === 1 ? T.guest : T.guests);
      document.getElementById("s-room").textContent = opt ? opt.getAttribute("data-name") : T.chooseRoom;
      document.getElementById("s-total").textContent = fmt.format(total) + " kr";
    }
    [fa, fd, fg].forEach(function (el) { el.addEventListener("change", update); });
    document.querySelectorAll(".room-opt input").forEach(function (el) { el.addEventListener("change", update); });
    update();

    document.getElementById("to-engine").addEventListener("click", function () {
      var eng = document.getElementById("engine");
      eng.hidden = false; eng.scrollIntoView({ behavior: "smooth", block: "start" }); eng.focus();
    });
  }

  // Kopiera-knappar (telefon/e-post)
  document.querySelectorAll("[data-copy]").forEach(function (b) {
    b.addEventListener("click", function () {
      var t = b.getAttribute("data-copy"), old = b.textContent;
      var ok = function () { b.textContent = T.copied; setTimeout(function () { b.textContent = old; }, 1600); };
      if (navigator.clipboard) navigator.clipboard.writeText(t).then(ok, function () {});
    });
  });

  // Årtal i sidfoten
  document.querySelectorAll("[data-year]").forEach(function (el) { el.textContent = new Date().getFullYear(); });
})();

// Hero-film: stillbilden visas direkt, filmen hämtas först när sidan har laddats.
// Ingen film vid "minska rörelse" eller sparat dataläge. Pausknapp enligt WCAG 2.2.2.
(function () {
  var v = document.querySelector(".hero-video");
  if (!v) return;
  var reduce = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  var save = navigator.connection && navigator.connection.saveData;
  if (reduce || save) return;
  var btn = document.querySelector(".hero-pause");
  function start() {
    v.src = window.innerWidth <= 800 ? v.getAttribute("data-src-small") : v.getAttribute("data-src");
    v.addEventListener("playing", function () { v.classList.add("is-playing"); }, { once: true });
    var p = v.play(); if (p && p.catch) p.catch(function () {});
    if (btn) {
      btn.hidden = false;
      btn.addEventListener("click", function () {
        var paused = btn.getAttribute("aria-pressed") === "true";
        if (paused) { v.play(); } else { v.pause(); }
        btn.setAttribute("aria-pressed", paused ? "false" : "true");
        btn.querySelector(".hero-pause-label").textContent = btn.getAttribute(paused ? "data-pause" : "data-play");
      });
    }
  }
  if (document.readyState === "complete") setTimeout(start, 300);
  else window.addEventListener("load", function () { setTimeout(start, 300); });
})();

// Fäll ihop huvudmenyn när den inte får plats på en rad (t.ex. tyska eller franska).
(function () {
  var head = document.querySelector(".site-header .wrap"), root = document.documentElement;
  if (!head) return;
  function fit() {
    root.classList.remove("nav-collapsed");
    if (window.innerWidth > 1060 && head.scrollWidth > head.clientWidth + 1) root.classList.add("nav-collapsed");
  }
  fit();
  window.addEventListener("resize", fit);
  if (document.fonts && document.fonts.ready) document.fonts.ready.then(fit);
})();

// 360°-visningar. Rundturen är byggd i 3DVista och ligger på egen server i /360/.
// Den laddas först när besökaren klickar, i en iframe som öppnas på rätt vy (#media-name=).
(function () {
  var boxes = document.querySelectorAll(".pano");
  if (!boxes.length) return;
  var PT = { ui: {}, s: {} };
  try { PT = JSON.parse(document.getElementById("pano-t").textContent); } catch (e) {}
  // Vyernas namn i 3DVista-projektet (svenska, används bara som adress).
  var NAME = {
    "01": "Infarten", "02": "Vägen till receptionen", "03": "Receptionen", "04": "Minigolfen", "05": "Trädäcket vid rummen",
    "06": "Rum 6", "07": "Rum 6 · Badrummet", "08": "Rum 6 · Loftet", "09": "Rum 7", "10": "Rum 7 · Badrummet", "11": "Rum 7 · Loftet",
    "12": "Rum 9", "13": "Rum 9 · Badrummet", "14": "Rum 9 · Loftet", "15": "Rum 10", "16": "Rum 10 · Badrummet", "17": "Rum 10 · Loftet",
    "18": "Kontorsbyggnaden", "22": "Festlokalens terrass", "23": "Festlokalens bar", "24": "Festlokalens lounge", "25": "Festlokalens matsal",
    "26": "Festlokalens stora sal", "26d": "Stora salen, dukad (illustration)", "27": "Vid gästköket", "28": "Gästkök, wc och dusch", "29": "Gästköket"
  };
  var active = null;
  function txt(id) { return PT.s[id] || [id, ""]; }
  function hash(id) { return "#media-name=" + encodeURIComponent(NAME[id] || NAME["01"]); }

  Array.prototype.forEach.call(boxes, function (box) {
    var wrap = box.parentNode, tour = box.getAttribute("data-tour");
    var btn = box.querySelector(".pano-start"), view = box.querySelector(".pano-view"), full = box.querySelector(".pano-full");
    var cap = wrap.querySelector(".pano-cap"), hint = wrap.querySelector(".pano-hint"), chips = wrap.querySelectorAll(".pano-chips button");
    var label = btn.querySelector(".pano-btn"), labelHTML = label.innerHTML;
    var inst = { frame: null, stop: stop };

    function mark(id) {
      var t = txt(id);
      cap.querySelector("strong").textContent = t[0];
      cap.querySelector("span").textContent = t[1];
      box.setAttribute("aria-label", box.getAttribute("aria-label").split(":")[0] + ": " + t[0]);
      Array.prototype.forEach.call(chips, function (c) { c.setAttribute("aria-pressed", c.getAttribute("data-scene") === id ? "true" : "false"); });
    }
    function stop() {
      if (inst.frame) { inst.frame.remove(); inst.frame = null; }
      box.classList.remove("is-on", "is-loading"); label.innerHTML = labelHTML; hint.hidden = true;
      if (full) full.hidden = true;
    }
    function start(id) {
      mark(id);
      if (inst.frame) {
        try { inst.frame.contentWindow.location.hash = hash(id); } catch (e) { inst.frame.src = tour + "index.htm" + hash(id); }
        return;
      }
      if (active && active !== inst) active.stop();
      active = inst;
      box.classList.add("is-loading"); label.textContent = PT.ui.loading || "…";
      var f = document.createElement("iframe");
      f.src = tour + "index.htm" + hash(id);
      f.title = box.getAttribute("aria-label");
      f.setAttribute("allow", "fullscreen; xr-spatial-tracking; accelerometer; gyroscope");
      f.setAttribute("allowfullscreen", "");
      f.addEventListener("load", function () {
        box.classList.remove("is-loading"); box.classList.add("is-on"); hint.hidden = false;
        if (full) full.hidden = false;
        try { f.focus(); } catch (e) {}
      });
      view.appendChild(f);
      inst.frame = f;
    }
    btn.addEventListener("click", function () { start(box.getAttribute("data-first")); });
    Array.prototype.forEach.call(chips, function (c) { c.addEventListener("click", function () { start(c.getAttribute("data-scene")); }); });
    if (full) full.addEventListener("click", function () {
      var el = inst.frame || box;
      if (el.requestFullscreen) el.requestFullscreen(); else if (el.webkitRequestFullscreen) el.webkitRequestFullscreen();
    });
  });
})();
