import { act } from "react";
import { createRoot } from "react-dom/client";
import { describe, expect, it, vi } from "vitest";
import type { Portfolio } from "./types";

const DATA: Portfolio = {
  connected: true, hidden: 14,
  projects: [{ id: "f1", title: "IrO2 crystal structure prediction", dossier: "active", updated_at: "", archived: 1, steps: 0, done: 0,
    items: [{ ref: "whiteboard:w1", kind: "whiteboard", title: "IrO2 digest probe", status: "active", steps: 0, step: 0, updated_at: "" }] }],
  loose: [{ ref: "canvas:c1", refs: ["canvas:c1"], kind: "canvas", title: "IrO2 interface bench", status: "active", steps: 0, step: 0, updated_at: "", suggest: "f1" }],
};
const file = vi.fn(async () => DATA);
vi.mock("./api", () => ({ api: { portfolio: async () => DATA, file, startProject: vi.fn(async () => DATA) } }));

(globalThis as { IS_REACT_ACT_ENVIRONMENT?: boolean }).IS_REACT_ACT_ENVIRONMENT = true;

describe("the projects home", () => {
  it("shows each project, the items not in one, and adds one to the suggested project", async () => {
    const { PortfolioPage } = await import("./PortfolioPage");
    const host = document.createElement("div");
    document.body.replaceChildren(host);
    await act(async () => createRoot(host).render(<PortfolioPage />));
    expect(host.querySelectorAll(".pf-card")).toHaveLength(1);
    expect(host.textContent).toContain("Not in a project yet");
    expect(host.textContent).toContain("14 archived items are not shown.");
    const add = [...host.querySelectorAll("button")].find((b) => b.textContent?.startsWith("Add to")) as HTMLButtonElement;
    await act(async () => add.click());
    expect(file).toHaveBeenCalledWith(["canvas:c1"], "f1");
  });
});
