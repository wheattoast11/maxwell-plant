// SPDX-License-Identifier: AGPL-3.0-or-later
// Copyright (c) 2026 Intuition Labs LLC
//
// sbStyles.js - the Switchboard object vocabulary's own scoped style island.
// ONE idempotent <style id="sb-styles"> tag holding every `--sb-*` custom
// property from the frozen kit tokens (maxwell/design/switchboard/tokens/*.css)
// plus the four sb-* keyframes. Mirrors dsStyles.js's ensureDsStyles idiom
// exactly - one <style> per island, injected once, never touching the global
// stylesheet - so this module lifts out of this repo verbatim.
//
// TWO deliberate departures from the raw kit, both mandated by the frozen seam
// (maxwell/docs/DESIGN-KIT.md):
//
//   1. SCOPE, not :root (correspondence condition 1). The kit's tokens.css
//      files declare `--sb-*` on `:root`; here they live under a `.sb-scope`
//      class instead, so the site's OKLCH base tokens stay authoritative
//      page-wide and the `--sb-*` set is the OBJECT vocabulary for projective
//      surfaces ONLY. Every sb primitive tags its own root with `sb-scope`
//      (SB_SCOPE below) so the vars resolve wherever a primitive is dropped;
//      a plate/configurator surface can also wrap a whole region once.
//
//   2. NO remote @import (seam doc §6, the font law). The kit's
//      typography.css opens with an `@import url(fonts.googleapis…)` for
//      Archivo + IBM Plex Mono; that is stripped here. `--sb-font-sans` and
//      `--sb-font-mono` still NAME those faces first, but fall back to the
//      portal sans/mono stacks (see canvasStyles.js) - Archivo / IBM Plex
//      Mono render only where a page actually supplies them (plates,
//      configurator islands); everywhere else the portal faces carry.
//
// HOOK: a new `--sb-*` token or `sb-*` keyframe goes HERE (and, for a
// keyframe, into the reduced-motion block below) - never as a differently
// prefixed name elsewhere in src/ds/switchboard, so the whole object
// vocabulary stays one-place-to-edit.

const STYLE_ID = 'sb-styles';

// SB_SCOPE - the class every sb primitive stamps on its root so the scoped
// `--sb-*` custom properties resolve on it and cascade to its subtree.
export const SB_SCOPE = 'sb-scope';

