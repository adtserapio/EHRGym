import Link from "next/link";

import { AppBrand } from "../components/app-brand";
import { SectionCard } from "../components/section-card";
import { WorkspaceSidebar } from "../components/workspace-sidebar";
import { formatDateTime, parseJsonValue } from "../lib/chart";
import { prisma } from "../lib/db";

type HomePatient = {
  id: string;
  mrn: string;
  fullName: string;
  age: number;
  sex: string;
  summary: string;
  bannerFlagsJson: string;
  encounters: Array<{
    status: string;
    reasonForVisit: string;
    startedAt: Date;
  }>;
  scenarios: Array<{
    title: string;
    objective: string;
  }>;
};

function cleanObjective(objective: string): string {
  const stripped = objective.replace(/^As the attending physician,\s*/i, "");
  return stripped.charAt(0).toUpperCase() + stripped.slice(1);
}

export default async function HomePage() {
  const patients: HomePatient[] = await prisma.patient.findMany({
    orderBy: { fullName: "asc" },
    include: {
      encounters: {
        take: 1,
        orderBy: { startedAt: "desc" }
      },
      scenarios: {
        take: 1,
        orderBy: { createdAt: "desc" }
      }
    }
  });

  const leadPatient = patients[0];
  const leadEncounter = leadPatient?.encounters[0];
  const leadFlags = leadPatient ? parseJsonValue<string[]>(leadPatient.bannerFlagsJson) : [];
  const openCount = patients.filter((patient) => patient.encounters[0]?.status === "OPEN").length;
  const signedCount = patients.length - openCount;

  return (
    <main className="dashboard-shell">
      <WorkspaceSidebar
        brand={<AppBrand title="EHRGym" subtitle="Clinical workspace" href="/" />}
        sections={[
          {
            title: "Navigation",
            items: [
              { label: "Dashboard", icon: "dashboard", href: "/" },
              { label: "Patient list", icon: "patients", href: "#patient-list-section" },
              { label: "Recent Activity", icon: "activity", href: "#recent-activity" },
              { label: "Snapshot", icon: "snapshot", href: "#selected-chart" }
            ]
          }
        ]}
        footerTitle="Operational View"
        footerText="Prepared for rounding, documentation, and order entry from a single dashboard."
      />

      <div className="dashboard-main">
        <header className="workspace-header workspace-header--home" data-testid="patient-list-hero">
          <span className="workspace-toggle workspace-toggle--static">
            <span className="workspace-toggle__icon" aria-hidden="true">
              <svg viewBox="0 0 20 20" fill="none" stroke="currentColor" strokeWidth="1.7" strokeLinecap="round" strokeLinejoin="round">
                <path d="M10 17s4.5-4.7 4.5-8A4.5 4.5 0 1 0 5.5 9c0 3.3 4.5 8 4.5 8Z" />
                <circle cx="10" cy="9" r="1.6" />
              </svg>
            </span>
            <span>5 West Med-Surg</span>
          </span>
          <div className="workspace-profile workspace-profile--panel">
            <div className="workspace-profile__avatar">PS</div>
            <div>
              <strong>Patrick Sullivan, MD</strong>
              <p>Attending Physician</p>
            </div>
          </div>
        </header>

        <section className="metric-grid">
          <SectionCard title="My Patients" subtitle="Current census" className="metric-card">
            <div className="metric-card__value">{patients.length}</div>
            <p>{openCount} charts in progress · {signedCount} signed</p>
          </SectionCard>
          <SectionCard title="Charts to Complete" subtitle="Awaiting documentation" className="metric-card">
            <div className="metric-card__value">{openCount}</div>
            <p>{openCount === 0 ? "All charts signed" : `${openCount} visit${openCount !== 1 ? "s" : ""} need notes, orders, or sign-off`}</p>
          </SectionCard>
          <SectionCard title="Next Review" subtitle="Current focus" className="metric-card metric-card--wide">
            <div className="metric-card__stack">
              <strong>{leadPatient?.fullName ?? "No patient selected"}</strong>
              <p>{leadEncounter?.reasonForVisit ?? "No active encounter"}</p>
              <span className="summary-flag summary-flag--accent">{leadEncounter ? formatDateTime(leadEncounter.startedAt) : "Pending"}</span>
            </div>
          </SectionCard>
        </section>

        <div className="content-grid content-grid--home">
          <div className="content-stack">
            <SectionCard title="Handoff Notes" subtitle="Overnight updates from covering team">
              <div id="recent-activity" />
              <div className="note-list">
                <article className="note-row">
                  <header>
                    <div>
                      <h3>Night Float Signout</h3>
                      <p className="muted">Cross-cover · Dr. R. Kimura</p>
                    </div>
                    <span className="muted">06:45 AM</span>
                  </header>
                  <p>Quiet overnight. No acute events. See patient list for pending labs and AM vitals. Two patients with new abnormal results flagged for your review.</p>
                </article>
              </div>
            </SectionCard>

            <SectionCard title="Patient List" subtitle="Select a patient to enter the chart" testId="patient-list">
              <div id="patient-list-section" />
              <div className="ehr-table__header">
                <span>Name</span>
                <span>MRN</span>
                <span>Visit</span>
                <span>Status</span>
                <span>Last update</span>
              </div>
              <div className="patient-list patient-list--table">
                {patients.map((patient: HomePatient) => {
                  const encounter = patient.encounters[0];
                  const scenario = patient.scenarios[0];
                  const flags = parseJsonValue<string[]>(patient.bannerFlagsJson);

                  return (
                    <Link
                      key={patient.id}
                      className="patient-card patient-card--table"
                      href={`/patient/${patient.id}`}
                      data-testid={`patient-card-${patient.id}`}
                    >
                      <div>
                        <strong>{patient.fullName}</strong>
                        <p className="muted">
                          {patient.age} y/o {patient.sex}
                        </p>
                      </div>
                      <div>
                        <strong>{patient.mrn}</strong>
                        <p className="muted">General medicine</p>
                      </div>
                      <div>
                        <strong>{encounter?.reasonForVisit ?? "No encounter"}</strong>
                        <p className="muted">{patient.summary}</p>
                      </div>
                      <div>
                        <span className="status-pill" data-status={encounter?.status ?? "OPEN"}>
                          {encounter?.status ?? "OPEN"}
                        </span>
                      </div>
                      <div>
                        <strong>{encounter ? formatDateTime(encounter.startedAt) : "Pending"}</strong>
                        <p className="muted">{scenario ? cleanObjective(scenario.objective) : flags.join(" · ")}</p>
                      </div>
                    </Link>
                  );
                })}
              </div>
            </SectionCard>
          </div>

          <aside className="content-stack">
            <SectionCard title="Selected Chart Snapshot" subtitle={leadPatient?.fullName ?? "No patient selected"} className="section-card--summary">
              <div id="selected-chart" />
              {leadPatient && leadEncounter ? (
                <div className="summary-panel">
                  <div className="summary-panel__row">
                    <strong>MRN</strong>
                    <span>{leadPatient.mrn}</span>
                  </div>
                  <div className="summary-panel__row">
                    <strong>Visit</strong>
                    <span>{leadEncounter.reasonForVisit}</span>
                  </div>
                  <div className="summary-panel__row">
                    <strong>Provider</strong>
                    <span>Open chart to continue workflow</span>
                  </div>
                  <div className="summary-flags">
                    {leadFlags.map((flag) => (
                      <span key={flag} className="summary-flag">
                        {flag}
                      </span>
                    ))}
                  </div>
                </div>
              ) : null}
            </SectionCard>

            <SectionCard title="Today’s Tasks" subtitle="Priority items for chart completion" className="section-card--summary">
              <div id="today-tasks" />
              <div className="task-list">
                {patients
                  .filter((p) => p.encounters[0]?.status === "OPEN" && p.scenarios[0])
                  .slice(0, 5)
                  .map((p) => {
                    const scenario = p.scenarios[0];
                    return (
                      <Link key={p.id} href={`/patient/${p.id}`} className="task-list__item">
                        <span className="task-list__check" />
                        <div>
                          <strong>{p.fullName}</strong>
                          <p className="muted">{scenario.title}</p>
                        </div>
                      </Link>
                    );
                  })}
              </div>
            </SectionCard>
          </aside>
        </div>
      </div>
    </main>
  );
}
