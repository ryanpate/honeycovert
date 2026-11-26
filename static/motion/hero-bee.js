/* hero-bee.js - homepage hero motion.
 *
 * A bee carries a HEIC photo to the upload box, tosses it in, and flies off with the
 * converted one. The whole picture is one function of time, frame(ctx, t, layout):
 * the same t and layout always draw the same frame. No Math.random(), no Date.now(),
 * nothing remembered between frames.
 *
 * The page works without this file: .hero-bee-still (a real <img>) is the finished
 * frame, shown when JavaScript is off or the visitor asks for reduced motion.
 */
(function () {
  'use strict';

  const TAU = Math.PI * 2;
  const clamp = (x, a = 0, b = 1) => Math.min(b, Math.max(a, x));
  const lerp = (a, b, p) => a + (b - a) * p;
  const ease = {
    linear: (p) => p,
    inCubic: (p) => p * p * p,
    outCubic: (p) => 1 - Math.pow(1 - p, 3),
    inOutCubic: (p) => (p < 0.5 ? 4 * p * p * p : 1 - Math.pow(-2 * p + 2, 3) / 2),
    outExpo: (p) => (p >= 1 ? 1 : 1 - Math.pow(2, -10 * p)),
    outBack: (p) => 1 + 2.70158 * Math.pow(p - 1, 3) + 1.70158 * Math.pow(p - 1, 2),
  };
  // Progress of t through [a, b], clamped to 0..1 and eased.
  const span = (t, a, b, fn = ease.linear) => fn(clamp((t - a) / (b - a)));

  // Seeded random: the same seed always gives the same sequence.
  function rand(seed) {
    let a = seed >>> 0;
    return function () {
      a = (a + 0x6d2b79f5) >>> 0;
      let x = Math.imul(a ^ (a >>> 15), 1 | a);
      x = (x + Math.imul(x ^ (x >>> 7), 61 | x)) ^ x;
      return ((x ^ (x >>> 14)) >>> 0) / 4294967296;
    };
  }

  // Time: 120 BPM. One delivery is four bars; the toss and the pop land on bar lines.
  const BEAT = 0.5;
  const RUN = 16 * BEAT; // 8s
  const FORMATS = ['PNG', 'JPG', 'WebP']; // one per delivery, then the loop repeats
  const DURATION = RUN * FORMATS.length;
  const POSTER = 6.5; // the bee resting with the converted photo: also the still image

  // Look: the site's honey clay palette (templates/index.html :root).
  const C = {
    honey: '#f7b733',
    pale: '#fde6a6',
    deep: '#8f5600',
    ink: '#3a2a10',
    muted: '#75603c',
    well: '#f6ead0',
    tint: '150, 95, 10',
  };
  const FONT = 'ui-rounded, "SF Pro Rounded", "Nunito", system-ui, -apple-system, "Segoe UI", Roboto, sans-serif';

  // Sizes are in bee lengths (S). The still image is the bee plus its photo in this box.
  const TILE = 0.8;
  const GRIP = { x: 0.04, y: 0.66 }; // where the carried photo hangs, from the bee's centre
  const SPRITE = { w: 1.4, h: 2.25, ox: 0.66, oy: 0.82 }; // roomy enough for the soft shade

  const pt = (x, y) => ({ x, y });
  const quad = (a, c, b, p) => {
    const q = 1 - p;
    return pt(q * q * a.x + 2 * q * p * c.x + p * p * b.x, q * q * a.y + 2 * q * p * c.y + p * p * b.y);
  };
  const cubic = (a, c1, c2, b, p) => {
    const q = 1 - p;
    return pt(
      q * q * q * a.x + 3 * q * q * p * c1.x + 3 * q * p * p * c2.x + p * p * p * b.x,
      q * q * q * a.y + 3 * q * q * p * c1.y + 3 * q * p * p * c2.y + p * p * p * b.y
    );
  };

  function roundRect(ctx, x, y, w, h, r) {
    ctx.beginPath();
    ctx.moveTo(x + r, y);
    ctx.arcTo(x + w, y, x + w, y + h, r);
    ctx.arcTo(x + w, y + h, x, y + h, r);
    ctx.arcTo(x, y + h, x, y, r);
    ctx.arcTo(x, y, x + w, y, r);
    ctx.closePath();
  }

  // Pointy-top hexagon, the shape of the logo mark.
  function hexagon(ctx, x, y, r, rot) {
    ctx.beginPath();
    for (let i = 0; i < 6; i++) {
      const a = rot + (i / 6) * TAU - Math.PI / 2;
      ctx.lineTo(x + Math.cos(a) * r, y + Math.sin(a) * r);
    }
    ctx.closePath();
  }

  // A photo card: little landscape on top, format label underneath.
  function drawTile(ctx, T, label, done) {
    const h = T / 2;
    const shade = ctx.createRadialGradient(T * 0.05, T * 0.14, T * 0.2, T * 0.05, T * 0.14, T * 0.78);
    shade.addColorStop(0, `rgba(${C.tint}, 0.3)`);
    shade.addColorStop(1, `rgba(${C.tint}, 0)`);
    ctx.fillStyle = shade;
    ctx.fillRect(-T, -T, T * 2, T * 2);

    const card = ctx.createLinearGradient(0, -h, 0, h);
    card.addColorStop(0, '#fffdf7');
    card.addColorStop(1, '#fff1cf');
    roundRect(ctx, -h, -h, T, T, T * 0.2);
    ctx.fillStyle = card;
    ctx.fill();
    ctx.lineWidth = Math.max(1, T * 0.025);
    ctx.strokeStyle = `rgba(${C.tint}, 0.3)`;
    ctx.stroke();

    ctx.save();
    roundRect(ctx, -T * 0.38, -T * 0.38, T * 0.76, T * 0.4, T * 0.09);
    ctx.clip();
    ctx.fillStyle = C.pale;
    ctx.fillRect(-h, -h, T, T);
    ctx.fillStyle = C.honey;
    ctx.beginPath();
    ctx.arc(T * 0.2, -T * 0.26, T * 0.075, 0, TAU);
    ctx.fill();
    ctx.fillStyle = 'rgba(143, 86, 0, 0.55)';
    ctx.beginPath();
    ctx.moveTo(-T * 0.38, T * 0.02);
    ctx.quadraticCurveTo(-T * 0.2, -T * 0.24, 0, -T * 0.06);
    ctx.quadraticCurveTo(T * 0.16, -T * 0.17, T * 0.38, -T * 0.02);
    ctx.lineTo(T * 0.38, T * 0.1);
    ctx.lineTo(-T * 0.38, T * 0.1);
    ctx.fill();
    ctx.restore();

    roundRect(ctx, -T * 0.38, T * 0.08, T * 0.76, T * 0.31, T * 0.12);
    ctx.fillStyle = done ? C.honey : C.well;
    ctx.fill();
    ctx.fillStyle = done ? C.ink : C.muted;
    ctx.font = `800 ${T * 0.23}px ${FONT}`;
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    ctx.fillText(label, 0, T * 0.245);
  }

  // The bee, drawn in a 100-unit box facing right, centred on (x, y).
  // carry: { label, done, sway } for the photo it holds, or null.
  function drawBee(ctx, x, y, S, tilt, t, carry) {
    ctx.save();
    ctx.translate(x, y);
    ctx.rotate(tilt);
    ctx.scale(S / 100, S / 100);

    // Soft tinted shade so it sits off the page like the clay cards do.
    const lift = ctx.createRadialGradient(6, 18, 8, 6, 18, 52);
    lift.addColorStop(0, `rgba(${C.tint}, 0.2)`);
    lift.addColorStop(1, `rgba(${C.tint}, 0)`);
    ctx.fillStyle = lift;
    ctx.fillRect(-60, -50, 130, 130);

    // Wings, behind the body: 12 beats a second.
    const flap = Math.sin(t * TAU * 12);
    for (const base of [-1.15, -0.45]) {
      ctx.save();
      ctx.translate(-10, -14);
      ctx.rotate(base + flap * 0.3);
      const glass = ctx.createLinearGradient(0, 0, 0, -60);
      glass.addColorStop(0, 'rgba(255, 253, 246, 0.95)');
      glass.addColorStop(1, 'rgba(253, 230, 166, 0.62)');
      ctx.beginPath();
      ctx.ellipse(0, -30, 15, 31, 0, 0, TAU);
      ctx.fillStyle = glass;
      ctx.fill();
      ctx.lineWidth = 1.8;
      ctx.strokeStyle = 'rgba(143, 86, 0, 0.4)';
      ctx.stroke();
      ctx.beginPath();
      ctx.moveTo(0, -6);
      ctx.lineTo(0, -50);
      ctx.lineWidth = 1.2;
      ctx.strokeStyle = 'rgba(143, 86, 0, 0.22)';
      ctx.stroke();
      ctx.restore();
    }

    if (carry) {
      ctx.save();
      ctx.translate(GRIP.x * 100, GRIP.y * 100);
      ctx.rotate(carry.sway || 0);
      drawTile(ctx, TILE * 100, carry.label, carry.done);
      ctx.restore();
    }

    // Body: striped, tail down and back.
    ctx.save();
    ctx.translate(-20, 12);
    ctx.rotate(-0.35);
    ctx.fillStyle = ctx.strokeStyle = C.ink;
    ctx.lineJoin = 'round';
    ctx.lineWidth = 5;
    ctx.beginPath();
    ctx.moveTo(-26, -5);
    ctx.lineTo(-39, 1);
    ctx.lineTo(-26, 6);
    ctx.closePath();
    ctx.fill();
    ctx.stroke();
    const body = ctx.createRadialGradient(-8, -10, 2, 0, 0, 38);
    body.addColorStop(0, '#ffe08a');
    body.addColorStop(0.55, C.honey);
    body.addColorStop(1, '#de971c');
    ctx.beginPath();
    ctx.ellipse(0, 0, 30, 25, 0, 0, TAU);
    ctx.fillStyle = body;
    ctx.fill();
    ctx.save();
    ctx.clip();
    ctx.fillStyle = C.ink;
    for (const cx of [-14, 5]) {
      ctx.beginPath();
      ctx.ellipse(cx, 0, 6, 32, 0, 0, TAU);
      ctx.fill();
    }
    const sheen = ctx.createRadialGradient(-8, -14, 1, -8, -14, 24);
    sheen.addColorStop(0, 'rgba(255, 255, 255, 0.42)');
    sheen.addColorStop(1, 'rgba(255, 255, 255, 0)');
    ctx.fillStyle = sheen;
    ctx.fillRect(-32, -28, 64, 56);
    ctx.restore();
    ctx.restore();

    // Antennae, then the head over their roots.
    ctx.strokeStyle = ctx.fillStyle = C.ink;
    ctx.lineWidth = 3.4;
    ctx.lineCap = 'round';
    for (const [x0, cx, cy, x1, y1] of [[14, 8, -48, 18, -56], [30, 34, -48, 44, -52]]) {
      ctx.beginPath();
      ctx.moveTo(x0, -30);
      ctx.quadraticCurveTo(cx, cy, x1, y1);
      ctx.stroke();
      ctx.beginPath();
      ctx.arc(x1 + 1, y1 - 1, 5, 0, TAU);
      ctx.fill();
    }
    const head = ctx.createRadialGradient(13, -19, 3, 22, -8, 34);
    head.addColorStop(0, '#ffeaa8');
    head.addColorStop(0.5, '#f9c247');
    head.addColorStop(1, '#e6a124');
    ctx.beginPath();
    ctx.arc(22, -8, 27, 0, TAU);
    ctx.fillStyle = head;
    ctx.fill();

    // Face.
    ctx.fillStyle = C.ink;
    ctx.beginPath();
    ctx.ellipse(27, -10, 5.2, 6.6, 0, 0, TAU);
    ctx.fill();
    ctx.beginPath();
    ctx.ellipse(42.5, -8, 4, 6, 0, 0, TAU);
    ctx.fill();
    ctx.fillStyle = '#fff';
    ctx.beginPath();
    ctx.arc(25.4, -12.4, 1.7, 0, TAU);
    ctx.arc(41.4, -10.2, 1.4, 0, TAU);
    ctx.fill();
    ctx.strokeStyle = C.ink;
    ctx.lineWidth = 2.5;
    ctx.beginPath();
    ctx.arc(35, -2.5, 6, Math.PI * 0.15, Math.PI * 0.85);
    ctx.stroke();

    ctx.restore();
  }

  // Where the bee is at time tau (0..RUN) of one delivery. spin is the loop-the-loop angle.
  function beeAt(tau, L) {
    const { S, E, A, B, R, X } = L;
    let x;
    let y;
    let spin = 0;
    if (tau < 1.5) {
      // Zips in from the left edge and settles beside the upload button.
      ({ x, y } = cubic(E, L.c1, L.c2, A, span(tau, 0, 1.5, ease.outCubic)));
    } else if (tau < 2.4) {
      // Winds up, then tosses the photo on the bar line (2.0).
      const back = span(tau, 1.7, 2.0, ease.inOutCubic) - span(tau, 2.0, 2.12, ease.outCubic);
      const lunge = span(tau, 2.0, 2.12, ease.outCubic) - span(tau, 2.12, 2.4, ease.inOutCubic);
      x = A.x + (lunge * 0.14 - back * 0.18) * S;
      y = A.y + back * 0.05 * S;
    } else if (tau < 3.3) {
      // Hops over the button to wait on the far side.
      ({ x, y } = quad(A, L.hop, B, span(tau, 2.4, 3.3, ease.inOutCubic)));
    } else if (tau < 4.75) {
      // Waits, nearly still, then dips as it catches the converted photo (4.0 to 4.5).
      const dip = span(tau, 4.4, 4.5, ease.outCubic) - span(tau, 4.5, 4.75, ease.inOutCubic);
      x = B.x;
      y = B.y + dip * 0.1 * S;
    } else if (tau < 6) {
      // Victory loop on the way to its resting spot.
      const p = span(tau, 4.75, 6, ease.inOutCubic);
      const base = quad(B, L.lift, R, p);
      spin = TAU * p;
      x = base.x + Math.sin(spin) * L.loop;
      y = base.y - (1 - Math.cos(spin)) * L.loop;
    } else if (tau < 7.4) {
      // Holds so the label can be read.
      x = R.x;
      y = R.y;
    } else {
      ({ x, y } = quad(R, L.out, X, span(tau, 7.4, 8, ease.inCubic)));
    }
    y += Math.sin(tau * TAU) * 0.035 * S; // hover bob, one a second
    return { x, y, spin };
  }

  function drawLooseTile(ctx, x, y, T, rot, scale, alpha, label, done) {
    ctx.save();
    ctx.globalAlpha = alpha;
    ctx.translate(x, y);
    ctx.rotate(rot);
    ctx.scale(scale, scale);
    drawTile(ctx, T, label, done);
    ctx.restore();
  }

  // layout: { S, icon: {x, y, r}, E, c1, c2, A, hop, B, lift, R, out, X, loop } in canvas pixels.
  function frame(ctx, t, L) {
    const run = Math.floor(t / RUN) % FORMATS.length;
    const tau = t - Math.floor(t / RUN) * RUN;
    const S = L.S;
    const T = S * TILE;
    const I = L.icon;
    const format = FORMATS[run];

    const bee = beeAt(tau, L);
    const before = beeAt(tau - 0.02, L);
    const after = beeAt(tau + 0.02, L);
    const vx = (after.x - before.x) / 0.04;
    const vy = (after.y - before.y) / 0.04;
    const lean = Math.atan2(vy, Math.abs(vx) + 3 * S) + clamp(vx / (14 * S), -0.22, 0.22);
    const tilt = bee.spin ? -bee.spin : lean;

    // Dotted flight trail, only while it is moving fast.
    ctx.fillStyle = C.deep;
    for (let k = 1; k <= 12; k++) {
      const tk = tau - k * 0.035;
      if (tk <= 0) break;
      const p = beeAt(tk, L);
      const q = beeAt(tk - 0.035, L);
      const speed = Math.hypot(p.x - q.x, p.y - q.y) / 0.035 / S;
      const alpha = clamp((speed - 1.2) / 3) * (1 - k / 13) * 0.5;
      if (alpha < 0.01) continue;
      ctx.globalAlpha = alpha;
      ctx.beginPath();
      ctx.arc(p.x, p.y + 0.1 * S, 0.05 * S * (1 - k / 24), 0, TAU);
      ctx.fill();
    }
    ctx.globalAlpha = 1;

    // The upload button takes the photo in: a ring, then sparks that gather and go quiet.
    const absorb = span(tau, 2.36, 2.9, ease.outCubic);
    if (tau > 2.36 && absorb < 1) {
      ctx.globalAlpha = (1 - absorb) * 0.55;
      ctx.lineWidth = I.r * 0.1;
      ctx.strokeStyle = C.deep;
      ctx.beginPath();
      ctx.arc(I.x, I.y, I.r * lerp(1.05, 1.75, absorb), 0, TAU);
      ctx.stroke();
    }
    const busy = span(tau, 2.4, 2.7, ease.outCubic) * (1 - span(tau, 3.3, 3.7, ease.inCubic));
    if (busy > 0) {
      ctx.globalAlpha = busy;
      for (let i = 0; i < 6; i++) {
        const a = (i / 6) * TAU + (tau - 2.4) * TAU * 0.9;
        const d = I.r * (0.35 + 1.0 * busy);
        hexagon(ctx, I.x + Math.cos(a) * d, I.y + Math.sin(a) * d, I.r * 0.14, a);
        ctx.fillStyle = i % 2 ? C.deep : C.honey;
        ctx.fill();
      }
    }

    // The pop (4.0): the biggest moment. A ring and honeycomb confetti.
    if (tau >= 4 && tau < 5) {
      const ring = span(tau, 4, 4.6, ease.outCubic);
      ctx.globalAlpha = (1 - ring) * 0.7;
      ctx.lineWidth = I.r * 0.14 * (1 - ring) + 1;
      ctx.strokeStyle = C.honey;
      ctx.beginPath();
      ctx.arc(I.x, I.y, I.r * lerp(1, 2.2, ring), 0, TAU);
      ctx.stroke();

      const r = rand(run * 97 + 11);
      const out = span(tau, 4, 4.9, ease.outExpo);
      const fade = 1 - span(tau, 4.5, 5);
      const fall = span(tau, 4, 5, ease.inCubic);
      for (let i = 0; i < 10; i++) {
        const a = -Math.PI * (0.06 + 0.88 * r()); // upward only: the label below stays clean
        const d = I.r * (1.5 + r() * 1.1);
        const size = I.r * (0.1 + r() * 0.1);
        const rot = r() * TAU;
        ctx.globalAlpha = fade;
        hexagon(ctx, I.x + Math.cos(a) * d * out, I.y + Math.sin(a) * d * out + fall * I.r * 0.3, size, rot + out * 2);
        ctx.fillStyle = [C.honey, C.deep, '#ffd67a', C.ink][i % 4];
        ctx.fill();
      }
    }
    ctx.globalAlpha = 1;

    // The photo in the air: tossed in as HEIC, popped out converted.
    if (tau >= 2 && tau < 2.4) {
      const from = beeAt(2, L);
      const p = span(tau, 2, 2.4);
      drawLooseTile(
        ctx,
        lerp(from.x + GRIP.x * S, I.x, p),
        lerp(from.y + GRIP.y * S, I.y, p) - Math.sin(p * Math.PI) * 0.45 * S,
        T, p * 0.9, lerp(1, 0.3, ease.inCubic(p)), 1 - span(tau, 2.32, 2.4), 'HEIC', false
      );
    } else if (tau >= 4 && tau < 4.5) {
      const to = beeAt(4.5, L);
      const p = span(tau, 4, 4.5, ease.outCubic);
      drawLooseTile(
        ctx,
        lerp(I.x, to.x + GRIP.x * S, p),
        lerp(I.y, to.y + GRIP.y * S, p) - Math.sin(p * Math.PI) * 0.55 * S,
        T, (1 - p) * -0.7, lerp(0.3, 1, span(tau, 4, 4.3, ease.outBack)), 1, format, true
      );
    }

    let carry = null;
    if (tau < 2) carry = { label: 'HEIC', done: false, sway: -lean * 0.6 };
    else if (tau >= 4.5) carry = { label: format, done: true, sway: bee.spin ? 0 : -lean * 0.6 };
    drawBee(ctx, bee.x, bee.y, S, tilt, t, carry);
  }

  // The resting bee on a transparent canvas: the source of static/motion/hero-bee.webp.
  // After changing how the bee is drawn, save __heroBee.sprite(350) as WebP over that file.
  function sprite(width) {
    const S = width / SPRITE.w;
    const c = document.createElement('canvas');
    c.width = width;
    c.height = Math.round(S * SPRITE.h);
    drawBee(c.getContext('2d'), S * SPRITE.ox, S * SPRITE.oy, S, 0, POSTER, { label: FORMATS[0], done: true });
    return c;
  }

  function mount() {
    const main = document.querySelector('.main-content');
    const box = document.getElementById('uploadArea');
    const iconEl = box && box.querySelector('.upload-icon');
    const stillEl = box && box.querySelector('.hero-bee-still');
    const h1 = document.querySelector('.hero h1');
    if (!main || !iconEl || !stillEl || !h1) return;

    const calm = window.matchMedia('(prefers-reduced-motion: reduce)');
    const canvas = document.createElement('canvas');
    canvas.className = 'hero-bee-canvas';
    canvas.setAttribute('aria-hidden', 'true');
    const ctx = canvas.getContext('2d');

    let L = null;
    let dpr = 1;
    let live = false;
    let visible = true;
    let settle = false; // someone has picked a photo: finish this delivery and rest
    let held = null; // a fixed time, set by hold() when checking stills
    let raf = 0;
    let played = 0;
    let last = 0;

    // Everything is placed from the real page: the upload button and the still image.
    function measure() {
      const o = main.getBoundingClientRect();
      const rel = (el) => {
        const r = el.getBoundingClientRect();
        return { x: r.left - o.left, y: r.top - o.top, w: r.width, h: r.height };
      };
      const b = rel(box);
      const ic = rel(iconEl);
      const st = rel(stillEl);
      const head = rel(h1);
      if (!b.w || !st.w) return (L = null); // the upload tab is hidden

      const w = o.width;
      const S = st.w / SPRITE.w;
      const R = pt(st.x + (st.w * SPRITE.ox) / SPRITE.w, st.y + (st.h * SPRITE.oy) / SPRITE.h);
      const wide = R.x > b.x + b.w; // the still sits out in the page margin
      const icon = { x: ic.x + ic.w / 2, y: ic.y + ic.h / 2, r: ic.w / 2 };
      // In the box it waits further left and a little higher, clear of the button label.
      const A = wide ? pt(b.x + b.w * 0.17, icon.y) : pt(b.x + b.w * 0.11, R.y - 0.15 * S);
      const B = wide ? pt(b.x + b.w * 0.83, icon.y) : R;
      const E = pt(-S, wide ? head.y + head.h / 2 : A.y - 0.4 * S);
      const X = pt(w + S, R.y - (wide ? 0.8 : 0.2) * S);
      L = {
        S, icon, E, A, B, R, X,
        c1: wide ? pt(b.x * 0.55, E.y) : pt(A.x * 0.2, E.y),
        c2: wide ? pt(b.x * 0.42, A.y) : pt(A.x * 0.5, A.y + 0.3 * S),
        hop: pt((A.x + B.x) / 2, A.y - 0.9 * S),
        lift: wide ? pt(R.x + 0.7 * S, B.y - 0.1 * S) : R,
        out: pt((R.x + X.x) / 2, R.y + 0.25 * S),
        // Wide: a real loop-the-loop. In the box: a roll on the spot, so it stays inside.
        loop: (wide ? 0.5 : -0.15) * S,
      };

      const h = Math.ceil(Math.max(b.y + b.h, R.y + 1.3 * S) + 16);
      dpr = Math.min(window.devicePixelRatio || 1, 2);
      if (w * h * dpr * dpr > 3.2e6) dpr = Math.sqrt(3.2e6 / (w * h)); // keep big screens cheap
      canvas.style.height = h + 'px';
      canvas.width = Math.round(w * dpr);
      canvas.height = Math.round(h * dpr);
    }

    function draw(t) {
      ctx.setTransform(1, 0, 0, 1, 0, 0);
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      if (!L) return;
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
      frame(ctx, t, L);
    }

    function tick(now) {
      raf = 0;
      if (!live) return;
      if (held !== null) return draw(held);
      played += last ? Math.min((now - last) / 1000, 0.1) : 0;
      last = now;
      const t = played % DURATION;
      if (settle && t % RUN >= POSTER) return draw(t - (t % RUN) + POSTER);
      draw(t);
      if (visible && !document.hidden) raf = requestAnimationFrame(tick);
    }

    function wake() {
      last = 0;
      if (live && !raf) raf = requestAnimationFrame(tick);
    }

    function start() {
      if (live || calm.matches) return;
      live = true;
      main.appendChild(canvas);
      document.documentElement.classList.add('hero-bee-live');
      measure();
      wake();
    }

    function stop() {
      live = false;
      cancelAnimationFrame(raf);
      raf = 0;
      canvas.remove();
      document.documentElement.classList.remove('hero-bee-live');
    }

    new IntersectionObserver((entries) => {
      visible = entries[0].isIntersecting;
      if (visible) wake();
    }).observe(canvas);
    const relayout = () => {
      if (!live) return;
      measure();
      wake();
    };
    new ResizeObserver(relayout).observe(main);
    new ResizeObserver(relayout).observe(box);
    document.addEventListener('visibilitychange', wake);
    calm.addEventListener('change', () => (calm.matches ? stop() : start()));
    const rest = () => {
      settle = true;
    };
    box.addEventListener('drop', rest);
    const input = document.getElementById('fileInput');
    if (input) input.addEventListener('change', rest);

    // For checking stills: __heroBee.hold(2.2) freezes that moment; hold(null) plays again.
    window.__heroBee = {
      duration: DURATION,
      run: RUN,
      poster: POSTER,
      sprite,
      hold(t) {
        held = t;
        wake();
      },
    };

    start();
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', mount);
  else mount();
})();