const CSS = `
.${SB_SCOPE} {
  /* ink */
  --sb-ink-1:#26221c; --sb-ink-2:#55503f; --sb-ink-3:#8d867a; --sb-ink-4:#c6bfae;
  /* paper tonal ladder (recessed to raised) */
  --sb-paper-well:#e2dbc9; --sb-paper-desk:#e7e1d3; --sb-paper-region:#efeadd;
  --sb-paper-panel:#f7f4ec; --sb-paper-card:#fbf9f3; --sb-paper-raised:#fffdf8;
  /* type hues - identity only, never order */
  --sb-hue-process:#33302a; --sb-hue-feed:#1f7a68; --sb-hue-product:#2e6da4;
  --sb-hue-policy:#6f56b8; --sb-hue-constraint:#8a3b2e; --sb-hue-ghost:#b0417a;
  --sb-hue-controller:#57652a;
  /* the one signal - open obligation (kit L6); NEVER aliased to site --accent */
  --sb-signal-open:#b3661a;
  /* state */
  --sb-state-stub:#8d867a; --sb-state-open:var(--sb-signal-open); --sb-state-sealed:#57652a;
  /* lines */
  --sb-line-1:#d9d2c2; --sb-line-2:#eee8da; --sb-line-strong:#b8b09c;
  /* semantic aliases */
  --sb-text-strong:var(--sb-ink-1); --sb-text-body:var(--sb-ink-2); --sb-text-muted:var(--sb-ink-3);
  --sb-surface-card:var(--sb-paper-card); --sb-surface-panel:var(--sb-paper-panel);
  --sb-surface-desk:var(--sb-paper-desk); --sb-surface-raised:var(--sb-paper-raised);

  /* typography - sans NAMES, mono MEASURES (kit L1). NO remote @import:
     Archivo / IBM Plex Mono lead, portal stacks carry the fallback. */
  --sb-font-sans:'Archivo',system-ui,-apple-system,'Segoe UI',Roboto,sans-serif;
  --sb-font-mono:'IBM Plex Mono','Geist Mono',ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;
  --sb-size-display:26px; --sb-lh-display:1.15; --sb-weight-display:650;
  --sb-size-title:20px;   --sb-size-name:16px;  --sb-weight-name:600;
  --sb-size-body:13px;    --sb-lh-body:1.55;
  --sb-size-data:14px;    --sb-weight-data:500; /* tabular-nums */
  --sb-size-unit:11px;    /* never bold, never colored (kit L2) */
  --sb-size-micro:11px;
  --sb-size-label:10px;   --sb-track-label:.14em; --sb-weight-label:600;

  /* spacing - 4-base scale; new meaning = two steps up; inside <= outside */
  --sb-space-atom:4px;  --sb-space-row:8px;   --sb-space-rows:12px; --sb-space-pad:16px;
  --sb-space-group:24px; --sb-space-cards:32px; --sb-space-lane:48px; --sb-space-region:64px;
  --sb-radius-chip:6px; --sb-radius-card:10px; --sb-radius-node:12px; --sb-radius-pill:20px;

  /* depth = agency, never emphasis (D-1 well … D3 floating) */
  --sb-elev-well:inset 0 1px 3px rgba(60,50,30,.16);
  --sb-elev-rest:0 1px 2px rgba(60,50,30,.08);
  --sb-elev-hand:0 2px 6px rgba(60,50,30,.13),0 8px 18px rgba(60,50,30,.09);
  --sb-elev-float:0 10px 28px rgba(60,50,30,.22);

  /* texture - grain marks the system's hand (derived); smooth = drawn */
  --sb-tex-ghost:repeating-linear-gradient(45deg,rgba(176,65,122,.13) 0 2px,transparent 2px 6px);
  --sb-tex-ghost-strong:repeating-linear-gradient(-45deg,rgba(176,65,122,.3) 0 3px,transparent 3px 8px);
  --sb-tex-controller:repeating-linear-gradient(45deg,rgba(87,101,42,.09) 0 2px,transparent 2px 6px);
  --sb-tex-dotgrid:radial-gradient(circle,#d8d1c0 1px,transparent 1px);
  --sb-tex-dotgrid-size:16px 16px;

  /* motion timing */
  --sb-dur-settle:var(--t-step); --sb-ease:var(--ease);
}

/* motion law: a surface may move only while its quantity is off steady state.
   Keyframes are always global (they can't be scoped under a class) - the
   primitives gate them by applying an inline animation only while off steady
   state (SealWell while open>0, VentFlux while residual>~0). */
@keyframes sb-spin{to{transform:rotate(1turn)}}
@keyframes sb-drift{to{background-position:0 -28px}}
@keyframes sb-pulse{0%,100%{transform:scale(.92);opacity:.5}50%{transform:scale(1.12);opacity:.95}}
@keyframes sb-focus{0%,18%{filter:blur(5px);opacity:.35}55%,100%{filter:blur(0);opacity:1}}

/* prefers-reduced-motion: every sb-* animation is applied INLINE (a style
   prop, never a class), so - exactly as dsStyles.js does for its ll* set - an
   attribute selector on the serialized style attribute is the one shape that
   can reach an inline animation by name and neutralize it. Nothing outside an
   sb primitive is touched. */
@media (prefers-reduced-motion: reduce) {
  [style*="sb-spin"], [style*="sb-drift"], [style*="sb-pulse"], [style*="sb-focus"] {
    animation: none !important;
  }
}
`;

// ensureSbStyles - idempotent: safe to call from every sb primitive's render.
// First call wins; later calls are no-ops (checked by id). Guarded for
// non-browser hosts (SSR/prerender/tests without a real DOM), same as
// ensureDsStyles - this app prerenders static shells, so this must never
// assume `document` exists.
export function ensureSbStyles() {
  if (typeof document === 'undefined') return;
  if (document.getElementById(STYLE_ID)) return;
  const el = document.createElement('style');
  el.id = STYLE_ID;
  el.textContent = CSS;
  document.head.appendChild(el);
}

// SB_TOKENS - the JS mirror the seam doc's placement map names (site
// sbStyles.js "+ JS mirror export"). Raw values only for the semantic scalars
// a JS consumer plausibly needs (type hues, the one signal, the state triad) -
// NOT a full duplicate of the CSS. The CSS island above stays authoritative;
// this is a read-only convenience so a JS caller can resolve a hue without a
// getComputedStyle round-trip. Kept intentionally small to avoid a second
// source of truth for the whole token set.
export const SB_TOKENS = {
  hue: {
    process: '#33302a', feed: '#1f7a68', product: '#2e6da4', policy: '#6f56b8',
    constraint: '#8a3b2e', ghost: '#b0417a', controller: '#57652a',
  },
  signalOpen: '#b3661a',
  state: { stub: '#8d867a', open: '#b3661a', sealed: '#57652a' },
};
