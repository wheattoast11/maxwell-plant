// SPDX-License-Identifier: AGPL-3.0-or-later
// Copyright (c) 2026 Intuition Labs LLC
//
// SealWell.jsx - the board-level seal dial (gradient-descent readout): an
// amber arc for the remaining obligations, circulating (sb-spin) while open>0,
// fusing solid to the sealed hue and STOPPING at zero. This is the motion law
// made literal - a surface moves only while its quantity is off steady state;
// seal = ledger empty = still. Translated from the frozen kit into ds
// conventions; the animation is applied INLINE so dsStyles-style reduced-motion
// neutralization in sbStyles.js can reach it.

import React from 'react';
import { ensureSbStyles, SB_SCOPE } from './sbStyles';

export function SealWell({ open = 0, size = 62 }) {
  ensureSbStyles();
  const sealed = open <= 0;
  const share = Math.min(open, 10) * 10;
  return (
    <div className={SB_SCOPE} style={{ position: 'relative', width: size, height: size }}>
      <div style={{ position: 'absolute', inset: 0, borderRadius: '50%',
        background: sealed ? 'var(--sb-state-sealed)' : 'conic-gradient(from 0deg, var(--sb-signal-open) 0 ' + share + '%, var(--sb-paper-well) ' + share + '% 100%)',
        animation: sealed ? 'none' : 'sb-spin calc(6 * var(--t-second)) linear infinite' }} />
      <div style={{ position: 'absolute', inset: size * 0.11, borderRadius: '50%', background: 'var(--sb-paper-card)', display: 'flex', alignItems: 'center', justifyContent: 'center', fontFamily: 'var(--sb-font-mono)', fontWeight: 600, fontSize: size * 0.24, color: sealed ? 'var(--sb-state-sealed)' : 'var(--sb-signal-open)' }}>{sealed ? '●' : open}</div>
    </div>
  );
}
