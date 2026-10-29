import { ObligationRow } from "./switchboard/ObligationRow";
import { SealWell } from "./switchboard/SealWell";
import { StateChip } from "./switchboard/StateChip";
import { TypeGlyph, type SbType } from "./switchboard/TypeGlyph";
import { Heading } from "./ui";

type Step = { id: string; type: SbType; name: string; open: string[] };

export const SAMPLE_PROJECT: { name: string; steps: Step[] } = {
  name: "Boiler 2 feedwater retrofit",
  steps: [
    { id: "s1", type: "process", name: "Feedwater loop FIC-1003", open: ["Valve trim size not confirmed"] },
    { id: "s2", type: "feed", name: "Historian tags FT-1003, LT-1001", open: [] },
    { id: "s3", type: "policy", name: "Management of change MOC-214", open: ["Operations sign-off", "Rollback setpoint"] },
    { id: "s4", type: "constraint", name: "Drum level 40 to 60 %", open: [] },
    { id: "s5", type: "controller", name: "Three-element level control", open: ["Tuning from step test"] },
  ],
};

export function BoardPage({ project = SAMPLE_PROJECT }: { project?: typeof SAMPLE_PROJECT }) {
  const open = project.steps.reduce((sum, step) => sum + step.open.length, 0);
  return <div className="panel projects-board">
    <Heading title={project.name} actions={<><StateChip state={open ? "draft" : "sealed"} count={open} /><SealWell open={open} /></>} />
    {project.steps.map((step) => <div key={step.id} className="projects-board-step">
      <div className="projects-board-name"><TypeGlyph type={step.type} size="chip" /> <span>{step.name}</span></div>
      {step.open.map((question) => <ObligationRow key={question} type={step.type}>{question}</ObligationRow>)}
    </div>)}
  </div>;
}
