/**
 * HealthInsight v2 — Liquid Cursor System
 * - Dot (exact position) + Blob (spring-lag follower)
 * - Cursor-reactive glass: specular highlight tracks mouse on .glass-panel
 * - Magnetic buttons: spring pull on .btn-primary, .chip-btn, .btn-send within 80px
 * - Disabled on touch devices
 */

(function () {
  /* ── Skip on touch/coarse-pointer devices ──────────────────────────────── */
  if (window.matchMedia('(hover: none)').matches) return;

  const dot  = document.getElementById('cursor-dot');
  const blob = document.getElementById('cursor-blob');
  if (!dot || !blob) return;

  /* ── State ─────────────────────────────────────────────────────────────── */
  let mouseX = -200, mouseY = -200;
  let blobX  = -200, blobY  = -200;
  let velX = 0, velY = 0;

  /* Spring constants: stiffness, damping */
  const K = 0.12;   /* spring pull toward mouse */
  const D = 0.78;   /* damping factor */

  /* Magnetic pull state per element */
  const magnetics = new Map();  /* el → { ox, oy } offset transform */

  let raf;

  /* ── Helpers ────────────────────────────────────────────────────────────── */
  function lerp(a, b, t) { return a + (b - a) * t; }
  function dist(ax, ay, bx, by) { return Math.hypot(ax - bx, ay - by); }

  /* ── Mouse tracking ─────────────────────────────────────────────────────── */
  document.addEventListener('mousemove', (e) => {
    mouseX = e.clientX;
    mouseY = e.clientY;
    updateGlassSpecular(e);
    updateMagnetics(e);
  });

  /* ── Cursor state classes ───────────────────────────────────────────────── */
  document.addEventListener('mouseover', (e) => {
    if (e.target.closest('button, a, .chip-btn, [role="button"], input, textarea, select, label')) {
      document.body.classList.add('cursor-hover');
    }
  });

  document.addEventListener('mouseout', (e) => {
    if (e.target.closest('button, a, .chip-btn, [role="button"], input, textarea, select, label')) {
      document.body.classList.remove('cursor-hover');
    }
  });

  document.addEventListener('mousedown', () => document.body.classList.add('cursor-click'));
  document.addEventListener('mouseup',   () => document.body.classList.remove('cursor-click'));

  /* ── Animation loop: spring physics blob ───────────────────────────────── */
  function tick() {
    /* Spring integration */
    velX = velX * D + (mouseX - blobX) * K;
    velY = velY * D + (mouseY - blobY) * K;
    blobX += velX;
    blobY += velY;

    /* Velocity magnitude for stretch (subtle) */
    const speed = Math.hypot(velX, velY);
    const stretch = Math.min(speed * 0.06, 14); /* max 14px stretch */

    /* Angle of travel */
    const angle = Math.atan2(velY, velX);
    const scaleX = 1 + stretch / 44;
    const scaleY = 1 - stretch / 88;

    dot.style.left  = mouseX + 'px';
    dot.style.top   = mouseY + 'px';

    blob.style.left = blobX + 'px';
    blob.style.top  = blobY + 'px';
    blob.style.transform = `translate(-50%,-50%) rotate(${angle}rad) scale(${scaleX},${scaleY})`;

    raf = requestAnimationFrame(tick);
  }

  tick();

  /* ── Cursor-reactive glass specular highlight ───────────────────────────── */
  function updateGlassSpecular(e) {
    const panels = document.querySelectorAll('.glass-panel');
    for (const panel of panels) {
      const rect = panel.getBoundingClientRect();
      /* Extend activation area: if cursor within 120px of panel */
      const isNear =
        e.clientX > rect.left - 120 && e.clientX < rect.right  + 120 &&
        e.clientY > rect.top  - 120 && e.clientY < rect.bottom + 120;

      if (!isNear) {
        /* Reset to default top-center */
        panel.style.setProperty('--spec-x', '50%');
        panel.style.setProperty('--spec-y', '20%');
        continue;
      }

      /* Map cursor position to percentage within panel */
      const px = ((e.clientX - rect.left) / rect.width)  * 100;
      const py = ((e.clientY - rect.top)  / rect.height) * 100;

      /* Clamp loosely (allow slight bleed for edge glints) */
      panel.style.setProperty('--spec-x', `${Math.min(Math.max(px, -10), 110)}%`);
      panel.style.setProperty('--spec-y', `${Math.min(Math.max(py, -10), 110)}%`);
    }
  }

  /* ── Magnetic buttons ───────────────────────────────────────────────────── */
  const MAGNET_RADIUS  = 80;   /* px — activation radius */
  const MAGNET_PULL    = 0.40; /* 0–1, how far to move element */

  function registerMagnetics() {
    const els = document.querySelectorAll('.btn-primary, .btn-send, .chip-btn');
    for (const el of els) {
      if (!magnetics.has(el)) {
        magnetics.set(el, { ox: 0, oy: 0 });
        el.style.willChange = 'transform';
      }
    }
  }

  function updateMagnetics(e) {
    /* Lazily register any new elements */
    registerMagnetics();

    for (const [el, state] of magnetics) {
      const rect = el.getBoundingClientRect();
      const cx = rect.left + rect.width  / 2;
      const cy = rect.top  + rect.height / 2;
      const d  = dist(e.clientX, e.clientY, cx, cy);

      if (d < MAGNET_RADIUS) {
        const force  = (MAGNET_RADIUS - d) / MAGNET_RADIUS;
        const targetX = (e.clientX - cx) * force * MAGNET_PULL;
        const targetY = (e.clientY - cy) * force * MAGNET_PULL;
        state.ox = lerp(state.ox, targetX, 0.18);
        state.oy = lerp(state.oy, targetY, 0.18);
      } else {
        state.ox = lerp(state.ox, 0, 0.14);
        state.oy = lerp(state.oy, 0, 0.14);
      }

      /* Only update if non-trivially displaced */
      if (Math.abs(state.ox) > 0.05 || Math.abs(state.oy) > 0.05) {
        el.style.transform = `translate(${state.ox.toFixed(2)}px, ${state.oy.toFixed(2)}px)`;
      } else if (el.style.transform) {
        el.style.transform = '';
      }
    }
  }

  /* ── Re-register when new chips/buttons are added dynamically ───────────── */
  const mo = new MutationObserver(() => registerMagnetics());
  mo.observe(document.body, { childList: true, subtree: true });

  /* ── Cleanup on visibility change ───────────────────────────────────────── */
  document.addEventListener('visibilitychange', () => {
    if (document.hidden) {
      cancelAnimationFrame(raf);
    } else {
      tick();
    }
  });
})();
