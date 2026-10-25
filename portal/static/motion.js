/**
 * HealthInsight v2 — Motion & Micro-Interaction Module
 * - IntersectionObserver-based scroll-reveal (.page-section)
 * - Count-up animation for KPI numerals
 * - Lenis smooth scroll (CDN)
 * - Navbar glass-blur on scroll
 * - Page transition (fade + blur) on SPA-style navigate
 */

(function () {
  /* ── LENIS SMOOTH SCROLL ─────────────────────────────────────────────────── */
  let lenis;

  function initLenis() {
    if (typeof Lenis === 'undefined') return;
    lenis = new Lenis({
      duration: 1.15,
      easing:   (t) => Math.min(1, 1.001 - Math.pow(2, -10 * t)),
      smoothWheel: true,
    });

    function lenisRaf(t) {
      lenis.raf(t);
      requestAnimationFrame(lenisRaf);
    }
    requestAnimationFrame(lenisRaf);
  }

  /* ── NAVBAR SCROLL EFFECT ────────────────────────────────────────────────── */
  function initNavScroll() {
    const navbar = document.querySelector('.navbar');
    if (!navbar) return;

    const threshold = 40;
    let ticking = false;

    function update() {
      const scrollY = window.scrollY || window.pageYOffset;
      navbar.classList.toggle('scrolled', scrollY > threshold);
      ticking = false;
    }

    window.addEventListener('scroll', () => {
      if (!ticking) { requestAnimationFrame(update); ticking = true; }
    }, { passive: true });
  }

  /* ── SCROLL-REVEAL (.page-section) ──────────────────────────────────────── */
  function initScrollReveal() {
    const sections = document.querySelectorAll('.page-section, .kpi-card, .glass-panel');
    if (!sections.length) return;

    const io = new IntersectionObserver((entries) => {
      for (const entry of entries) {
        if (entry.isIntersecting) {
          entry.target.classList.add('visible');
          io.unobserve(entry.target);
        }
      }
    }, {
      threshold: 0.08,
      rootMargin: '0px 0px -40px 0px',
    });

    for (const el of sections) io.observe(el);
  }

  /* ── COUNT-UP ANIMATION ──────────────────────────────────────────────────── */
  /**
   * Animates a numeric value in an element.
   * @param {HTMLElement} el   — target element
   * @param {number}      end  — final value
   * @param {number}      dur  — duration ms
   * @param {string}      prefix — e.g. '$'
   * @param {string}      suffix — e.g. 'ms'
   * @param {number}      decimals — decimal places
   */
  function countUp(el, end, dur = 900, prefix = '', suffix = '', decimals = 0) {
    const start  = 0;
    const startT = performance.now();
    const multiplier = Math.pow(10, decimals);

    function easeOutQuart(t) { return 1 - Math.pow(1 - t, 4); }

    function frame(now) {
      const elapsed = Math.min((now - startT) / dur, 1);
      const value   = start + (end - start) * easeOutQuart(elapsed);
      const display = Math.round(value * multiplier) / multiplier;
      el.textContent = prefix + display.toLocaleString(undefined, {
        minimumFractionDigits: decimals,
        maximumFractionDigits: decimals,
      }) + suffix;

      if (elapsed < 1) {
        requestAnimationFrame(frame);
      } else {
        el.textContent = prefix + end.toLocaleString(undefined, {
          minimumFractionDigits: decimals,
          maximumFractionDigits: decimals,
        }) + suffix;
        el.classList.add('count-up-done');
      }
    }

    requestAnimationFrame(frame);
  }

  /* Parses a formatted string back to a number for count-up re-trigger */
  function parseNumeric(str) {
    if (!str) return null;
    const cleaned = str.replace(/[^0-9.\-]/g, '');
    const n = parseFloat(cleaned);
    return isNaN(n) ? null : n;
  }

  /* Extract prefix (currency symbols etc.) and suffix (units) */
  function extractAffix(str) {
    const prefixMatch = str.match(/^([^0-9\-]*)/);
    const suffixMatch = str.match(/([^0-9.]+)$/);
    return {
      prefix: prefixMatch ? prefixMatch[1] : '',
      suffix: suffixMatch ? suffixMatch[1] : '',
    };
  }

  /**
   * Observe KPI elements and trigger count-up when they appear.
   * Works with the existing monitor.js that sets text content.
   */
  function initKpiCountUp() {
    const kpiIds = ['kpi-patients', 'kpi-encounters', 'kpi-cost', 'kpi-duration'];

    /* MutationObserver to detect when monitor.js updates the value */
    const mo = new MutationObserver((mutations) => {
      for (const mut of mutations) {
        if (mut.type !== 'characterData' && mut.type !== 'childList') continue;
        const el = mut.target.nodeType === 3
          ? mut.target.parentElement
          : mut.target;

        if (!el || el.dataset.countingUp) continue;
        const str = el.textContent.trim();
        const num = parseNumeric(str);
        if (num === null || num === 0) continue;

        const { prefix, suffix } = extractAffix(str);
        const decimals = (str.includes('.') ? (str.split('.')[1] || '').replace(/\D/g,'').length : 0);

        el.dataset.countingUp = '1';
        countUp(el, num, 1100, prefix, suffix, decimals);

        /* Allow re-trigger after animation completes */
        setTimeout(() => delete el.dataset.countingUp, 1200);
      }
    });

    for (const id of kpiIds) {
      const el = document.getElementById(id);
      if (el) mo.observe(el, { characterData: true, childList: true, subtree: true });
    }
  }

  /* ── PAGE TRANSITION (fade-blur in) ─────────────────────────────────────── */
  function initPageTransition() {
    const container = document.querySelector('.app-container') || document.body;

    /* Entrance: fade in from slightly blurred */
    container.style.opacity = '0';
    container.style.filter  = 'blur(6px)';
    container.style.transition = 'opacity 540ms cubic-bezier(0.22,1,0.36,1), filter 540ms cubic-bezier(0.22,1,0.36,1)';

    requestAnimationFrame(() => {
      requestAnimationFrame(() => {
        container.style.opacity = '1';
        container.style.filter  = 'blur(0px)';
      });
    });
  }

  /* ── COPY SQL BUTTON ─────────────────────────────────────────────────────── */
  function initCopyButtons() {
    document.addEventListener('click', (e) => {
      const btn = e.target.closest('.btn-copy-sql');
      if (!btn) return;
      const box  = btn.closest('.sql-box');
      const code = box?.querySelector('.sql-code');
      if (!code) return;

      navigator.clipboard.writeText(code.textContent.trim()).then(() => {
        const orig = btn.textContent;
        btn.textContent = 'Copied ✓';
        setTimeout(() => { btn.textContent = orig; }, 1800);
      });
    });
  }

  /* ── RESULT TABS ─────────────────────────────────────────────────────────── */
  function initResultTabs() {
    document.addEventListener('click', (e) => {
      const tab = e.target.closest('.tab-btn');
      if (!tab) return;

      const group = tab.closest('.result-tabs');
      if (!group) return;
      group.querySelectorAll('.tab-btn').forEach(t => t.classList.remove('active'));
      tab.classList.add('active');

      const target  = tab.dataset.target;
      const wrapper = tab.closest('.message-ai, .result-area');
      if (!wrapper || !target) return;

      wrapper.querySelectorAll('[data-panel]').forEach(p => {
        p.style.display = p.dataset.panel === target ? '' : 'none';
      });
    });
  }

  /* ── INIT ALL ────────────────────────────────────────────────────────────── */
  function init() {
    initLenis();
    initNavScroll();
    initScrollReveal();
    initKpiCountUp();
    initPageTransition();
    initCopyButtons();
    initResultTabs();
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }

  /* Expose countUp globally for direct use from monitor.js or chat.js if needed */
  window.HI_countUp = countUp;
})();
