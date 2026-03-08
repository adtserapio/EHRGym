"use client";

import { useMemo, useState } from "react";

import { formatDateTime } from "../lib/chart";

type EncounterItem = {
  id: string;
  type: string;
  reasonForVisit: string;
  provider: string;
  startedAt: Date | string;
  status: string;
};

type LabItem = {
  id: string;
  name: string;
  loinc: string | null;
  value: string;
  unit: string;
  referenceRange: string;
  abnormal: boolean;
  collectedAt: Date | string;
};

type NoteItem = {
  id: string;
  type: string;
  title: string;
  author: string;
  content: string;
  signed: boolean;
  createdAt: Date | string;
};

type ChartReviewTabsProps = {
  encounters: EncounterItem[];
  labs: LabItem[];
  notes: NoteItem[];
};

type TabKey = "encounters" | "labs" | "notes";

export function ChartReviewTabs({ encounters, labs, notes }: ChartReviewTabsProps) {
  const [activeTab, setActiveTab] = useState<TabKey>("encounters");

  const tabs = useMemo(
    () => [
      { key: "encounters" as const, label: "Encounters" },
      { key: "labs" as const, label: "Labs" },
      { key: "notes" as const, label: "Clinical Notes" }
    ],
    []
  );

  return (
    <div className="section-stack">
      <div className="subtab-strip" aria-label="Chart review tabs" role="tablist">
        {tabs.map((tab) => (
          <button
            key={tab.key}
            type="button"
            role="tab"
            aria-selected={activeTab === tab.key}
            aria-controls={`chart-tab-panel-${tab.key}`}
            id={`chart-tab-${tab.key}`}
            className={activeTab === tab.key ? "subtab-strip__item subtab-strip__item--active" : "subtab-strip__item"}
            data-testid={`chart-tab-${tab.key}`}
            onClick={() => setActiveTab(tab.key)}
          >
            {tab.label}
          </button>
        ))}
      </div>

      <section
        id="chart-tab-panel-encounters"
        role="tabpanel"
        aria-labelledby="chart-tab-encounters"
        hidden={activeTab !== "encounters"}
        className="list-row"
        data-testid="encounter-timeline"
      >
        <header>
          <div>
            <h3>Encounter timeline</h3>
            <p className="muted">Linked visit history and responsible clinicians.</p>
          </div>
        </header>
        <div className="timeline">
          {encounters.map((encounter) => (
            <div key={encounter.id} className="list-row">
              <header>
                <div>
                  <strong>{encounter.type}</strong>
                  <p className="muted">
                    {encounter.reasonForVisit} · {encounter.provider}
                  </p>
                </div>
                <span className="status-pill" data-status={encounter.status}>
                  {encounter.status}
                </span>
              </header>
              <p className="muted">Started {formatDateTime(new Date(encounter.startedAt))}</p>
            </div>
          ))}
        </div>
      </section>

      <section
        id="chart-tab-panel-labs"
        role="tabpanel"
        aria-labelledby="chart-tab-labs"
        hidden={activeTab !== "labs"}
        className="list-row"
        data-testid="labs-table-wrapper"
      >
        <header>
          <div>
            <h3>Labs</h3>
            <p className="muted">Recent resulted values for the active encounter.</p>
          </div>
        </header>
        <table className="table" aria-label="Recent labs" data-testid="labs-table">
          <thead>
            <tr>
              <th>Collected</th>
              <th>Test</th>
              <th>Value</th>
              <th>Reference</th>
            </tr>
          </thead>
          <tbody>
            {labs.map((lab) => (
              <tr key={lab.id} className="lab-row" data-testid={`lab-row-${lab.id}`}>
                <td>{formatDateTime(new Date(lab.collectedAt))}</td>
                <td>{lab.name}</td>
                <td className={lab.abnormal ? "abnormal" : undefined}>
                  {lab.value} {lab.unit}
                </td>
                <td>{lab.referenceRange}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </section>

      <section
        id="chart-tab-panel-notes"
        role="tabpanel"
        aria-labelledby="chart-tab-notes"
        hidden={activeTab !== "notes"}
        className="note-list"
        data-testid="chart-review-notes"
      >
        {notes.map((note) => (
          <article key={note.id} className="note-row" data-testid={`chart-note-row-${note.id}`}>
            <header>
              <div>
                <h3>{note.title}</h3>
                <p className="muted">
                  {note.type} · {note.author} · {formatDateTime(new Date(note.createdAt))}
                </p>
              </div>
              <span className="status-pill" data-status={note.signed ? "SIGNED" : "OPEN"}>
                {note.signed ? "SIGNED" : "DRAFT"}
              </span>
            </header>
            <p style={{ whiteSpace: "pre-wrap" }}>{note.content}</p>
          </article>
        ))}
      </section>
    </div>
  );
}
