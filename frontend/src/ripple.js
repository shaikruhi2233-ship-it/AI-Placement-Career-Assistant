/**
 * Click feedback: a material-style ripple that spreads from the exact point
 * where a button / card / link was clicked. Implemented once with event
 * delegation, so every current and future button gets it automatically.
 *
 * The ripple lives inside its own clipped wrapper (inset: 0; overflow:
 * hidden), so the clicked element's own layout and overflow are untouched.
 */
const SELECTOR = [
  "button:not(:disabled)",
  ".btn",
  ".quick",
  ".kpi",
  ".nav-link",
  ".step",
  ".hero-gauge",
  ".lp-feature",
  ".auth-tabs a",
  ".dropzone",
].join(",");

function onPointerDown(e) {
  if (e.button !== 0) return;
  const host = e.target.closest(SELECTOR);
  if (!host) return;
  if (window.matchMedia?.("(prefers-reduced-motion: reduce)").matches) return;

  const rect = host.getBoundingClientRect();
  if (getComputedStyle(host).position === "static") host.style.position = "relative";

  const wrap = document.createElement("span");
  wrap.className = "ripple-wrap";
  const dot = document.createElement("span");
  dot.className = "ripple";
  const size = Math.max(rect.width, rect.height) * 2.2;
  dot.style.width = dot.style.height = `${size}px`;
  dot.style.left = `${e.clientX - rect.left - size / 2}px`;
  dot.style.top = `${e.clientY - rect.top - size / 2}px`;
  wrap.appendChild(dot);
  host.appendChild(wrap);

  const cleanup = () => wrap.remove();
  dot.addEventListener("animationend", cleanup, { once: true });
  setTimeout(cleanup, 900); // safety net
}

export function installRipple() {
  if (typeof document === "undefined" || window.__rippleInstalled) return;
  window.__rippleInstalled = true;
  document.addEventListener("pointerdown", onPointerDown, { passive: true });
}
