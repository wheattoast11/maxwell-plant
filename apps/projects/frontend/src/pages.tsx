import { tourClosing, tt, type ShellNavItem, type TourStep } from "@plantcraft/ui";
import { FolderKanban, NotebookPen } from "lucide-react";

/** The app's own pages in the suite frame (app standard, section 10); Help is the frame's own entry.
 * Projects is home; Notebook holds each note and the asset deep link (`/assets/<id>`). */
export const NAV: Array<Omit<ShellNavItem, "label"> & { label: string }> = [
  { to: "/", label: "Projects", icon: <FolderKanban />, match: (path) => path === "/" || path.startsWith("/p/") },
  {
    to: "/notes",
    label: "Notebook",
    icon: <NotebookPen />,
    match: (path) => path.startsWith("/notes") || path.startsWith("/assets/"),
  },
];

/** The app's guided tour (@plantcraft/ui): opens the first time a person opens the app. */
export function tourSteps(): TourStep[] {
  return [
    {
      title: tt("Welcome to Projects"),
      body: tt("Every project in one list. Anything not in a project yet sits under the cards: add it to one, or start a project from it."),
    },
    {
      path: "/notes",
      target: ".pcs-content .panel",
      title: tt("Notebook"),
      body: tt("Every note, newest first. An editor writes one on any asset of PlantCraft's asset tree; Ctrl+K finds them from anywhere in the suite."),
    },
    tourClosing(),
  ];
}
