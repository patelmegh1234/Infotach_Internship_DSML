// Dimple, Upload Date: 2026-07-28
import { Clock3 } from "lucide-react";
import type { AnalysisHistoryItem, AnalysisResponse } from "../types";

type HistoryPanelProps = {
  history: AnalysisHistoryItem[];
  onSelect: (item: AnalysisResponse) => void;
};

export function HistoryPanel({ history, onSelect }: HistoryPanelProps) {
  return (
    <section className="panel history-panel">
      <div className="panel-heading">
        <div>
          <p className="eyebrow">Local Cases</p>
          <h2>Analysis History</h2>
        </div>
        <Clock3 size={22} />
      </div>

      <div className="history-list">
        {history.length === 0 && <div className="empty-state">No saved cases</div>}
        {history.map((item) => (
          <button className="history-item" key={item.id} type="button" onClick={() => onSelect(item)}>
            <span>{item.file_name}</span>
            <strong>{Math.round(item.confidence * 100)}%</strong>
            <small>{new Date(item.createdAt).toLocaleString()}</small>
          </button>
        ))}
      </div>
    </section>
  );
}

