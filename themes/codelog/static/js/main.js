/* CodeLog theme behaviour. Everything is progressive: the page is fully
   readable with this file blocked. Configuration arrives on <body data-*>. */
(function () {
  "use strict";

  var body = document.body;
  var SITEURL = body.dataset.siteurl || "";

  /* -- Theme ------------------------------------------------------------ */

  function initTheme() {
    var toggle = document.querySelector(".theme-toggle");
    if (!toggle) return;

    toggle.addEventListener("click", function () {
      var root = document.documentElement;
      var prefersDark = window.matchMedia("(prefers-color-scheme: dark)").matches;
      var current = root.dataset.theme || (prefersDark ? "dark" : "light");
      var next = current === "dark" ? "light" : "dark";

      root.dataset.theme = next;
      try {
        localStorage.setItem("theme", next);
      } catch (e) {
        /* private mode — the choice just won't persist */
      }
      toggle.setAttribute("aria-label", "Switch to " + current + " theme");
    });
  }

  /* -- Premium (ad-free) mode -------------------------------------------
     The flag is already on <html> by the time this runs — the inline head
     script applies it before first paint. This only wires the control and
     keeps it in sync, so the toggle works without a reload. */

  function initPremium() {
    var toggles = document.querySelectorAll("[data-premium-toggle]");
    if (!toggles.length) return;

    var root = document.documentElement;
    var on = root.dataset.premium === "on";

    function sync() {
      if (on) root.dataset.premium = "on";
      else delete root.dataset.premium;

      toggles.forEach(function (toggle) {
        toggle.setAttribute("aria-checked", String(on));
      });
    }

    sync();

    toggles.forEach(function (toggle) {
      toggle.addEventListener("click", function () {
        on = !on;
        sync();
        try {
          localStorage.setItem("premium", on ? "on" : "off");
        } catch (e) {
          /* private mode — the choice just won't persist */
        }
      });
    });
  }

  /* -- Mobile navigation ------------------------------------------------ */

  function initNav() {
    var toggle = document.querySelector(".nav-toggle");
    var nav = document.getElementById("primary-nav");
    if (!toggle || !nav) return;

    toggle.addEventListener("click", function () {
      var open = nav.classList.toggle("is-open");
      toggle.setAttribute("aria-expanded", String(open));
    });

    nav.addEventListener("click", function (event) {
      if (event.target.closest("a")) {
        nav.classList.remove("is-open");
        toggle.setAttribute("aria-expanded", "false");
      }
    });
  }

  /* -- Search ------------------------------------------------------------
     Pagefind is imported on first use so the search bundle costs nothing on
     a normal page view. */

  function initSearch() {
    var modal = document.getElementById("search-modal");
    var input = document.getElementById("search-input");
    var results = document.getElementById("search-results");
    if (!modal || !input || !results) return;

    var pagefind = null;
    var loading = null;
    var lastFocus = null;
    var activeIndex = -1;
    var debounce;

    function loadPagefind() {
      if (loading) return loading;
      // SITEURL is relative ("." / "..") in production builds, and a dynamic
      // import resolves against this script's URL — so resolve it against the
      // document first.
      var bundle = new URL(SITEURL + "/pagefind/pagefind.js", document.baseURI).href;
      loading = import(bundle)
        .then(function (module) {
          pagefind = module;
          return module.init();
        })
        .catch(function () {
          pagefind = null;
          state("Search is unavailable on this build.");
        });
      return loading;
    }

    function open() {
      lastFocus = document.activeElement;
      modal.classList.add("is-open");
      modal.setAttribute("aria-hidden", "false");
      body.classList.add("no-scroll");
      input.focus();
      input.select();
      loadPagefind();
    }

    function close() {
      modal.classList.remove("is-open");
      modal.setAttribute("aria-hidden", "true");
      body.classList.remove("no-scroll");
      if (lastFocus) lastFocus.focus();
    }

    function state(message) {
      results.innerHTML = '<p class="search-state"></p>';
      results.firstChild.textContent = message;
    }

    function move(step) {
      var items = results.querySelectorAll(".search-result");
      if (!items.length) return;
      if (activeIndex >= 0) items[activeIndex].classList.remove("is-active");
      activeIndex = (activeIndex + step + items.length) % items.length;
      items[activeIndex].classList.add("is-active");
      items[activeIndex].scrollIntoView({ block: "nearest" });
    }

    function render(items) {
      activeIndex = -1;
      if (!items.length) {
        state("No results.");
        return;
      }
      results.innerHTML = items
        .map(function (item) {
          return (
            '<a class="search-result" href="' +
            item.url +
            '"><div class="search-result__title"></div><div class="search-result__excerpt">' +
            (item.excerpt || "") +
            "</div></a>"
          );
        })
        .join("");
      // Titles are set as text so a post title can never inject markup.
      results.querySelectorAll(".search-result__title").forEach(function (el, i) {
        el.textContent = (items[i].meta && items[i].meta.title) || "Untitled";
      });
    }

    function run(query) {
      if (!query) {
        state("Type to search all posts.");
        return;
      }
      loadPagefind().then(function () {
        if (!pagefind) return;
        pagefind.search(query).then(function (search) {
          Promise.all(
            search.results.slice(0, 8).map(function (result) {
              return result.data();
            })
          ).then(render);
        });
      });
    }

    document.querySelectorAll("[data-search-open]").forEach(function (trigger) {
      trigger.addEventListener("click", open);
    });

    modal.addEventListener("click", function (event) {
      if (event.target === modal || event.target.closest("[data-search-close]")) close();
    });

    input.addEventListener("input", function (event) {
      var query = event.target.value.trim();
      clearTimeout(debounce);
      debounce = setTimeout(function () {
        run(query);
      }, 140);
    });

    document.addEventListener("keydown", function (event) {
      var isOpen = modal.classList.contains("is-open");
      var focused = document.activeElement || {};
      var typing = /^(INPUT|TEXTAREA|SELECT)$/.test(focused.tagName || "");

      if ((event.key === "k" && (event.metaKey || event.ctrlKey)) || (event.key === "/" && !typing && !isOpen)) {
        event.preventDefault();
        open();
        return;
      }
      if (!isOpen) return;

      if (event.key === "Escape") close();
      if (event.key === "ArrowDown") {
        event.preventDefault();
        move(1);
      }
      if (event.key === "ArrowUp") {
        event.preventDefault();
        move(-1);
      }
      if (event.key === "Enter" && activeIndex >= 0) {
        var active = results.querySelectorAll(".search-result")[activeIndex];
        if (active) {
          event.preventDefault();
          window.location.href = active.href;
        }
      }
    });

    state("Type to search all posts.");
  }

  /* -- Table of contents ------------------------------------------------- */

  function initToc() {
    var toc = document.getElementById("toc");
    var prose = document.querySelector("[data-toc-source]");
    if (!toc || !prose) return;

    var headings = prose.querySelectorAll("h2, h3");
    if (headings.length < 2) {
      var module = toc.closest(".module");
      if (module) module.remove();
      return;
    }

    var used = Object.create(null);
    var list = document.createElement("ul");

    headings.forEach(function (heading) {
      if (!heading.id) {
        var base =
          heading.textContent
            .toLowerCase()
            .trim()
            .replace(/[^\w\s-]/g, "")
            .replace(/\s+/g, "-") || "section";
        used[base] = (used[base] || 0) + 1;
        heading.id = used[base] > 1 ? base + "-" + used[base] : base;
      }

      var item = document.createElement("li");
      item.className = "toc-" + heading.tagName.toLowerCase();
      var link = document.createElement("a");
      link.href = "#" + heading.id;
      link.textContent = heading.textContent;
      item.appendChild(link);
      list.appendChild(item);
    });

    toc.appendChild(list);

    var links = {};
    toc.querySelectorAll("a").forEach(function (link) {
      links[link.getAttribute("href").slice(1)] = link;
    });

    var observer = new IntersectionObserver(
      function (entries) {
        entries.forEach(function (entry) {
          if (!entry.isIntersecting) return;
          Object.keys(links).forEach(function (id) {
            links[id].classList.toggle("is-current", id === entry.target.id);
          });
        });
      },
      { rootMargin: "-80px 0px -70% 0px", threshold: 0 }
    );

    headings.forEach(function (heading) {
      observer.observe(heading);
    });
  }

  /* -- Reading progress -------------------------------------------------- */

  function initProgress() {
    var bar = document.querySelector(".progress");
    var article = document.querySelector("[data-toc-source]");
    if (!bar || !article) return;

    var ticking = false;

    function update() {
      var start = article.offsetTop;
      var span = article.offsetHeight - window.innerHeight + 200;
      var ratio = span > 0 ? (window.scrollY - start + 200) / span : 1;
      bar.style.transform = "scaleX(" + Math.min(Math.max(ratio, 0), 1) + ")";
      ticking = false;
    }

    window.addEventListener(
      "scroll",
      function () {
        if (ticking) return;
        ticking = true;
        window.requestAnimationFrame(update);
      },
      { passive: true }
    );
    update();
  }

  /* -- Code blocks ------------------------------------------------------- */

  function initCodeBlocks() {
    document.querySelectorAll(".prose div.highlight, .prose > pre").forEach(function (block) {
      var wrapper = document.createElement("div");
      wrapper.className = "code-block";
      block.parentNode.insertBefore(wrapper, block);
      wrapper.appendChild(block);

      var button = document.createElement("button");
      button.className = "code-copy";
      button.type = "button";
      button.textContent = "Copy";
      wrapper.appendChild(button);

      button.addEventListener("click", function () {
        var code = block.querySelector("code") || block;
        navigator.clipboard.writeText(code.innerText.replace(/\n$/, "")).then(
          function () {
            button.textContent = "Copied";
            setTimeout(function () {
              button.textContent = "Copy";
            }, 1600);
          },
          function () {
            button.textContent = "Failed";
          }
        );
      });
    });
  }

  /* -- Share ------------------------------------------------------------- */

  function initShare() {
    var button = document.querySelector("[data-copy-link]");
    if (!button) return;

    button.addEventListener("click", function () {
      navigator.clipboard.writeText(window.location.href).then(function () {
        var label = button.getAttribute("aria-label");
        button.setAttribute("aria-label", "Link copied");
        button.classList.add("is-done");
        setTimeout(function () {
          button.setAttribute("aria-label", label);
          button.classList.remove("is-done");
        }, 1600);
      });
    });
  }

  /* -- Ad slots ----------------------------------------------------------
     The in-article slot is placed after the third top-level heading, which is
     roughly a third of the way down a typical post. The node is moved before
     any ad request is made, so the network fill always matches its final
     position. */

  function initAds() {
    var inArticle = document.querySelector('[data-ad-slot="in_article"]');
    var prose = document.querySelector("[data-toc-source]");

    if (inArticle && prose) {
      var headings = prose.querySelectorAll("h2");
      var anchor = headings[2] || headings[1];
      if (anchor) anchor.parentNode.insertBefore(inArticle, anchor);
    }

    // Premium is ad-free for real, not just visually: with the flag set we
    // never fill a unit, so no ad request leaves the browser.
    if (document.documentElement.dataset.premium === "on") return;

    var units = document.querySelectorAll("ins.adsbygoogle");
    if (!units.length || !window.adsbygoogle) return;
    units.forEach(function () {
      (window.adsbygoogle = window.adsbygoogle || []).push({});
    });
  }

  /* -- Boot -------------------------------------------------------------- */

  function boot() {
    initTheme();
    initPremium();
    initNav();
    initSearch();
    initToc();
    initProgress();
    initCodeBlocks();
    initShare();
    initAds();

    var year = document.getElementById("year");
    if (year) year.textContent = String(new Date().getFullYear());
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", boot);
  } else {
    boot();
  }
})();
