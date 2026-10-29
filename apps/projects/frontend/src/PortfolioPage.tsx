import { DataTable, folderApi } from "@plantcraft/ui";
import { useEffect, useState, type DragEvent } from "react";
import { api } from "./api";
import { formatAgo, t } from "./i18n";
import { navigate } from "./nav";
import type { Item, Loose, Portfolio, Project } from "./types";
import { ErrorBox, Heading, Loading, message } from "./ui";

const KIND: Record<Item["kind"], string> = { whiteboard: "Whiteboard", canvas: "Process box", tasks: "Task list", research: "Research" };

export function Kind({ kind }: { kind: Item["kind"] }) {
  return <span className={`pf-kind pf-kind-${kind}`}>{t(KIND[kind])}</span>;
}

/** A gear whose teeth are the project's items and whose filled teeth are the steps done. */
export function Gear({ project }: { project: Project }) {
  const teeth = Math.max(project.items.length, 3);
  const filled = project.steps ? Math.round((project.done / project.steps) * teeth) : 0;
  const r = 14 + Math.sqrt(project.items.length + 1) * 4;
  return <svg className="pf-gear" viewBox={`${-r - 4} ${-r - 4} ${2 * r + 8} ${2 * r + 8}`} width={2 * r + 8} aria-hidden>
    <circle r={r} className="pf-gear-body" />
    {Array.from({ length: teeth }, (_, k) => {
      const a = -Math.PI / 2 + (k / teeth) * Math.PI * 2;
      return <circle key={k} cx={Math.cos(a) * r * 0.7} cy={Math.sin(a) * r * 0.7} r={2.4} className={k < filled ? "pf-tooth-done" : "pf-tooth"} />;
    })}
  </svg>;
}

function usePortfolio() {
  const [data, setData] = useState<Portfolio | null>(null);
  const [error, setError] = useState("");
  const load = () => api.portfolio().then(setData).catch((err) => setError(message(err)));
  useEffect(() => { void load(); }, []);
  const move = (refs: string[], projectId: string) =>
    Promise.all(refs.map((ref) => folderApi.move("item", ref, projectId))).then(load).catch((err) => setError(message(err)));
  const start = (title: string, refs: string[]) =>
    folderApi.create("item", title).then((folder) => move(refs, folder.folder_id)).catch((err) => setError(message(err)));
  return { data, error, move, start };
}

function MoveTo({ projects, current, onMove }: { projects: Project[]; current?: string; onMove: (projectId: string) => void }) {
  return <select className="pf-move" value="" aria-label={t("Move to project")} onChange={(e) => e.target.value && onMove(e.target.value)}>
    <option value="">{t("Move to…")}</option>
    {projects.filter((p) => p.id !== current).map((p) => <option key={p.id} value={p.id}>{p.title}</option>)}
  </select>;
}

export function PortfolioPage() {
  const { data, error, move, start } = usePortfolio();
  const [over, setOver] = useState("");
  if (error) return <ErrorBox text={error} />;
  if (!data) return <Loading />;
  if (!data.connected) return <ErrorBox text={t("Projects is not connected to Maxwell yet. Ask your administrator.")} />;
  const suggested = (l: Loose) => data.projects.find((p) => p.id === l.suggest);
  const drop = (e: DragEvent, projectId: string) => {
    e.preventDefault();
    setOver("");
    const refs = e.dataTransfer.getData("text/plain");
    if (refs) void move(refs.split(" "), projectId);
  };
  return <div className="pf">
    <Heading title={t("Projects")} />
    {data.projects.length === 0 && <p className="pf-quiet">{t("No projects yet. Start one from any item below.")}</p>}
    <div className="pf-grid">
      {data.projects.map((p) => <button key={p.id} className={`pf-card${over === p.id ? " pf-over" : ""}`}
        onClick={() => navigate(`/p/${encodeURIComponent(p.id)}`)}
        onDragOver={(e) => { e.preventDefault(); setOver(p.id); }} onDragLeave={() => setOver("")} onDrop={(e) => drop(e, p.id)}>
        <Gear project={p} />
        <span className="pf-title">{p.title}</span>
        <span className="pf-quiet">{t("{n} items", { n: p.items.length })}{p.steps > 0 && ` · ${t("{done} of {steps} done", { done: p.done, steps: p.steps })}`}</span>
      </button>)}
    </div>
    {data.loose.length > 0 && <>
      <h2 className="pf-sub">{t("Not in a project yet")}</h2>
      <div className="pf-dock">
        {data.loose.map((l) => <div key={l.ref} className="pf-chip" draggable onDragStart={(e) => e.dataTransfer.setData("text/plain", l.refs.join(" "))}>
          <Kind kind={l.kind} /><span>{l.title}{l.refs.length > 1 && ` (${l.refs.length})`}</span>
          {suggested(l) && <button className="pf-act" onClick={() => void move(l.refs, l.suggest!)}>{t("Add to {name}", { name: suggested(l)!.title })}</button>}
          <MoveTo projects={data.projects} onMove={(id) => void move(l.refs, id)} />
          <button className="pf-act" onClick={() => void start(l.title, l.refs)}>{t("New project")}</button>
        </div>)}
      </div>
    </>}
    {data.hidden > 0 && <p className="pf-quiet">{t("{n} archived items are not shown.", { n: data.hidden })}</p>}
  </div>;
}

export function ProjectPage({ projectId }: { projectId: string }) {
  const { data, error, move } = usePortfolio();
  if (error) return <ErrorBox text={error} />;
  if (!data) return <Loading />;
  const project = data.projects.find((p) => p.id === projectId);
  if (!project) return <ErrorBox text={t("Project not found.")} />;
  return <div className="pf">
    <Heading title={project.title} actions={<Gear project={project} />} />
    <DataTable rows={project.items} rowKey={(i) => i.ref} label={t("Items")} searchText={(i) => i.title}
      initialSort={{ key: "when", descending: true }}
      columns={[
        { key: "kind", label: t("Type"), sort: (i) => i.kind, filter: true, render: (i) => <Kind kind={i.kind} /> },
        { key: "title", label: t("Name"), sort: (i) => i.title, render: (i) => i.title },
        { key: "progress", label: t("Done"), sort: (i) => i.step, render: (i) => (i.steps ? `${i.step} / ${i.steps}` : "") },
        { key: "when", label: t("Changed"), sort: (i) => i.updated_at, render: (i) => formatAgo(i.updated_at) },
        { key: "move", label: "", render: (i) => <>
          <MoveTo projects={data.projects} current={project.id} onMove={(id) => void move([i.ref], id)} />
          {!i.linked && <button className="pf-act" onClick={() => void move([i.ref], "")}>{t("Remove")}</button>}
        </> },
      ]} />
    {project.archived > 0 && <p className="pf-quiet">{t("{n} archived items are not shown.", { n: project.archived })}</p>}
  </div>;
}
