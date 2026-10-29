// SPDX-License-Identifier: AGPL-3.0-or-later
// Copyright (c) 2026 Intuition Labs LLC
//
// StateChip.jsx — the state triad readout, identical everywhere: stub ○ /
// draft ◐ (n open) / sealed ● (kit's ○ ◐ ● ↔ manifest status named/building/
// live). Amber (--sb-state-open) appears ONLY here and on obligation rows —
// the one signal. Translated from the frozen kit into ds conventions.

import React from 'react';
import { ensureSbStyles, SB_SCOPE } from './sbStyles';

export function StateChip({ state = 'draft', count }) {
  ensureSbStyles();
  const map = {
    stub:   { mark: '○', color: 'var(--sb-state-stub)',   text: 'stub' },
    draft:  { mark: '◐', color: 'var(--sb-state-open)',   text: count != null ? count + ' open' : 'draft' },
    sealed: { mark: '●', color: 'var(--sb-state-sealed)', text: 'sealed' }
  };
  const s = map[state] || map.draft;
  return (
    <span className={SB_SCOPE} style={{ fontFamily: 'var(--sb-font-mono)', fontWeight: 500, fontSize: 'var(--sb-size-micro)', color: s.color, display: 'inline-flex', gap: 5, alignItems: 'baseline' }}>
      <span>{s.mark}</span><span>{s.text}</span>
    </span>
  );
}
