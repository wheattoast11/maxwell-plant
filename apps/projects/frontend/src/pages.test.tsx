import { describe, expect, it } from "vitest";
import { NAV } from "./pages";

describe("the frame's pages", () => {
  it("Projects is home and Notebook holds each note and the asset deep link", () => {
    const [projects, notebook] = NAV;
    expect(NAV.map((item) => item.to)).toEqual(["/", "/notes"]);
    for (const path of ["/", "/p/dossier%3Ax"]) expect(projects.match?.(path)).toBe(true);
    for (const path of ["/notes", "/notes/abc", "/assets/FIC-1001"]) expect(notebook.match?.(path)).toBe(true);
    expect(notebook.match?.("/help")).toBe(false);
  });
});
