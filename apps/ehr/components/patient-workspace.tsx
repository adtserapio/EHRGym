"use client";

import { type FormEvent, useMemo, useState } from "react";

import { ActivityNav } from "./activity-nav";
import { AppBrand } from "./app-brand";
import { ChartReviewTabs } from "./chart-review-tabs";
import { SectionCard } from "./section-card";
import { WorkspaceSidebar } from "./workspace-sidebar";
import { formatDateTime } from "../lib/chart";

type NoteItem = {
  id: string;
  type: string;
  title: string;
  author: string;
  content: string;
  signed: boolean;
  createdAt: string;
};

type OrderItem = {
  id: string;
  name: string;
  category: string;
  parameters: Record<string, string>;
  status: string;
  rationale: string;
  createdAt: string;
};

type EncounterItem = {
  id: string;
  type: string;
  reasonForVisit: string;
  provider: string;
  startedAt: string;
  status: string;
  labs: Array<{
    id: string;
    name: string;
    loinc: string | null;
    value: string;
    unit: string;
    referenceRange: string;
    abnormal: boolean;
    collectedAt: string;
  }>;
  notes: NoteItem[];
  orders: OrderItem[];
};

type ScenarioItem = {
  id: string;
  encounterId: string;
  title: string;
  objective: string;
  rubric: string[];
  requiredOrders: string[];
  requiredNoteElements: string[];
};

export type PatientWorkspaceData = {
  id: string;
  mrn: string;
  fullName: string;
  age: number;
  sex: string;
  allergies: string[];
  bannerFlags: string[];
  summary: string;
  encounters: EncounterItem[];
  scenarios: ScenarioItem[];
};

type WorkflowResponse =
  | { note: NoteItem }
  | { order: OrderItem }
  | { encounter: { id: string; status: string } }
  | { ok: true };

type PatientWorkspaceProps = {
  initialPatient: PatientWorkspaceData;
};

