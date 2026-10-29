// SPDX-License-Identifier: AGPL-3.0-or-later
// Copyright (c) 2026 Intuition Labs LLC
//
// TypeGlyph.jsx — one single-codepoint glyph per artifact type, drawn in its
// own hue, legible before any word is read (kit L5: glyph carries type, stroke
// carries state, color reinforces). Translated verbatim from the frozen kit
// (maxwell/design/switchboard/components/core/TypeGlyph.jsx) into ds
// conventions: inline-style token-driven, self-scoping via SB_SCOPE, mounting
// the sb style island on render.
//
// TYPE_META is the exported source of truth for the seven types' glyph / hue /
// label / drawn flag — ObligationRow and ArtifactCard both read it, so a new
// type is added in exactly one place. `drawn:false` (controller, ghost) marks
// the DERIVED / system-minted types that carry grain (kit channel law:
// texture → provenance).

import React from 'react';
import { ensureSbStyles, SB_SCOPE } from './sbStyles';

export const TYPE_META = {
  process:    { glyph: '▢', hue: 'var(--sb-hue-process)',    label: 'process',    drawn: true  },
  feed:       { glyph: '⇥', hue: 'var(--sb-hue-feed)',       label: 'feed',       drawn: true  },
  product:    { glyph: '↦', hue: 'var(--sb-hue-product)',    label: 'product',    drawn: true  },
  policy:     { glyph: '§', hue: 'var(--sb-hue-policy)',     label: 'policy',     drawn: true  },
  constraint: { glyph: '‖', hue: 'var(--sb-hue-constraint)', label: 'constraint', drawn: true  },
  controller: { glyph: '⊸', hue: 'var(--sb-hue-controller)', label: 'controller', drawn: false },
  ghost:      { glyph: '↥', hue: 'var(--sb-hue-ghost)',      label: 'ghost',      drawn: false }
};

export function TypeGlyph({ type = 'feed', size = 'chip', title }) {
  ensureSbStyles();
  const m = TYPE_META[type] || TYPE_META.feed;
  const base = { fontFamily: 'var(--sb-font-mono)', fontWeight: 500, lineHeight: 1, display: 'inline-flex', alignItems: 'center', justifyContent: 'center' };
  const skins = {
    inline: { color: m.hue, fontSize: 12 },
    chip:   { color: m.hue, fontSize: 12, border: '1px solid ' + m.hue, borderRadius: 'var(--sb-radius-pill)', padding: '2px 9px' },
    header: { color: 'var(--sb-paper-raised)', background: m.hue, fontSize: 14, borderRadius: 'var(--sb-radius-chip)', padding: '3px 8px' },
    node:   { color: m.hue, fontSize: 16, border: '1.5px solid ' + m.hue, borderRadius: 8, padding: '4px 10px', background: 'var(--sb-paper-raised)' }
  };
  return <span className={SB_SCOPE} title={title || m.label} style={{ ...base, ...(skins[size] || skins.chip) }}>{m.glyph}</span>;
}
