import ELDLogSheet from "./ELDLogSheet";
import type { ELDLog } from "../types/trip";
import "./ELDLogs.css";

interface Props {
  logs: ELDLog[];
}

export default function ELDLogs({ logs }: Props) {
  if (logs.length === 0) return null;

  return (
    <div className="eld-logs">
      <h3>Daily Log Sheets</h3>
      <div className="eld-logs-list">
        {logs.map((log) => (
          <ELDLogSheet key={log.date} log={log} />
        ))}
      </div>
    </div>
  );
}
