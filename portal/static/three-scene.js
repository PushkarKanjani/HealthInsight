/**
 * HealthInsight v2 — Pastel Mesh Background Canvas
 * Replaces Three.js dark particle field with a soft Apple-style pastel blob canvas.
 * Pure Canvas 2D API — no external dependencies.
 */

(function () {
  const canvas = document.getElementById('webgl-canvas');
  if (!canvas) return;

  const ctx = canvas.getContext('2d');
  let W, H, dpr;
  let raf;

  /* ── BLOB DEFINITIONS ──────────────────────────────────────────────────────── */
  /* Each blob: pastel colour, size, starting position, drift speed/phase */
  const BLOBS = [
    { h: 350,  s: 80,  l: 82, a: 0.18, rx: 0.15, ry: 0.18, ax: 0.00008, ay: 0.00007, px: 0, py: 1.2  },
    { h: 265,  s: 60,  l: 84, a: 0.15, rx: 0.22, ry: 0.20, ax: 0.00006, ay: 0.00009, px: 2, py: 0.5  },
    { h: 196,  s: 55,  l: 86, a: 0.13, rx: 0.18, ry: 0.22, ax: 0.00009, ay: 0.00006, px: 4, py: 3.1  },
    { h: 30,   s: 75,  l: 88, a: 0.14, rx: 0.20, ry: 0.16, ax: 0.00007, ay: 0.00008, px: 1, py: 2.3  },
    { h: 310,  s: 50,  l: 85, a: 0.12, rx: 0.25, ry: 0.24, ax: 0.00005, ay: 0.00007, px: 3, py: 0.9  },
    { h: 165,  s: 60,  l: 87, a: 0.11, rx: 0.16, ry: 0.18, ax: 0.00010, ay: 0.00005, px: 5, py: 4.0  },
  ];

  /* ── RESIZE ────────────────────────────────────────────────────────────────── */
  function resize() {
    dpr = window.devicePixelRatio || 1;
    W = window.innerWidth;
    H = window.innerHeight;
    canvas.width  = W * dpr;
    canvas.height = H * dpr;
    canvas.style.width  = W + 'px';
    canvas.style.height = H + 'px';
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
  }

  /* ── DRAW FRAME ────────────────────────────────────────────────────────────── */
  function draw(ts) {
    ctx.clearRect(0, 0, W, H);

    /* Pearl canvas base */
    ctx.fillStyle = '#F5F5F7';
    ctx.fillRect(0, 0, W, H);

    for (const b of BLOBS) {
      /* Sinusoidal drift — very slow, serene */
      const x = (0.15 + 0.70 * (0.5 + 0.5 * Math.sin(ts * b.ax + b.px))) * W;
      const y = (0.10 + 0.80 * (0.5 + 0.5 * Math.cos(ts * b.ay + b.py))) * H;
      const rX = b.rx * W * (0.85 + 0.15 * Math.sin(ts * b.ax * 1.7 + b.px));
      const rY = b.ry * H * (0.85 + 0.15 * Math.cos(ts * b.ay * 1.3 + b.py));

      const grad = ctx.createRadialGradient(x, y, 0, x, y, Math.max(rX, rY));
      grad.addColorStop(0,   `hsla(${b.h}, ${b.s}%, ${b.l}%, ${b.a})`);
      grad.addColorStop(0.55,`hsla(${b.h}, ${b.s}%, ${b.l + 3}%, ${b.a * 0.55})`);
      grad.addColorStop(1,   `hsla(${b.h}, ${b.s}%, ${b.l + 5}%, 0)`);

      /* Draw as ellipse */
      ctx.save();
      ctx.translate(x, y);
      ctx.scale(rX / Math.max(rX, rY), rY / Math.max(rX, rY));
      ctx.beginPath();
      ctx.arc(0, 0, Math.max(rX, rY), 0, Math.PI * 2);
      ctx.fillStyle = grad;
      ctx.fill();
      ctx.restore();
    }

    /* Subtle noise grain overlay (thin, just enough texture) */
    paintGrain(ts);

    raf = requestAnimationFrame(draw);
  }

  /* ── GRAIN OVERLAY ─────────────────────────────────────────────────────────── */
  let grainOffCanvas, grainCtx;
  const GRAIN_SIZE = 128;

  function buildGrainCanvas() {
    grainOffCanvas = document.createElement('canvas');
    grainOffCanvas.width  = GRAIN_SIZE;
    grainOffCanvas.height = GRAIN_SIZE;
    grainCtx = grainOffCanvas.getContext('2d');
  }

  function paintGrain(ts) {
    if (!grainOffCanvas) buildGrainCanvas();

    const imgData = grainCtx.createImageData(GRAIN_SIZE, GRAIN_SIZE);
    const d = imgData.data;
    const seed = Math.floor(ts / 40);

    for (let i = 0; i < d.length; i += 4) {
      /* Simple LCG pseudo-random seeded per frame section */
      const n = (((i ^ seed) * 1664525 + 1013904223) & 0xFFFFFFFF) >>> 24;
      d[i] = d[i+1] = d[i+2] = n;
      d[i+3] = 9;  /* very faint — alpha ≈ 0.035 */
    }

    grainCtx.putImageData(imgData, 0, 0);

    /* Tile across canvas */
    const pat = ctx.createPattern(grainOffCanvas, 'repeat');
    ctx.globalCompositeOperation = 'overlay';
    ctx.globalAlpha = 0.12;
    ctx.fillStyle = pat;
    ctx.fillRect(0, 0, W, H);
    ctx.globalAlpha = 1;
    ctx.globalCompositeOperation = 'source-over';
  }

  /* ── INIT ──────────────────────────────────────────────────────────────────── */
  function init() {
    resize();
    window.addEventListener('resize', () => { resize(); });
    cancelAnimationFrame(raf);
    requestAnimationFrame(draw);
  }

  /* Wait for DOM */
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
