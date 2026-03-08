import { notFound } from "next/navigation";

import { PatientWorkspace, type PatientWorkspaceData } from "../../../components/patient-workspace";
import { parseJsonValue } from "../../../lib/chart";
import { prisma } from "../../../lib/db";

type PatientPageData = {
  id: string;
  mrn: string;
  fullName: string;
  age: number;
  sex: string;
  allergiesJson: string;
  bannerFlagsJson: string;
  summary: string;
  encounters: Array<{
    id: string;
    type: string;
    reasonForVisit: string;
    provider: string;
    startedAt: Date;
    status: string;
    labs: Array<{
      id: string;
      name: string;
      loinc: string | null;
      value: string;
      unit: string;
      referenceRange: string;
      abnormal: boolean;
      collectedAt: Date;
    }>;
    notes: Array<{
      id: string;
      type: string;
      title: string;
      author: string;
      content: string;
      signed: boolean;
      createdAt: Date;
    }>;
    orders: Array<{
      id: string;
      name: string;
      category: string;
      parametersJson: string;
      status: string;
      rationale: string;
      createdAt: Date;
    }>;
  }>;
  scenarios: Array<{
    id: string;
    encounterId: string;
    title: string;
    objective: string;
    rubricJson: string;
    requiredOrdersJson: string;
    requiredNoteElementsJson: string;
  }>;
};

type PatientPageProps = {
  params: Promise<{
    id: string;
  }>;
};

export default async function PatientPage({ params }: PatientPageProps) {
  const { id } = await params;

  const patient: PatientPageData | null = await prisma.patient.findUnique({
    where: { id },
    include: {
      encounters: {
        orderBy: { startedAt: "desc" },
        include: {
          labs: {
            orderBy: { collectedAt: "desc" }
          },
          notes: {
            orderBy: { createdAt: "desc" }
          },
          orders: {
            orderBy: { createdAt: "desc" }
          }
        }
      },
      scenarios: {
        orderBy: { createdAt: "desc" }
      }
    }
  });

  if (!patient) {
    notFound();
  }

  const activeEncounter = patient.encounters[0];
  const scenario =
    patient.scenarios.find((candidate: PatientPageData["scenarios"][number]) => candidate.encounterId === activeEncounter?.id) ??
    patient.scenarios[0];

  if (!activeEncounter) {
    notFound();
  }

  const initialPatient: PatientWorkspaceData = {
    id: patient.id,
    mrn: patient.mrn,
    fullName: patient.fullName,
    age: patient.age,
    sex: patient.sex,
    allergies: parseJsonValue<string[]>(patient.allergiesJson),
    bannerFlags: parseJsonValue<string[]>(patient.bannerFlagsJson),
    summary: patient.summary,
    encounters: patient.encounters.map((encounter) => ({
      id: encounter.id,
      type: encounter.type,
      reasonForVisit: encounter.reasonForVisit,
      provider: encounter.provider,
      startedAt: encounter.startedAt.toISOString(),
      status: encounter.status,
      labs: encounter.labs.map((lab) => ({
        ...lab,
        collectedAt: lab.collectedAt.toISOString()
      })),
      notes: encounter.notes.map((note) => ({
        ...note,
        createdAt: note.createdAt.toISOString()
      })),
      orders: encounter.orders.map((order) => ({
        id: order.id,
        name: order.name,
        category: order.category,
        parameters: parseJsonValue<Record<string, string>>(order.parametersJson),
        status: order.status,
        rationale: order.rationale,
        createdAt: order.createdAt.toISOString()
      }))
    })),
    scenarios: patient.scenarios.map((item) => ({
      id: item.id,
      encounterId: item.encounterId,
      title: item.title,
      objective: item.objective,
      rubric: parseJsonValue<string[]>(item.rubricJson),
      requiredOrders: parseJsonValue<string[]>(item.requiredOrdersJson),
      requiredNoteElements: parseJsonValue<string[]>(item.requiredNoteElementsJson)
    }))
  };

  return <PatientWorkspace initialPatient={initialPatient} />;
}
