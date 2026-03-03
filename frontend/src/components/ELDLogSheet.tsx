import type { ELDLog, DutyStatus } from "../types/trip";
import "./ELDLogSheet.css";

const STATUSES: { key: DutyStatus; label: string }[] = [
  { key: "off_duty", label: "Off Duty" },
  { key: "sleeper_berth", label: "Sleeper Berth" },
  { key: "driving", label: "Driving" },
  { key: "on_duty", label: "On Duty" },
];

const STATUS_COLORS: Record<DutyStatus, string> = {
  off_duty: "#6b7280",
  sleeper_berth: "#7c3aed",
  driving: "#2563eb",
  on_duty: "#16a34a",
};

const GRID_LEFT = 110;
const GRID_RIGHT = 690;
const GRID_WIDTH = GRID_RIGHT - GRID_LEFT;
const ROW_HEIGHT = 28;
const GRID_TOP = 30;
const HOUR_WIDTH = GRID_WIDTH / 24;

function hourToX(hour: number): number {
  return GRID_LEFT + (hour / 24) * GRID_WIDTH;
}

function formatDate(dateStr: string): string {
  const d = new Date(dateStr + "T00:00:00");
  return d.toLocaleDateString("en-US", {
    weekday: "short",
    month: "short",
    day: "numeric",
    year: "numeric",
  });
}

interface Props {
  log: ELDLog;
}

export default function ELDLogSheet({ log }: Props) {
  const totalAll =
    log.total_hours.off_duty +
    log.total_hours.sleeper_berth +
    log.total_hours.driving +
    log.total_hours.on_duty;

  return (
    <div className="eld-sheet">
      <div className="eld-header">
        <span className="eld-date">{formatDate(log.date)}</span>
        <span className="eld-total">{totalAll.toFixed(1)}h total</span>
      </div>

      <svg
        viewBox={`0 0 730 ${GRID_TOP + STATUSES.length * ROW_HEIGHT + 10}`}
        className="eld-grid"
      >
        {/* Hour labels */}
        {Array.from({ length: 25 }, (_, i) => (
          <text
            key={`h${i}`}
            x={hourToX(i)}
            y={GRID_TOP - 8}
            textAnchor="middle"
            className="eld-hour-label"
          >
            {i === 0 ? "M" : i === 12 ? "N" : i === 24 ? "M" : i > 12 ? i - 12 : i}
          </text>
        ))}

        {/* Status rows */}
        {STATUSES.map((s, rowIdx) => {
          const y = GRID_TOP + rowIdx * ROW_HEIGHT;
          return (
            <g key={s.key}>
              {/* Row label */}
              <text x={GRID_LEFT - 8} y={y + ROW_HEIGHT / 2 + 4} textAnchor="end" className="eld-status-label">
                {s.label}
              </text>

              {/* Row background */}
              <rect
                x={GRID_LEFT}
                y={y}
                width={GRID_WIDTH}
                height={ROW_HEIGHT}
                fill={rowIdx % 2 === 0 ? "#fafafa" : "#fff"}
                stroke="#e5e7eb"
                strokeWidth={0.5}
              />

              {/* Vertical hour lines */}
              {Array.from({ length: 25 }, (_, i) => (
                <line
                  key={`vl${i}`}
                  x1={hourToX(i)}
                  y1={y}
                  x2={hourToX(i)}
                  y2={y + ROW_HEIGHT}
                  stroke={i % 6 === 0 ? "#d1d5db" : "#f3f4f6"}
                  strokeWidth={i % 6 === 0 ? 1 : 0.5}
                />
              ))}

              {/* Duty bars for this status */}
              {log.entries
                .filter((e) => e.status === s.key)
                .map((entry, idx) => {
                  const x1 = hourToX(entry.start_hour);
                  const x2 = hourToX(entry.end_hour);
                  const barWidth = x2 - x1;
                  if (barWidth < 0.5) return null;
                  return (
                    <rect
                      key={idx}
                      x={x1}
                      y={y + 4}
                      width={barWidth}
                      height={ROW_HEIGHT - 8}
                      rx={3}
                      fill={STATUS_COLORS[s.key]}
                      opacity={0.85}
                    />
                  );
                })}

              {/* Hours total */}
              <text
                x={GRID_RIGHT + 8}
                y={y + ROW_HEIGHT / 2 + 4}
                className="eld-hours-total"
              >
                {log.total_hours[s.key].toFixed(1)}
              </text>
            </g>
          );
        })}

        {/* Transition lines (vertical connectors between status changes) */}
        {log.entries.map((entry, idx) => {
          if (idx === 0) return null;
          const prev = log.entries[idx - 1];
          const prevRow = STATUSES.findIndex((s) => s.key === prev.status);
          const currRow = STATUSES.findIndex((s) => s.key === entry.status);
          if (prevRow === currRow) return null;

          const x = hourToX(entry.start_hour);
          const y1 = GRID_TOP + Math.min(prevRow, currRow) * ROW_HEIGHT + ROW_HEIGHT / 2;
          const y2 = GRID_TOP + Math.max(prevRow, currRow) * ROW_HEIGHT + ROW_HEIGHT / 2;

          return (
            <line
              key={`t${idx}`}
              x1={x}
              y1={y1}
              x2={x}
              y2={y2}
              stroke="#374151"
              strokeWidth={1.5}
              strokeDasharray="3,2"
            />
          );
        })}
      </svg>

      {log.remarks.length > 0 && (
        <div className="eld-remarks">
          <span className="eld-remarks-label">Remarks:</span>{" "}
          {log.remarks.join(" \u2022 ")}
        </div>
      )}
    </div>
  );
}
