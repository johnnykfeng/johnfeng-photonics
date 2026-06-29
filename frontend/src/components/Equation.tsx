import "katex/dist/katex.min.css";
import { BlockMath } from "react-katex";

interface EquationProps {
  math: string;
}

export function Equation({ math }: EquationProps) {
  return (
    <div className="my-2 overflow-x-auto">
      <BlockMath math={math} />
    </div>
  );
}

interface EquationListProps {
  equations: string[];
}

export function EquationList({ equations }: EquationListProps) {
  return (
    <div className="space-y-1">
      {equations.map((equation) => (
        <Equation key={equation} math={equation} />
      ))}
    </div>
  );
}
