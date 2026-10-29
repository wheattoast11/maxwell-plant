import { act } from "react";
import { createRoot } from "react-dom/client";
import { describe, expect, it } from "vitest";
import { BoardPage, SAMPLE_PROJECT } from "./BoardPage";

(globalThis as { IS_REACT_ACT_ENVIRONMENT?: boolean }).IS_REACT_ACT_ENVIRONMENT = true;

function mount(project = SAMPLE_PROJECT) {
  const host = document.createElement("div");
  document.body.replaceChildren(host);
  act(() => createRoot(host).render(<BoardPage project={project} />));
  return host;
}

describe("the project board", () => {
  it("draws a glyph per step, a dashed row per open question and the seal count", () => {
    const host = mount();
    expect(host.textContent).toContain("▢");
    expect(host.textContent).toContain("⊸");
    expect(host.querySelectorAll('[style*="dashed"]')).toHaveLength(4);
    expect(host.textContent).toContain("4 open");
    expect(document.getElementById("sb-styles")?.textContent).toContain("--sb-signal-open:#b3661a");
  });

  it("seals when no question is open", () => {
    const host = mount({ ...SAMPLE_PROJECT, steps: SAMPLE_PROJECT.steps.map((s) => ({ ...s, open: [] })) });
    expect(host.querySelectorAll('[style*="dashed"]')).toHaveLength(0);
    expect(host.textContent).toContain("sealed");
    expect(host.textContent).toContain("●");
  });
});
