import type { JSX } from "react";
export type SbType = "process" | "feed" | "product" | "policy" | "constraint" | "controller" | "ghost";
export function TypeGlyph(props: { type?: SbType; size?: "inline" | "chip" | "header" | "node"; title?: string }): JSX.Element;
