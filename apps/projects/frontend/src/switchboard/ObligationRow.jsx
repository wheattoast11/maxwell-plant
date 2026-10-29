// SPDX-License-Identifier: AGPL-3.0-or-later
// Copyright (c) 2026 Intuition Labs LLC
//
// ObligationRow.jsx — one open obligation in the ledger, typed by glyph + hue,
// dashed stroke (dashed = open). Derived types (controller, ghost — TYPE_META
// drawn:false) carry grain (kit channel law: texture → provenance, grain =
// system-minted). Clicking focuses the discharging widget. The obligation
// ledger ↔ the receipts spine: a row per open obligation, discharged by
// evidence, seal only at zero. Translated from the frozen kit into ds
// conventions; reads TYPE_META (the single source of truth for the 7 types).

import React from 'react';
import { ensureSbStyles, SB_SCOPE } from './sbStyles';
import { TYPE_META } from './TypeGlyph';

export function ObligationRow({ type = 'controller', children, onClick }) {
  ensureSbStyles();
  const m = TYPE_META[type] || TYPE_META.controller;
  const grained = !m.drawn;
  const Component = onClick ? 'button' : 'div';
  return (
    <Component type={onClick ? 'button' : undefined} className={SB_SCOPE} onClick={onClick} style={{ display: 'flex', width: '100%', gap: 7, alignItems: 'baseline', textAlign: 'left', color: m.hue, border: '1px dashed ' + m.hue, borderRadius: 'var(--sb-radius-chip)', padding: '4px 9px', background: grained ? 'var(--sb-paper-card) ' + (type === 'ghost' ? 'var(--sb-tex-ghost)' : 'var(--sb-tex-controller)') : 'var(--sb-paper-card)', fontFamily: 'var(--sb-font-mono)', fontWeight: 500, fontSize: '10.5px', cursor: onClick ? 'pointer' : 'default' }}>
      <span>{m.glyph}</span>
      <span style={{ fontFamily: 'var(--sb-font-sans)', fontWeight: 400, fontSize: '11.5px', color: 'var(--sb-text-body)' }}>{children}</span>
    </Component>
  );
}