export function PatientWorkspace({ initialPatient }: PatientWorkspaceProps) {
  const [patient, setPatient] = useState(initialPatient);
  const [notePending, setNotePending] = useState(false);
  const [orderPending, setOrderPending] = useState(false);
  const [signingOrderId, setSigningOrderId] = useState<string | null>(null);
  const [signingEncounter, setSigningEncounter] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const activeEncounter = patient.encounters[0];
  const scenario =
    patient.scenarios.find((candidate) => candidate.encounterId === activeEncounter?.id) ?? patient.scenarios[0];

  const requiredOrders = scenario?.requiredOrders ?? [];
  const requiredNoteElements = scenario?.requiredNoteElements ?? [];
  const rubric = scenario?.rubric ?? [];
  const problemList = useMemo(() => Array.from(new Set([activeEncounter?.reasonForVisit, ...patient.bannerFlags].filter(Boolean))), [
    activeEncounter?.reasonForVisit,
    patient.bannerFlags
  ]);
  const visitDiagnoses = useMemo(
    () => Array.from(new Set([scenario?.title ?? activeEncounter?.reasonForVisit, activeEncounter?.type, patient.summary].filter(Boolean))),
    [activeEncounter?.reasonForVisit, activeEncounter?.type, patient.summary, scenario?.title]
  );

  const globalNavItems = [
    { label: "Chart Review", href: "#chart-review" },
    { label: "Synopsis", href: "#summary" },
    { label: "Orders", href: "#orders" },
    { label: "Notes", href: "#notes" },
    { label: "Plan", href: "#summary" },
    { label: "Wrap-Up", href: "#encounter" }
  ];
  const activityNavItems = [
    { label: "Summary", href: "#summary", testId: "activity-summary" },
    { label: "Chart Review", href: "#chart-review", testId: "activity-chart-review" },
    { label: "Notes", href: "#notes", testId: "activity-notes" },
    { label: "Orders", href: "#orders", testId: "activity-orders" },
    { label: "Wrap-Up", href: "#encounter", testId: "activity-encounter" }
  ];
  const sidebarNavItems = [
    { label: "Summary", href: "#summary" },
    { label: "Labs & encounters", href: "#chart-review" },
    { label: "Documentation", href: "#notes" },
    { label: "Order Entry", href: "#orders" },
    { label: "Sign / close", href: "#encounter" }
  ];

  const noteText = activeEncounter?.notes.map((note) => note.content).join("\n") ?? "";
  const ordersComplete = requiredOrders.length === 0 || requiredOrders.every((ro) => activeEncounter?.orders.some((o) => o.name === ro && o.status === "SIGNED"));
  const notesComplete = requiredNoteElements.length === 0 || requiredNoteElements.every((el) => noteText.toLowerCase().includes(el.toLowerCase()));
  const encounterSigned = activeEncounter?.status === "SIGNED";
  const hasLabs = (activeEncounter?.labs.length ?? 0) > 0;

  // Map each rubric item to a completion check based on its keywords
  const completedRubric = new Set<string>();
  for (const item of rubric) {
    const lower = item.toLowerCase();
    if (lower.includes("sign") && lower.includes("encounter")) {
      if (encounterSigned) completedRubric.add(item);
    } else if (lower.includes("order") || lower.includes("place")) {
      if (ordersComplete) completedRubric.add(item);
    } else if (lower.includes("document") || lower.includes("note") || lower.includes("write")) {
      if (notesComplete) completedRubric.add(item);
    } else if (lower.includes("review") || lower.includes("identify") || lower.includes("assess")) {
      if (hasLabs) completedRubric.add(item);
    }
  }

  if (!activeEncounter) {
    return null;
  }

  async function postWorkflow(payload: Record<string, unknown>) {
    const response = await fetch(`/api/patients/${patient.id}/workflow`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify(payload)
    });

    if (!response.ok) {
      const body = (await response.json().catch(() => null)) as { error?: string } | null;
      throw new Error(body?.error ?? "Request failed");
    }

    return (await response.json()) as WorkflowResponse;
  }

  function updateEncounter(update: (encounter: EncounterItem) => EncounterItem) {
    setPatient((current) => ({
      ...current,
      encounters: current.encounters.map((encounter) => (encounter.id === activeEncounter.id ? update(encounter) : encounter))
    }));
  }

  async function handleCreateNote(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setErrorMessage(null);
    setNotePending(true);

    const form = event.currentTarget;
    const formData = new FormData(form);

    try {
      const result = await postWorkflow({
        type: "create_note",
        encounterId: activeEncounter.id,
        author: formData.get("author"),
        title: formData.get("title"),
        content: formData.get("content")
      });

      if ("note" in result) {
        updateEncounter((encounter) => ({
          ...encounter,
          notes: [result.note, ...encounter.notes]
        }));
      }
      form.reset();
    } catch (error) {
      setErrorMessage(error instanceof Error ? error.message : "Failed to save note");
    } finally {
      setNotePending(false);
    }
  }

  async function handleCreateOrder(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setErrorMessage(null);
    setOrderPending(true);

    const form = event.currentTarget;
    const formData = new FormData(form);

    try {
      const result = await postWorkflow({
        type: "create_order",
        encounterId: activeEncounter.id,
        name: formData.get("name"),
        category: formData.get("category"),
        parameters: formData.get("parameters"),
        rationale: formData.get("rationale"),
        submitForSignature: formData.get("submitForSignature") === "on"
      });

      if ("order" in result) {
        updateEncounter((encounter) => ({
          ...encounter,
          orders: [result.order, ...encounter.orders]
        }));
      }
      form.reset();
    } catch (error) {
      setErrorMessage(error instanceof Error ? error.message : "Failed to save order");
    } finally {
      setOrderPending(false);
    }
  }

  async function handleSignOrder(orderId: string) {
    setErrorMessage(null);
    setSigningOrderId(orderId);

    try {
      const result = await postWorkflow({
        type: "sign_order",
        orderId
      });

      if ("order" in result) {
        updateEncounter((encounter) => ({
          ...encounter,
          orders: encounter.orders.map((order) => (order.id === orderId ? result.order : order))
        }));
      }
    } catch (error) {
      setErrorMessage(error instanceof Error ? error.message : "Failed to sign order");
    } finally {
      setSigningOrderId(null);
    }
  }

  async function handleSignEncounter() {
    setErrorMessage(null);
    setSigningEncounter(true);

    try {
      await postWorkflow({
        type: "sign_encounter",
        encounterId: activeEncounter.id
      });

      updateEncounter((encounter) => ({
        ...encounter,
        status: "SIGNED",
        notes: encounter.notes.map((note) => ({ ...note, signed: true })),
        orders: encounter.orders.map((order) => ({ ...order, status: "SIGNED" }))
      }));
    } catch (error) {
      setErrorMessage(error instanceof Error ? error.message : "Failed to sign encounter");
    } finally {
      setSigningEncounter(false);
    }
  }

  return (
    <main className="dashboard-shell">
      <WorkspaceSidebar
        brand={<AppBrand title="EHRGym" subtitle="Chart workspace" href="/" />}
        sections={[
          {
            title: "Navigation",
            items: [
              { label: "Dashboard", icon: "dashboard", href: "/" },
              { label: "Chart", icon: "chart", href: "#summary" }
            ]
          },
          {
            title: "Sections",
            items: [
              { label: "Summary", icon: "summary", href: "#summary" },
              { label: "Review", icon: "review", href: "#chart-review" },
              { label: "Orders", icon: "orders", href: "#orders" },
              { label: "Notes", icon: "notes", href: "#notes" }
            ]
          }
        ]}
        footerTitle="Active Visit"
        footerText={`${activeEncounter.reasonForVisit} · Patrick Sullivan, MD`}
        footerAction="Return to Worklist"
        footerHref="/"
      />

      <div className="dashboard-main">
        <header className="workspace-header workspace-header--chart">
          <div className="workspace-header__breadcrumbs">
            <a href="/" className="workspace-backlink">
              ← All patients
            </a>
            <ActivityNav items={globalNavItems} className="workspace-pills" ariaLabel="Chart navigation" defaultHref="#chart-review" />
          </div>
          <div className="workspace-header__actions">
            <div className="workspace-profile workspace-profile--compact">
              <div className="workspace-profile__avatar">PS</div>
              <div>
                <strong>Patrick Sullivan, MD</strong>
                <p>Attending Physician</p>
              </div>
            </div>
          </div>
        </header>

        <section className="patient-hero" data-testid="patient-banner">
          <div className="patient-hero__identity">
            <div>
              <p className="patient-hero__eyebrow">Active Chart · MRN {patient.mrn}</p>
              <h1 className="patient-hero__title">{patient.fullName}</h1>
              <p className="patient-hero__lede">
                {patient.age} y/o {patient.sex} · {activeEncounter.reasonForVisit}
              </p>
            </div>
          </div>
          <div className="patient-hero__meta">
            <div className="patient-hero__panel" data-testid="allergies-card">
              <strong>Allergies</strong>
              <span>{patient.allergies.join(", ")}</span>
            </div>
            <div className="patient-hero__panel" data-testid="flags-card">
              <strong>Chart flags</strong>
              <span>{patient.bannerFlags.join(" · ")}</span>
            </div>
            <div className="patient-hero__panel" data-testid="encounter-card">
              <strong>Visit focus</strong>
              <span>{scenario?.title ?? activeEncounter.type}</span>
            </div>
            <div className="patient-hero__panel">
              <strong>Admitting</strong>
              <span>{activeEncounter.provider}</span>
            </div>
            <div className="patient-hero__panel patient-hero__panel--status">
              <strong>Visit Status</strong>
              <span className="status-pill" data-status={activeEncounter.status}>
                {activeEncounter.status === "SIGNED" ? "Signed" : activeEncounter.status === "OPEN" ? "In Progress" : activeEncounter.status}
              </span>
            </div>
          </div>
        </section>

        <ActivityNav items={activityNavItems} className="chart-activity-bar workspace-pills workspace-pills--wide" ariaLabel="Activity navigation" defaultHref="#summary" />

        <div id="summary" />

        <div className="content-grid content-grid--chart">
          <div className="content-stack">
            <SectionCard title="Chart Review" subtitle="Encounter timeline and laboratory review" testId="chart-review-panel" className="section-card--chart">
              <div id="chart-review">
                <ChartReviewTabs encounters={patient.encounters} labs={activeEncounter.labs} notes={activeEncounter.notes} />
              </div>
            </SectionCard>

            <SectionCard title="Notes" subtitle="Progress and clinical documentation" testId="notes-panel" className="section-card--notes">
              <div id="notes" className="grid grid--2">
                <form onSubmit={handleCreateNote} className="list-row" data-testid="note-form">
                  <div className="form-grid">
                    <label className="field">
                      <span className="muted">Author</span>
                      <input aria-label="Note author" name="author" defaultValue="Attending Physician" required />
                    </label>
                    <label className="field">
                      <span className="muted">Title</span>
                      <input aria-label="Note title" name="title" defaultValue="Progress Note" required />
                    </label>
                    <label className="field">
                      <span className="muted">Progress note</span>
                      <textarea
                        aria-label="Progress note content"
                        name="content"
                        defaultValue={`S:\nO:\nA:\nP:`}
                        required
                      />
                    </label>
                    <div className="form-actions">
                      <button className="primary-button" type="submit" data-testid="save-note-button" disabled={notePending}>
                        {notePending ? "Saving note..." : "File progress note"}
                      </button>
                    </div>
                  </div>
                </form>

                <div className="note-list">
                  {activeEncounter.notes.map((note) => (
                    <article key={note.id} className="note-row" data-testid={`note-row-${note.id}`}>
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
                </div>
              </div>
            </SectionCard>

            <SectionCard title="Orders" subtitle="Medication, lab, and imaging entry" testId="orders-panel" className="section-card--orders">
              <div id="orders" className="grid grid--2">
                <form onSubmit={handleCreateOrder} className="list-row" data-testid="order-form">
                  <div className="form-grid">
                    <label className="field">
                      <span className="muted">Order name</span>
                      <input aria-label="Order name" name="name" placeholder="Normal saline bolus" required />
                    </label>
                    <label className="field">
                      <span className="muted">Category</span>
                      <select aria-label="Order category" name="category" defaultValue="LAB">
                        <option value="LAB">Lab</option>
                        <option value="MED">Medication</option>
                        <option value="IMAGING">Imaging</option>
                      </select>
                    </label>
                    <label className="field">
                      <span className="muted">Parameters</span>
                      <input aria-label="Order parameters" name="parameters" placeholder="1 L IV once" required />
                    </label>
                    <label className="field">
                      <span className="muted">Rationale</span>
                      <textarea aria-label="Order rationale" name="rationale" placeholder="Why is this order needed?" required />
                    </label>
                    <label className="checkbox-field">
                      <input className="checkbox-field__control" aria-label="Sign order immediately" name="submitForSignature" type="checkbox" defaultChecked />
                      <span>Sign immediately</span>
                    </label>
                    <div className="form-actions">
                      <button className="primary-button" type="submit" data-testid="save-order-button" disabled={orderPending}>
                        {orderPending ? "Placing order..." : "Place order"}
                      </button>
                    </div>
                  </div>
                </form>

                <div className="order-list">
                  {activeEncounter.orders.map((order) => (
                    <article key={order.id} className="order-row" data-testid={`order-row-${order.id}`}>
                      <header>
                        <div>
                          <h3>{order.name}</h3>
                          <p className="muted">
                            {order.category} · {formatDateTime(new Date(order.createdAt))}
                          </p>
                        </div>
                        <span className="status-pill" data-status={order.status}>
                          {order.status}
                        </span>
                      </header>
                      <p>
                        <strong>Parameters:</strong> {Object.values(order.parameters).join(", ")}
                      </p>
                      <p>
                        <strong>Rationale:</strong> {order.rationale}
                      </p>
                      {order.status !== "SIGNED" ? (
                        <div className="form-actions">
                          <button
                            className="secondary-button"
                            type="button"
                            data-testid={`sign-order-${order.id}`}
                            disabled={signingOrderId === order.id}
                            onClick={() => handleSignOrder(order.id)}
                          >
                            {signingOrderId === order.id ? "Signing..." : "Sign order"}
                          </button>
                        </div>
                      ) : null}
                    </article>
                  ))}
                </div>
              </div>
            </SectionCard>

            <SectionCard title="Wrap-Up" subtitle="Finalize documentation and orders" testId="encounter-panel" className="section-card--wrapup">
              <div id="encounter" className="list-row list-row--split">
                <p>Signing this visit finalizes notes and promotes all remaining draft or pending orders to signed.</p>
                <div className="form-actions">
                  <button className="primary-button" type="button" data-testid="sign-encounter-button" disabled={signingEncounter} onClick={handleSignEncounter}>
                    {signingEncounter ? "Signing visit..." : "Sign visit"}
                  </button>
                </div>
              </div>
            </SectionCard>
          </div>

          <aside className="content-stack">
            <SectionCard title="Review Status" subtitle="Visit workflow" className="section-card--summary">
              <div className="rail-list">
                {rubric.map((item) => {
                  const completed = completedRubric.has(item);
                  return (
                    <div key={item} className="rail-list__item">
                      <strong>{item}</strong>
                      <span>{completed ? "Completed" : "Pending review"}</span>
                    </div>
                  );
                })}
              </div>
            </SectionCard>

            <SectionCard title="Chart Navigation" subtitle="Common activities" className="section-card--summary">
              <ActivityNav items={sidebarNavItems} className="sidebar-nav" ariaLabel="Chart sections" defaultHref="#summary" />
            </SectionCard>

            <SectionCard title="Problem List" subtitle="Active charted issues" className="section-card--problem-list">
              <div className="problem-list">
                {problemList.map((problem) => (
                  <div key={problem} className="problem-list__item">
                    <span>{problem}</span>
                    <span className="problem-list__status">Active</span>
                  </div>
                ))}
              </div>
            </SectionCard>

            <SectionCard title="Visit Diagnoses" subtitle="Current encounter associations" className="section-card--diagnosis-list">
              <div className="problem-list">
                {visitDiagnoses.map((diagnosis) => (
                  <div key={diagnosis} className="problem-list__item">
                    <span>{diagnosis}</span>
                    <span className="problem-list__status problem-list__status--muted">Visit</span>
                  </div>
                ))}
              </div>
            </SectionCard>

            {errorMessage ? (
              <SectionCard title="Workflow Error" subtitle="Most recent action" className="section-card--summary">
                <p>{errorMessage}</p>
              </SectionCard>
            ) : null}
          </aside>
        </div>
      </div>
    </main>
  );
}