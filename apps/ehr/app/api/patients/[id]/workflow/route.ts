import { randomUUID } from "node:crypto";

import { NextResponse } from "next/server";

import { prisma } from "../../../../../lib/db";

type WorkflowPayload =
  | {
      type: "create_note";
      encounterId: string;
      author: string;
      title: string;
      content: string;
    }
  | {
      type: "create_order";
      encounterId: string;
      name: string;
      category: "LAB" | "MED" | "IMAGING";
      parameters: string;
      rationale: string;
      submitForSignature: boolean;
    }
  | {
      type: "sign_order";
      orderId: string;
    }
  | {
      type: "sign_encounter";
      encounterId: string;
    };

function isNonEmptyString(value: unknown): value is string {
  return typeof value === "string" && value.trim().length > 0;
}

function isOrderCategory(value: unknown): value is "LAB" | "MED" | "IMAGING" {
  return value === "LAB" || value === "MED" || value === "IMAGING";
}

function getTrimmedString(value: unknown): string | null {
  return isNonEmptyString(value) ? value.trim() : null;
}

export async function POST(request: Request, context: { params: Promise<{ id: string }> }) {
  const { id: patientId } = await context.params;
  const payload = (await request.json()) as Partial<WorkflowPayload>;

  if (!isNonEmptyString(patientId)) {
    return NextResponse.json({ error: "Missing patient id" }, { status: 400 });
  }

  if (payload.type === "create_note") {
    const encounterId = getTrimmedString(payload.encounterId);
    const author = getTrimmedString(payload.author);
    const title = getTrimmedString(payload.title);
    const content = getTrimmedString(payload.content);

    if (!encounterId || !author || !title || !content) {
      return NextResponse.json({ error: "Missing note fields" }, { status: 400 });
    }

    const note = await prisma.clinicalNote.create({
      data: {
        id: randomUUID(),
        encounterId,
        type: "PROGRESS",
        title,
        author,
        content,
        signed: false
      }
    });

    return NextResponse.json({
      note: {
        ...note,
        createdAt: note.createdAt.toISOString()
      }
    });
  }

  if (payload.type === "create_order") {
    const encounterId = getTrimmedString(payload.encounterId);
    const name = getTrimmedString(payload.name);
    const category = payload.category;
    const parameters = getTrimmedString(payload.parameters);
    const rationale = getTrimmedString(payload.rationale);

    if (!encounterId || !name || !parameters || !rationale || !isOrderCategory(category)) {
      return NextResponse.json({ error: "Missing order fields" }, { status: 400 });
    }

    const order = await prisma.order.create({
      data: {
        id: randomUUID(),
        encounterId,
        name,
        category,
        parametersJson: JSON.stringify({ freeText: parameters }),
        rationale,
        status: payload.submitForSignature ? "PENDING_SIGNATURE" : "DRAFT"
      }
    });

    return NextResponse.json({
      order: {
        id: order.id,
        name: order.name,
        category: order.category,
        parameters: { freeText: JSON.parse(order.parametersJson).freeText as string },
        status: order.status,
        rationale: order.rationale,
        createdAt: order.createdAt.toISOString()
      }
    });
  }

  if (payload.type === "sign_order") {
    if (!isNonEmptyString(payload.orderId)) {
      return NextResponse.json({ error: "Missing order id" }, { status: 400 });
    }

    const order = await prisma.order.update({
      where: { id: payload.orderId },
      data: { status: "SIGNED" }
    });

    return NextResponse.json({
      order: {
        id: order.id,
        name: order.name,
        category: order.category,
        parameters: { freeText: JSON.parse(order.parametersJson).freeText as string },
        status: order.status,
        rationale: order.rationale,
        createdAt: order.createdAt.toISOString()
      }
    });
  }

  if (payload.type === "sign_encounter") {
    if (!isNonEmptyString(payload.encounterId)) {
      return NextResponse.json({ error: "Missing encounter id" }, { status: 400 });
    }

    await prisma.$transaction([
      prisma.encounter.update({
        where: { id: payload.encounterId },
        data: { status: "SIGNED" }
      }),
      prisma.clinicalNote.updateMany({
        where: { encounterId: payload.encounterId },
        data: { signed: true }
      }),
      prisma.order.updateMany({
        where: {
          encounterId: payload.encounterId,
          status: {
            in: ["DRAFT", "PENDING_SIGNATURE"]
          }
        },
        data: { status: "SIGNED" }
      })
    ]);

    return NextResponse.json({ encounter: { id: payload.encounterId, status: "SIGNED" } });
  }

  return NextResponse.json({ error: "Unsupported workflow action" }, { status: 400 });
}