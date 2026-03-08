export type SeedLab = {
  id: string;
  name: string;
  loinc?: string;
  value: string;
  unit: string;
  referenceRange: string;
  abnormal: boolean;
  collectedAt: string;
};

export type SeedNote = {
  id: string;
  type: "PROGRESS" | "CONSULT" | "DISCHARGE";
  title: string;
  author: string;
  content: string;
  signed: boolean;
  createdAt: string;
};

export type SeedOrder = {
  id: string;
  name: string;
  category: "LAB" | "MED" | "IMAGING";
  parameters: Record<string, string>;
  status: "DRAFT" | "PENDING_SIGNATURE" | "SIGNED";
  rationale: string;
  createdAt: string;
};

export type SeedEncounter = {
  id: string;
  type: string;
  reasonForVisit: string;
  provider: string;
  startedAt: string;
  status: "OPEN" | "SIGNED" | "CLOSED";
  labs: SeedLab[];
  notes: SeedNote[];
  orders: SeedOrder[];
};

export type SeedScenario = {
  id: string;
  title: string;
  objective: string;
  rubric: string[];
  requiredOrders: string[];
  requiredNoteElements: string[];
};

export type SeedPatient = {
  id: string;
  mrn: string;
  fullName: string;
  age: number;
  sex: string;
  allergies: string[];
  bannerFlags: string[];
  summary: string;
  encounters: SeedEncounter[];
  scenarios: SeedScenario[];
};

// ---------------------------------------------------------------------------
// 25 synthetic patients with clinically accurate presentations
// ---------------------------------------------------------------------------

export const seedPatients: SeedPatient[] = [

  // ── 1. AKI Chart Review ─────────────────────────────────────────────────
  {
    id: "pat-1001",
    mrn: "SYN-1001",
    fullName: "Mary Johnson",
    age: 68,
    sex: "F",
    allergies: ["Penicillin"],
    bannerFlags: ["Fall risk", "CKD stage 3"],
    summary: "Admitted with weakness and oliguria after several days of poor oral intake.",
    encounters: [
      {
        id: "enc-1001",
        type: "Inpatient",
        reasonForVisit: "Acute kidney injury evaluation",
        provider: "Dr. Ada Carter",
        startedAt: "2026-03-05T14:15:00.000Z",
        status: "OPEN",
        labs: [
          { id: "lab-1001", name: "Creatinine", loinc: "2160-0", value: "2.3", unit: "mg/dL", referenceRange: "0.6-1.2", abnormal: true, collectedAt: "2026-03-06T08:12:00.000Z" },
          { id: "lab-1002", name: "Creatinine", loinc: "2160-0", value: "1.8", unit: "mg/dL", referenceRange: "0.6-1.2", abnormal: true, collectedAt: "2026-03-05T09:02:00.000Z" },
          { id: "lab-1003", name: "Hemoglobin", loinc: "718-7", value: "10.4", unit: "g/dL", referenceRange: "12.0-16.0", abnormal: true, collectedAt: "2026-03-06T08:12:00.000Z" }
        ],
        notes: [
          { id: "note-1001", type: "CONSULT", title: "Nephrology consult", author: "Dr. J. Morales", content: "Assessment: pre-renal AKI suspected. Recommend isotonic fluids, medication review, and repeat BMP in 6 hours.", signed: true, createdAt: "2026-03-05T16:40:00.000Z" }
        ],
        orders: [
          { id: "ord-1001", name: "Basic metabolic panel", category: "LAB", parameters: { frequency: "q6h" }, status: "SIGNED", rationale: "Trend renal function.", createdAt: "2026-03-05T16:55:00.000Z" }
        ]
      }
    ],
    scenarios: [
      {
        id: "scn-1001",
        title: "AKI chart review — fluid resuscitation and renal monitoring",
        objective: "As the attending physician, review the creatinine trend and urine output, assess volume status, place IV fluid and repeat BMP orders, document your renal assessment with differential, then sign the encounter.",
        rubric: [
          "Review relevant labs, vitals, and clinical notes",
          "Place order: Basic metabolic panel",
          "Place order: Normal saline bolus",
          "Document comprehensive clinical assessment and plan",
          "Sign the encounter"
        ],
        requiredOrders: ["Basic metabolic panel", "Normal saline bolus"],
        requiredNoteElements: [
          "Creatinine trend",
          "Volume assessment",
          "Urine output",
          "AKI differential diagnosis"
        ]
      }
    ]
  },

  // ── 2. Community-Acquired Pneumonia ─────────────────────────────────────
  {
    id: "pat-1002",
    mrn: "SYN-1002",
    fullName: "Robert Chen",
    age: 52,
    sex: "M",
    allergies: ["None known"],
    bannerFlags: ["Droplet precautions"],
    summary: "Seen for fever, productive cough, and exertional dyspnea.",
    encounters: [
      {
        id: "enc-1002",
        type: "Observation",
        reasonForVisit: "Community-acquired pneumonia",
        provider: "Dr. Nina Brooks",
        startedAt: "2026-03-04T11:05:00.000Z",
        status: "OPEN",
        labs: [
          { id: "lab-2001", name: "WBC", loinc: "6690-2", value: "14.8", unit: "K/uL", referenceRange: "4.0-10.5", abnormal: true, collectedAt: "2026-03-04T11:40:00.000Z" },
          { id: "lab-2002", name: "Procalcitonin", loinc: "33959-8", value: "1.8", unit: "ng/mL", referenceRange: "<0.5", abnormal: true, collectedAt: "2026-03-04T11:40:00.000Z" }
        ],
        notes: [
          { id: "note-2001", type: "DISCHARGE", title: "Prior urgent care note", author: "Dr. A. Singh", content: "Started doxycycline yesterday; advised chest imaging if symptoms worsen.", signed: true, createdAt: "2026-03-03T18:20:00.000Z" }
        ],
        orders: [
          { id: "ord-2001", name: "Chest X-ray", category: "IMAGING", parameters: { priority: "Routine" }, status: "PENDING_SIGNATURE", rationale: "Evaluate infiltrate.", createdAt: "2026-03-04T11:50:00.000Z" }
        ]
      }
    ],
    scenarios: [
      {
        id: "scn-1002",
        title: "CAP — antibiotic stewardship and imaging follow-up",
        objective: "As the attending physician, review the chest imaging and culture results, document the antibiotic course and respiratory status, order a follow-up chest X-ray, then sign the encounter.",
        rubric: [
          "Review relevant labs, vitals, and clinical notes",
          "Place order: Chest X-ray",
          "Document clinical assessment and plan",
          "Sign the encounter"
        ],
        requiredOrders: ["Chest X-ray"],
        requiredNoteElements: ["Antibiotic exposure", "Respiratory symptoms", "Follow-up plan"]
      }
    ]
  },

  // ── 3. Diabetic Ketoacidosis ────────────────────────────────────────────
  {
    id: "pat-1003",
    mrn: "SYN-1003",
    fullName: "Sarah Williams",
    age: 28,
    sex: "F",
    allergies: ["Sulfa drugs"],
    bannerFlags: ["Type 1 DM", "Insulin pump"],
    summary: "Presented with nausea, vomiting, abdominal pain, and Kussmaul breathing. Blood glucose 456 with anion-gap acidosis.",
    encounters: [
      {
        id: "enc-1003",
        type: "Inpatient",
        reasonForVisit: "Diabetic ketoacidosis",
        provider: "Dr. Marcus Reid",
        startedAt: "2026-03-06T02:30:00.000Z",
        status: "OPEN",
        labs: [
          { id: "lab-3001", name: "Glucose", loinc: "2345-7", value: "456", unit: "mg/dL", referenceRange: "70-110", abnormal: true, collectedAt: "2026-03-06T02:50:00.000Z" },
          { id: "lab-3002", name: "Anion gap", loinc: "33037-3", value: "24", unit: "mEq/L", referenceRange: "8-12", abnormal: true, collectedAt: "2026-03-06T02:50:00.000Z" },
          { id: "lab-3003", name: "Bicarbonate", loinc: "1963-8", value: "10", unit: "mEq/L", referenceRange: "22-28", abnormal: true, collectedAt: "2026-03-06T02:50:00.000Z" },
          { id: "lab-3004", name: "Venous pH", loinc: "2746-6", value: "7.18", unit: "", referenceRange: "7.32-7.42", abnormal: true, collectedAt: "2026-03-06T02:55:00.000Z" },
          { id: "lab-3005", name: "Potassium", loinc: "2823-3", value: "5.8", unit: "mEq/L", referenceRange: "3.5-5.0", abnormal: true, collectedAt: "2026-03-06T02:50:00.000Z" },
          { id: "lab-3006", name: "Beta-hydroxybutyrate", loinc: "53061-8", value: "6.2", unit: "mmol/L", referenceRange: "<0.6", abnormal: true, collectedAt: "2026-03-06T02:55:00.000Z" }
        ],
        notes: [
          { id: "note-3001", type: "PROGRESS", title: "ED physician note", author: "Dr. L. Huang", content: "28F T1DM presenting with DKA. AG 24, glucose 456, pH 7.18. Started NS 1 L bolus. Insulin pump discontinued on arrival.", signed: true, createdAt: "2026-03-06T03:10:00.000Z" }
        ],
        orders: [
          { id: "ord-3001", name: "Basic metabolic panel", category: "LAB", parameters: { frequency: "q2h" }, status: "SIGNED", rationale: "Monitor anion gap closure and potassium.", createdAt: "2026-03-06T03:00:00.000Z" }
        ]
      }
    ],
    scenarios: [
      {
        id: "scn-1003",
        title: "DKA — insulin protocol and anion-gap monitoring",
        objective: "As the attending physician, review the metabolic panel (glucose, anion gap, pH, bicarbonate), start an insulin drip with serial BMP monitoring, document the DKA severity, precipitant workup, fluid and insulin management, potassium monitoring, and gap closure criteria, then sign the encounter.",
        rubric: [
          "Review relevant labs, vitals, and clinical notes",
          "Place order: Insulin drip",
          "Place order: Basic metabolic panel",
          "Document comprehensive clinical assessment and plan",
          "Sign the encounter"
        ],
        requiredOrders: ["Insulin drip", "Basic metabolic panel"],
        requiredNoteElements: [
          "Anion gap",
          "Blood glucose level",
          "Serum bicarbonate",
          "Fluid resuscitation",
          "Insulin management",
          "DKA precipitant",
          "Potassium monitoring"
        ]
      }
    ]
  },

  // ── 4. Acute Coronary Syndrome (STEMI) ──────────────────────────────────
  {
    id: "pat-1004",
    mrn: "SYN-1004",
    fullName: "James Mitchell",
    age: 71,
    sex: "M",
    allergies: ["None known"],
    bannerFlags: ["HTN", "Hyperlipidemia", "Prior PCI 2019"],
    summary: "Admitted with crushing substernal chest pain radiating to left arm. ECG showed ST elevations in II, III, aVF.",
    encounters: [
      {
        id: "enc-1004",
        type: "Inpatient",
        reasonForVisit: "ST-elevation myocardial infarction",
        provider: "Dr. Carla Vega",
        startedAt: "2026-03-07T06:20:00.000Z",
        status: "OPEN",
        labs: [
          { id: "lab-4001", name: "Troponin I", loinc: "10839-9", value: "8.4", unit: "ng/mL", referenceRange: "<0.04", abnormal: true, collectedAt: "2026-03-07T07:00:00.000Z" },
          { id: "lab-4002", name: "Troponin I", loinc: "10839-9", value: "2.1", unit: "ng/mL", referenceRange: "<0.04", abnormal: true, collectedAt: "2026-03-07T06:30:00.000Z" },
          { id: "lab-4003", name: "CK-MB", loinc: "13969-1", value: "42", unit: "U/L", referenceRange: "0-7", abnormal: true, collectedAt: "2026-03-07T07:00:00.000Z" },
          { id: "lab-4004", name: "BNP", loinc: "30934-4", value: "890", unit: "pg/mL", referenceRange: "<100", abnormal: true, collectedAt: "2026-03-07T07:00:00.000Z" },
          { id: "lab-4005", name: "Creatinine", loinc: "2160-0", value: "1.1", unit: "mg/dL", referenceRange: "0.7-1.3", abnormal: false, collectedAt: "2026-03-07T06:30:00.000Z" }
        ],
        notes: [
          { id: "note-4001", type: "CONSULT", title: "Cardiology consult", author: "Dr. R. Patel", content: "Inferior STEMI. Troponin trending 2.1 to 8.4. Dual antiplatelet therapy initiated (aspirin + clopidogrel). Recommend emergent cath.", signed: true, createdAt: "2026-03-07T07:15:00.000Z" }
        ],
        orders: [
          { id: "ord-4001", name: "ECG 12-lead", category: "LAB", parameters: { frequency: "stat" }, status: "SIGNED", rationale: "Evaluate ST changes.", createdAt: "2026-03-07T06:25:00.000Z" },
          { id: "ord-4002", name: "Troponin I serial", category: "LAB", parameters: { frequency: "q6h" }, status: "SIGNED", rationale: "Trend cardiac biomarkers.", createdAt: "2026-03-07T06:25:00.000Z" }
        ]
      }
    ],
    scenarios: [
      {
        id: "scn-1004",
        title: "STEMI — anticoagulation and cardiac workup",
        objective: "As the attending physician, review serial troponins and ECG findings, place heparin drip and echocardiogram, document the full ACS assessment including risk stratification, ECG interpretation, antiplatelet and anticoagulation rationale, and cardiology consultation, then sign the encounter.",
        rubric: [
          "Review relevant labs, vitals, and clinical notes",
          "Place order: Heparin drip",
          "Place order: Echocardiogram",
          "Document comprehensive clinical assessment and plan",
          "Sign the encounter"
        ],
        requiredOrders: ["Heparin drip", "Echocardiogram"],
        requiredNoteElements: [
          "Troponin trend",
          "ECG interpretation",
          "ST elevation",
          "Chest pain characterization",
          "TIMI risk score",
          "Antiplatelet therapy",
          "Cardiology consultation"
        ]
      }
    ]
  },

  // ── 5. Upper GI Bleed ──────────────────────────────────────────────────
  {
    id: "pat-1005",
    mrn: "SYN-1005",
    fullName: "Patricia Davis",
    age: 59,
    sex: "F",
    allergies: ["NSAIDs"],
    bannerFlags: ["Cirrhosis", "EtOH use disorder"],
    summary: "Presented with hematemesis and melena. Tachycardic and hypotensive on arrival. History of liver cirrhosis.",
    encounters: [
      {
        id: "enc-1005",
        type: "Inpatient",
        reasonForVisit: "Upper gastrointestinal hemorrhage",
        provider: "Dr. Omar Farid",
        startedAt: "2026-03-05T20:10:00.000Z",
        status: "OPEN",
        labs: [
          { id: "lab-5001", name: "Hemoglobin", loinc: "718-7", value: "7.2", unit: "g/dL", referenceRange: "12.0-16.0", abnormal: true, collectedAt: "2026-03-05T20:30:00.000Z" },
          { id: "lab-5002", name: "Hemoglobin", loinc: "718-7", value: "9.8", unit: "g/dL", referenceRange: "12.0-16.0", abnormal: true, collectedAt: "2026-03-04T08:00:00.000Z" },
          { id: "lab-5003", name: "Platelet count", loinc: "777-3", value: "88", unit: "K/uL", referenceRange: "150-400", abnormal: true, collectedAt: "2026-03-05T20:30:00.000Z" },
          { id: "lab-5004", name: "INR", loinc: "6301-6", value: "1.8", unit: "", referenceRange: "0.9-1.1", abnormal: true, collectedAt: "2026-03-05T20:30:00.000Z" },
          { id: "lab-5005", name: "BUN", loinc: "3094-0", value: "42", unit: "mg/dL", referenceRange: "7-20", abnormal: true, collectedAt: "2026-03-05T20:30:00.000Z" }
        ],
        notes: [
          { id: "note-5001", type: "PROGRESS", title: "ED physician note", author: "Dr. K. Simmons", content: "59F with known cirrhosis presenting with hematemesis. Hemodynamically unstable on arrival — HR 118, BP 84/52. Two large-bore IVs placed. Type and crossmatch sent.", signed: true, createdAt: "2026-03-05T20:45:00.000Z" }
        ],
        orders: [
          { id: "ord-5001", name: "CBC", category: "LAB", parameters: { frequency: "q4h" }, status: "SIGNED", rationale: "Trend hemoglobin.", createdAt: "2026-03-05T20:35:00.000Z" },
          { id: "ord-5002", name: "Type and screen", category: "LAB", parameters: { priority: "STAT" }, status: "SIGNED", rationale: "Prepare for transfusion.", createdAt: "2026-03-05T20:35:00.000Z" }
        ]
      }
    ],
    scenarios: [
      {
        id: "scn-1005",
        title: "Upper GI bleed — transfusion and acid suppression",
        objective: "As the attending physician, review hemoglobin trend and coag panel, place PRBC transfusion and IV pantoprazole, document the bleed severity, hemodynamics, and GI consultation need, then sign the encounter.",
        rubric: [
          "Review relevant labs, vitals, and clinical notes",
          "Place order: Packed red blood cells",
          "Place order: Pantoprazole IV",
          "Document comprehensive clinical assessment and plan",
          "Sign the encounter"
        ],
        requiredOrders: ["Packed red blood cells", "Pantoprazole IV"],
        requiredNoteElements: [
          "Hemoglobin trend",
          "Hemodynamic status",
          "Glasgow-Blatchford score",
          "Transfusion plan",
          "GI consultation indication"
        ]
      }
    ]
  },

  // ── 6. COPD Exacerbation ────────────────────────────────────────────────
  {
    id: "pat-1006",
    mrn: "SYN-1006",
    fullName: "William Thompson",
    age: 74,
    sex: "M",
    allergies: ["Aspirin"],
    bannerFlags: ["COPD GOLD III", "Home O2 2L"],
    summary: "Brought in with worsening dyspnea, increased sputum production, and wheezing over 3 days. SpO2 84% on room air.",
    encounters: [
      {
        id: "enc-1006",
        type: "Inpatient",
        reasonForVisit: "Acute COPD exacerbation",
        provider: "Dr. Hannah Cole",
        startedAt: "2026-03-06T09:30:00.000Z",
        status: "OPEN",
        labs: [
          { id: "lab-6001", name: "ABG pH", loinc: "2744-1", value: "7.31", unit: "", referenceRange: "7.35-7.45", abnormal: true, collectedAt: "2026-03-06T09:50:00.000Z" },
          { id: "lab-6002", name: "ABG pCO2", loinc: "2019-8", value: "58", unit: "mmHg", referenceRange: "35-45", abnormal: true, collectedAt: "2026-03-06T09:50:00.000Z" },
          { id: "lab-6003", name: "ABG pO2", loinc: "2703-7", value: "52", unit: "mmHg", referenceRange: "80-100", abnormal: true, collectedAt: "2026-03-06T09:50:00.000Z" },
          { id: "lab-6004", name: "WBC", loinc: "6690-2", value: "13.2", unit: "K/uL", referenceRange: "4.0-10.5", abnormal: true, collectedAt: "2026-03-06T09:50:00.000Z" },
          { id: "lab-6005", name: "Procalcitonin", loinc: "33959-8", value: "0.3", unit: "ng/mL", referenceRange: "<0.5", abnormal: false, collectedAt: "2026-03-06T09:50:00.000Z" }
        ],
        notes: [
          { id: "note-6001", type: "CONSULT", title: "Pulmonology consult", author: "Dr. E. Park", content: "Severe COPD exacerbation with acute-on-chronic hypercapnic respiratory failure. Consider BiPAP. Low suspicion for bacterial PNA given low procalcitonin.", signed: true, createdAt: "2026-03-06T11:00:00.000Z" }
        ],
        orders: [
          { id: "ord-6001", name: "ABG", category: "LAB", parameters: { priority: "STAT" }, status: "SIGNED", rationale: "Assess ventilation and acid-base status.", createdAt: "2026-03-06T09:40:00.000Z" },
          { id: "ord-6002", name: "Chest X-ray", category: "IMAGING", parameters: { priority: "Routine" }, status: "PENDING_SIGNATURE", rationale: "Rule out pneumonia or pneumothorax.", createdAt: "2026-03-06T09:40:00.000Z" }
        ]
      }
    ],
    scenarios: [
      {
        id: "scn-1006",
        title: "COPD exacerbation — systemic steroids and bronchodilators",
        objective: "As the attending physician, review the ABG showing hypercapnic respiratory failure, place IV steroids and nebulizer, document the respiratory acidosis, ABG findings, oxygen needs, and steroid plan, then sign the encounter.",
        rubric: [
          "Review relevant labs, vitals, and clinical notes",
          "Place order: Methylprednisolone IV",
          "Place order: Albuterol nebulizer",
          "Document comprehensive clinical assessment and plan",
          "Sign the encounter"
        ],
        requiredOrders: ["Methylprednisolone IV", "Albuterol nebulizer"],
        requiredNoteElements: [
          "Respiratory acidosis",
          "ABG interpretation",
          "Oxygen requirements",
          "Steroid plan"
        ]
      }
    ]
  },

  // ── 7. Heart Failure Exacerbation ───────────────────────────────────────
  {
    id: "pat-1007",
    mrn: "SYN-1007",
    fullName: "Dorothy Garcia",
    age: 76,
    sex: "F",
    allergies: ["Lisinopril (angioedema)"],
    bannerFlags: ["HFrEF EF 25%", "ICD in place"],
    summary: "Admitted with progressive dyspnea on exertion, orthopnea, and bilateral lower extremity edema over 2 weeks.",
    encounters: [
      {
        id: "enc-1007",
        type: "Inpatient",
        reasonForVisit: "Acute decompensated heart failure",
        provider: "Dr. Irene Walsh",
        startedAt: "2026-03-05T15:00:00.000Z",
        status: "OPEN",
        labs: [
          { id: "lab-7001", name: "BNP", loinc: "30934-4", value: "2450", unit: "pg/mL", referenceRange: "<100", abnormal: true, collectedAt: "2026-03-05T15:30:00.000Z" },
          { id: "lab-7002", name: "Sodium", loinc: "2951-2", value: "131", unit: "mEq/L", referenceRange: "136-145", abnormal: true, collectedAt: "2026-03-05T15:30:00.000Z" },
          { id: "lab-7003", name: "Creatinine", loinc: "2160-0", value: "1.6", unit: "mg/dL", referenceRange: "0.6-1.2", abnormal: true, collectedAt: "2026-03-05T15:30:00.000Z" },
          { id: "lab-7004", name: "Potassium", loinc: "2823-3", value: "4.8", unit: "mEq/L", referenceRange: "3.5-5.0", abnormal: false, collectedAt: "2026-03-05T15:30:00.000Z" }
        ],
        notes: [
          { id: "note-7001", type: "CONSULT", title: "Cardiology note", author: "Dr. V. Nair", content: "Known HFrEF EF 25%. Appears volume overloaded with JVD, bibasilar crackles, and 3+ pitting edema. Weight up 8 lbs from dry weight. Recommend IV diuresis.", signed: true, createdAt: "2026-03-05T16:30:00.000Z" }
        ],
        orders: [
          { id: "ord-7001", name: "BNP", category: "LAB", parameters: { priority: "STAT" }, status: "SIGNED", rationale: "Assess heart failure severity.", createdAt: "2026-03-05T15:20:00.000Z" },
          { id: "ord-7002", name: "Chest X-ray", category: "IMAGING", parameters: { priority: "STAT" }, status: "SIGNED", rationale: "Evaluate pulmonary edema.", createdAt: "2026-03-05T15:20:00.000Z" }
        ]
      }
    ],
    scenarios: [
      {
        id: "scn-1007",
        title: "CHF exacerbation — IV diuresis and volume management",
        objective: "As the attending physician, review BNP, electrolytes, and daily weights, place IV furosemide and renal monitoring, document the volume overload assessment and diuresis strategy, then sign the encounter.",
        rubric: [
          "Review relevant labs, vitals, and clinical notes",
          "Place order: Furosemide IV",
          "Place order: Basic metabolic panel",
          "Document comprehensive clinical assessment and plan",
          "Sign the encounter"
        ],
        requiredOrders: ["Furosemide IV", "Basic metabolic panel"],
        requiredNoteElements: [
          "Volume status",
          "BNP level",
          "Daily weight trend",
          "Ejection fraction",
          "Diuretic plan"
        ]
      }
    ]
  },

  // ── 8. Pulmonary Embolism Workup ────────────────────────────────────────
  {
    id: "pat-1008",
    mrn: "SYN-1008",
    fullName: "Michael Brown",
    age: 45,
    sex: "M",
    allergies: ["None known"],
    bannerFlags: ["Recent knee surgery", "BMI 34"],
    summary: "Presents with acute-onset pleuritic chest pain and dyspnea. Recently had right knee arthroscopy two weeks ago.",
    encounters: [
      {
        id: "enc-1008",
        type: "Observation",
        reasonForVisit: "Suspected pulmonary embolism",
        provider: "Dr. Tanya Moore",
        startedAt: "2026-03-06T14:00:00.000Z",
        status: "OPEN",
        labs: [
          { id: "lab-8001", name: "D-dimer", loinc: "48065-7", value: "4.2", unit: "ug/mL", referenceRange: "<0.5", abnormal: true, collectedAt: "2026-03-06T14:20:00.000Z" },
          { id: "lab-8002", name: "Troponin I", loinc: "10839-9", value: "0.08", unit: "ng/mL", referenceRange: "<0.04", abnormal: true, collectedAt: "2026-03-06T14:20:00.000Z" },
          { id: "lab-8003", name: "ABG pO2", loinc: "2703-7", value: "68", unit: "mmHg", referenceRange: "80-100", abnormal: true, collectedAt: "2026-03-06T14:25:00.000Z" }
        ],
        notes: [
          { id: "note-8001", type: "PROGRESS", title: "ED physician note", author: "Dr. P. Johannsen", content: "45M post-op knee scope 2 weeks ago with acute pleuritic CP and dyspnea. HR 108, SpO2 92%. Wells score intermediate risk. D-dimer markedly elevated at 4.2.", signed: true, createdAt: "2026-03-06T14:40:00.000Z" }
        ],
        orders: [
          { id: "ord-8001", name: "D-dimer", category: "LAB", parameters: { priority: "STAT" }, status: "SIGNED", rationale: "Risk-stratify for PE.", createdAt: "2026-03-06T14:10:00.000Z" },
          { id: "ord-8002", name: "ABG", category: "LAB", parameters: { priority: "STAT" }, status: "SIGNED", rationale: "Assess oxygenation.", createdAt: "2026-03-06T14:10:00.000Z" }
        ]
      }
    ],
    scenarios: [
      {
        id: "scn-1008",
        title: "PE — diagnostic imaging and empiric anticoagulation",
        objective: "As the attending physician, review D-dimer and Wells criteria, place CTA chest and heparin drip, document the PE probability, hemodynamics, and anticoagulation rationale, then sign the encounter.",
        rubric: [
          "Review relevant labs, vitals, and clinical notes",
          "Place order: CT angiography chest",
          "Place order: Heparin drip",
          "Document comprehensive clinical assessment and plan",
          "Sign the encounter"
        ],
        requiredOrders: ["CT angiography chest", "Heparin drip"],
        requiredNoteElements: [
          "D-dimer elevation",
          "Wells score",
          "Hypoxia evaluation",
          "Right heart strain",
          "Anticoagulation plan"
        ]
      }
    ]
  },

  // ── 9. Urosepsis ───────────────────────────────────────────────────────
  {
    id: "pat-1009",
    mrn: "SYN-1009",
    fullName: "Margaret Wilson",
    age: 82,
    sex: "F",
    allergies: ["Fluoroquinolones"],
    bannerFlags: ["Dementia", "Chronic Foley catheter"],
    summary: "Found altered and febrile at nursing home. BP 82/48, HR 112, temp 39.4 C. Foley draining cloudy urine.",
    encounters: [
      {
        id: "enc-1009",
        type: "Inpatient",
        reasonForVisit: "Sepsis secondary to urinary source",
        provider: "Dr. Elena Ruiz",
        startedAt: "2026-03-06T05:45:00.000Z",
        status: "OPEN",
        labs: [
          { id: "lab-9001", name: "WBC", loinc: "6690-2", value: "22.4", unit: "K/uL", referenceRange: "4.0-10.5", abnormal: true, collectedAt: "2026-03-06T06:10:00.000Z" },
          { id: "lab-9002", name: "Lactate", loinc: "2524-7", value: "4.8", unit: "mmol/L", referenceRange: "0.5-2.0", abnormal: true, collectedAt: "2026-03-06T06:10:00.000Z" },
          { id: "lab-9003", name: "Creatinine", loinc: "2160-0", value: "2.1", unit: "mg/dL", referenceRange: "0.6-1.2", abnormal: true, collectedAt: "2026-03-06T06:10:00.000Z" },
          { id: "lab-9004", name: "Urinalysis WBC", loinc: "5821-4", value: "50+", unit: "per HPF", referenceRange: "0-5", abnormal: true, collectedAt: "2026-03-06T06:15:00.000Z" },
          { id: "lab-9005", name: "Urinalysis nitrites", loinc: "5802-4", value: "Positive", unit: "", referenceRange: "Negative", abnormal: true, collectedAt: "2026-03-06T06:15:00.000Z" }
        ],
        notes: [
          { id: "note-9001", type: "PROGRESS", title: "ED physician note", author: "Dr. S. Chowdhury", content: "82F from SNF with sepsis likely urosepsis. qSOFA 3. 30 mL/kg crystalloid bolus initiated. Blood cultures x2 drawn prior to antibiotics.", signed: true, createdAt: "2026-03-06T06:30:00.000Z" }
        ],
        orders: [
          { id: "ord-9001", name: "Blood cultures x2", category: "LAB", parameters: { priority: "STAT" }, status: "SIGNED", rationale: "Identify bacteremia.", createdAt: "2026-03-06T06:05:00.000Z" },
          { id: "ord-9002", name: "Urinalysis", category: "LAB", parameters: { priority: "STAT" }, status: "SIGNED", rationale: "Evaluate urinary source.", createdAt: "2026-03-06T06:05:00.000Z" }
        ]
      }
    ],
    scenarios: [
      {
        id: "scn-1009",
        title: "Urosepsis — SEP-1 bundle compliance",
        objective: "As the attending physician, review lactate, urinalysis, and blood cultures, place empiric IV antibiotics and fluid resuscitation within the SEP-1 bundle, document the full sepsis workup including source, bundle timing, hemodynamic response, and reassessment, then sign the encounter.",
        rubric: [
          "Review relevant labs, vitals, and clinical notes",
          "Place order: Ceftriaxone IV",
          "Place order: Normal saline bolus",
          "Document comprehensive clinical assessment and plan",
          "Sign the encounter"
        ],
        requiredOrders: ["Ceftriaxone IV", "Normal saline bolus"],
        requiredNoteElements: [
          "Sepsis criteria",
          "Lactate level",
          "Source identification",
          "Blood culture timing",
          "Hemodynamic response to fluids",
          "Antibiotic selection rationale",
          "Reassessment plan"
        ]
      }
    ]
  },

  // ── 10. Acute Pancreatitis ──────────────────────────────────────────────
  {
    id: "pat-1010",
    mrn: "SYN-1010",
    fullName: "David Martinez",
    age: 48,
    sex: "M",
    allergies: ["None known"],
    bannerFlags: ["EtOH use", "Obesity BMI 36"],
    summary: "Presents with severe epigastric pain radiating to back after a heavy alcohol binge. Associated nausea and vomiting.",
    encounters: [
      {
        id: "enc-1010",
        type: "Inpatient",
        reasonForVisit: "Acute pancreatitis",
        provider: "Dr. Grace Lin",
        startedAt: "2026-03-05T22:00:00.000Z",
        status: "OPEN",
        labs: [
          { id: "lab-10001", name: "Lipase", loinc: "3040-3", value: "1850", unit: "U/L", referenceRange: "0-160", abnormal: true, collectedAt: "2026-03-05T22:20:00.000Z" },
          { id: "lab-10002", name: "Amylase", loinc: "1798-8", value: "620", unit: "U/L", referenceRange: "28-100", abnormal: true, collectedAt: "2026-03-05T22:20:00.000Z" },
          { id: "lab-10003", name: "ALT", loinc: "1742-6", value: "45", unit: "U/L", referenceRange: "7-56", abnormal: false, collectedAt: "2026-03-05T22:20:00.000Z" },
          { id: "lab-10004", name: "Triglycerides", loinc: "2571-8", value: "280", unit: "mg/dL", referenceRange: "<150", abnormal: true, collectedAt: "2026-03-05T22:20:00.000Z" },
          { id: "lab-10005", name: "Calcium", loinc: "17861-6", value: "8.0", unit: "mg/dL", referenceRange: "8.5-10.5", abnormal: true, collectedAt: "2026-03-05T22:20:00.000Z" },
          { id: "lab-10006", name: "WBC", loinc: "6690-2", value: "14.2", unit: "K/uL", referenceRange: "4.0-10.5", abnormal: true, collectedAt: "2026-03-05T22:20:00.000Z" }
        ],
        notes: [
          { id: "note-10001", type: "PROGRESS", title: "ED physician note", author: "Dr. T. Owens", content: "48M with epigastric pain radiating to back after heavy binge. Lipase 1850. Likely alcohol-induced pancreatitis. BISAP score 2.", signed: true, createdAt: "2026-03-05T22:40:00.000Z" }
        ],
        orders: [
          { id: "ord-10001", name: "Lipase", category: "LAB", parameters: { priority: "STAT" }, status: "SIGNED", rationale: "Confirm pancreatitis diagnosis.", createdAt: "2026-03-05T22:10:00.000Z" },
          { id: "ord-10002", name: "CBC", category: "LAB", parameters: { priority: "STAT" }, status: "SIGNED", rationale: "Assess for leukocytosis.", createdAt: "2026-03-05T22:10:00.000Z" }
        ]
      }
    ],
    scenarios: [
      {
        id: "scn-1010",
        title: "Acute pancreatitis — aggressive hydration and imaging",
        objective: "As the attending physician, review lipase and severity markers, place aggressive fluid resuscitation and CT imaging, document the etiology workup, severity scoring, and nutrition plan, then sign the encounter.",
        rubric: [
          "Review relevant labs, vitals, and clinical notes",
          "Place order: Lactated Ringer bolus",
          "Place order: CT abdomen with contrast",
          "Document comprehensive clinical assessment and plan",
          "Sign the encounter"
        ],
        requiredOrders: ["Lactated Ringer bolus", "CT abdomen with contrast"],
        requiredNoteElements: [
          "Lipase elevation",
          "Gallstone evaluation",
          "Ranson criteria",
          "Fluid management",
          "NPO and nutrition plan"
        ]
      }
    ]
  },

  // ── 11. New-onset Atrial Fibrillation ───────────────────────────────────
  {
    id: "pat-1011",
    mrn: "SYN-1011",
    fullName: "Linda Anderson",
    age: 66,
    sex: "F",
    allergies: ["Amiodarone"],
    bannerFlags: ["Hypothyroidism", "Valvular disease"],
    summary: "Found in rapid atrial fibrillation (HR 142) during post-operative monitoring after hip replacement surgery.",
    encounters: [
      {
        id: "enc-1011",
        type: "Inpatient",
        reasonForVisit: "New-onset atrial fibrillation with RVR",
        provider: "Dr. Samuel Grant",
        startedAt: "2026-03-06T18:00:00.000Z",
        status: "OPEN",
        labs: [
          { id: "lab-11001", name: "TSH", loinc: "3016-3", value: "0.8", unit: "mIU/L", referenceRange: "0.4-4.0", abnormal: false, collectedAt: "2026-03-06T18:20:00.000Z" },
          { id: "lab-11002", name: "Potassium", loinc: "2823-3", value: "3.2", unit: "mEq/L", referenceRange: "3.5-5.0", abnormal: true, collectedAt: "2026-03-06T18:20:00.000Z" },
          { id: "lab-11003", name: "Magnesium", loinc: "19123-9", value: "1.4", unit: "mg/dL", referenceRange: "1.7-2.2", abnormal: true, collectedAt: "2026-03-06T18:20:00.000Z" },
          { id: "lab-11004", name: "Troponin I", loinc: "10839-9", value: "0.02", unit: "ng/mL", referenceRange: "<0.04", abnormal: false, collectedAt: "2026-03-06T18:20:00.000Z" }
        ],
        notes: [
          { id: "note-11001", type: "CONSULT", title: "Cardiology consult", author: "Dr. M. Kapoor", content: "New-onset AFib with RVR post-op (HR 142). TSH normal. Low K and Mg likely contributors. CHA2DS2-VASc = 3. Recommend rate control and electrolyte repletion.", signed: true, createdAt: "2026-03-06T19:00:00.000Z" }
        ],
        orders: [
          { id: "ord-11001", name: "Telemetry", category: "LAB", parameters: { duration: "Continuous" }, status: "SIGNED", rationale: "Continuous rhythm monitoring.", createdAt: "2026-03-06T18:10:00.000Z" },
          { id: "ord-11002", name: "TSH", category: "LAB", parameters: { priority: "STAT" }, status: "SIGNED", rationale: "Rule out thyroid etiology.", createdAt: "2026-03-06T18:10:00.000Z" }
        ]
      }
    ],
    scenarios: [
      {
        id: "scn-1011",
        title: "New-onset AFib with RVR — rate control and stroke risk",
        objective: "As the attending physician, review electrolytes, thyroid function, and telemetry, place IV diltiazem and potassium repletion, document the rhythm analysis, CHA2DS2-VASc score, rate control strategy, and anticoagulation decision, then sign the encounter.",
        rubric: [
          "Review relevant labs, vitals, and clinical notes",
          "Place order: Diltiazem IV",
          "Place order: Potassium chloride IV",
          "Document comprehensive clinical assessment and plan",
          "Sign the encounter"
        ],
        requiredOrders: ["Diltiazem IV", "Potassium chloride IV"],
        requiredNoteElements: [
          "Heart rate",
          "Rhythm interpretation",
          "CHA2DS2-VASc score",
          "Rate control strategy",
          "Anticoagulation decision",
          "Hemodynamic stability"
        ]
      }
    ]
  },

  // ── 12. Hyponatremia (SIADH) ───────────────────────────────────────────
  {
    id: "pat-1012",
    mrn: "SYN-1012",
    fullName: "Richard Taylor",
    age: 58,
    sex: "M",
    allergies: ["None known"],
    bannerFlags: ["SIADH", "Small cell lung cancer"],
    summary: "Found lethargic with sodium 118 on routine labs. Known small cell lung cancer. Currently on SSRI.",
    encounters: [
      {
        id: "enc-1012",
        type: "Inpatient",
        reasonForVisit: "Severe hyponatremia workup",
        provider: "Dr. Julia Fox",
        startedAt: "2026-03-06T10:00:00.000Z",
        status: "OPEN",
        labs: [
          { id: "lab-12001", name: "Sodium", loinc: "2951-2", value: "118", unit: "mEq/L", referenceRange: "136-145", abnormal: true, collectedAt: "2026-03-06T10:20:00.000Z" },
          { id: "lab-12002", name: "Serum osmolality", loinc: "2692-2", value: "248", unit: "mOsm/kg", referenceRange: "275-295", abnormal: true, collectedAt: "2026-03-06T10:20:00.000Z" },
          { id: "lab-12003", name: "Urine osmolality", loinc: "2695-5", value: "520", unit: "mOsm/kg", referenceRange: "300-900", abnormal: false, collectedAt: "2026-03-06T10:25:00.000Z" },
          { id: "lab-12004", name: "Urine sodium", loinc: "2955-3", value: "68", unit: "mEq/L", referenceRange: "20-40", abnormal: true, collectedAt: "2026-03-06T10:25:00.000Z" }
        ],
        notes: [
          { id: "note-12001", type: "CONSULT", title: "Endocrinology consult", author: "Dr. A. Desai", content: "Euvolemic hyponatremia likely SIADH in setting of SCLC. Urine studies consistent: urine osm > serum osm, urine Na > 40. Recommend fluid restriction and consider hypertonic saline if symptomatic.", signed: true, createdAt: "2026-03-06T11:30:00.000Z" }
        ],
        orders: [
          { id: "ord-12001", name: "Serum osmolality", category: "LAB", parameters: { priority: "STAT" }, status: "SIGNED", rationale: "Characterize hyponatremia.", createdAt: "2026-03-06T10:10:00.000Z" },
          { id: "ord-12002", name: "Urine electrolytes", category: "LAB", parameters: { priority: "STAT" }, status: "SIGNED", rationale: "SIADH workup.", createdAt: "2026-03-06T10:10:00.000Z" }
        ]
      }
    ],
    scenarios: [
      {
        id: "scn-1012",
        title: "Severe hyponatremia — SIADH diagnosis and safe correction",
        objective: "As the attending physician, review sodium, serum and urine osmolality, and urine sodium, place hypertonic saline with serial BMP monitoring, document the hyponatremia classification, SIADH diagnostic criteria, and safe correction rate plan with osmotic demyelination risk, then sign the encounter.",
        rubric: [
          "Review relevant labs, vitals, and clinical notes",
          "Place order: Sodium chloride 3% IV",
          "Place order: Basic metabolic panel",
          "Document comprehensive clinical assessment and plan",
          "Sign the encounter"
        ],
        requiredOrders: ["Sodium chloride 3% IV", "Basic metabolic panel"],
        requiredNoteElements: [
          "Sodium level",
          "Serum osmolality",
          "Urine osmolality",
          "Urine sodium",
          "Volume status classification",
          "SIADH assessment",
          "Correction rate goal"
        ]
      }
    ]
  },

  // ── 13. Acute Ischemic Stroke ───────────────────────────────────────────
  {
    id: "pat-1013",
    mrn: "SYN-1013",
    fullName: "Barbara White",
    age: 72,
    sex: "F",
    allergies: ["Contrast dye"],
    bannerFlags: ["Atrial fibrillation", "Not on anticoagulation"],
    summary: "Brought by EMS with sudden-onset right-sided weakness and aphasia. Last known well 90 minutes ago. NIHSS 14.",
    encounters: [
      {
        id: "enc-1013",
        type: "Inpatient",
        reasonForVisit: "Acute ischemic stroke",
        provider: "Dr. Nathan Cross",
        startedAt: "2026-03-07T03:15:00.000Z",
        status: "OPEN",
        labs: [
          { id: "lab-13001", name: "Glucose", loinc: "2345-7", value: "142", unit: "mg/dL", referenceRange: "70-110", abnormal: true, collectedAt: "2026-03-07T03:25:00.000Z" },
          { id: "lab-13002", name: "Platelet count", loinc: "777-3", value: "198", unit: "K/uL", referenceRange: "150-400", abnormal: false, collectedAt: "2026-03-07T03:25:00.000Z" },
          { id: "lab-13003", name: "INR", loinc: "6301-6", value: "1.0", unit: "", referenceRange: "0.9-1.1", abnormal: false, collectedAt: "2026-03-07T03:25:00.000Z" },
          { id: "lab-13004", name: "Creatinine", loinc: "2160-0", value: "0.9", unit: "mg/dL", referenceRange: "0.6-1.2", abnormal: false, collectedAt: "2026-03-07T03:25:00.000Z" }
        ],
        notes: [
          { id: "note-13001", type: "PROGRESS", title: "ED stroke alert note", author: "Dr. C. Yamamoto", content: "72F with acute L MCA syndrome — R hemiplegia and global aphasia. LKW 90 min ago. NIHSS 14. CT head negative for hemorrhage. Within tPA window. Known AFib, not on anticoagulation.", signed: true, createdAt: "2026-03-07T03:40:00.000Z" }
        ],
        orders: [
          { id: "ord-13001", name: "CT head without contrast", category: "IMAGING", parameters: { priority: "STAT" }, status: "SIGNED", rationale: "Rule out hemorrhagic stroke.", createdAt: "2026-03-07T03:20:00.000Z" },
          { id: "ord-13002", name: "CBC", category: "LAB", parameters: { priority: "STAT" }, status: "SIGNED", rationale: "Pre-thrombolytic lab panel.", createdAt: "2026-03-07T03:20:00.000Z" }
        ]
      }
    ],
    scenarios: [
      {
        id: "scn-1013",
        title: "Acute ischemic stroke — thrombolysis decision",
        objective: "As the attending physician, review CT head, INR, platelets, and glucose, assess tPA eligibility, place alteplase and CTA orders, document the NIHSS, time last known well, contraindication screen, eligibility determination, BP management, and neurology consultation, then sign the encounter.",
        rubric: [
          "Review relevant labs, vitals, and clinical notes",
          "Place order: Alteplase IV",
          "Place order: CT angiography head and neck",
          "Document comprehensive clinical assessment and plan",
          "Sign the encounter"
        ],
        requiredOrders: ["Alteplase IV", "CT angiography head and neck"],
        requiredNoteElements: [
          "NIHSS score",
          "Time last known well",
          "CT head interpretation",
          "tPA contraindication screen",
          "tPA eligibility",
          "Blood pressure management",
          "Neurology consultation"
        ]
      }
    ]
  },

  // ── 14. MRSA Cellulitis ─────────────────────────────────────────────────
  {
    id: "pat-1014",
    mrn: "SYN-1014",
    fullName: "Thomas Jackson",
    age: 55,
    sex: "M",
    allergies: ["Penicillin"],
    bannerFlags: ["IVDU", "Hepatitis C", "Prior MRSA"],
    summary: "Presents with expanding erythema, warmth, and purulent drainage from left lower extremity. Fever to 38.9 C.",
    encounters: [
      {
        id: "enc-1014",
        type: "Inpatient",
        reasonForVisit: "Cellulitis with MRSA risk",
        provider: "Dr. Fiona Kemp",
        startedAt: "2026-03-06T12:30:00.000Z",
        status: "OPEN",
        labs: [
          { id: "lab-14001", name: "WBC", loinc: "6690-2", value: "16.8", unit: "K/uL", referenceRange: "4.0-10.5", abnormal: true, collectedAt: "2026-03-06T12:50:00.000Z" },
          { id: "lab-14002", name: "CRP", loinc: "1988-5", value: "12.4", unit: "mg/dL", referenceRange: "<1.0", abnormal: true, collectedAt: "2026-03-06T12:50:00.000Z" },
          { id: "lab-14003", name: "ESR", loinc: "4537-7", value: "68", unit: "mm/hr", referenceRange: "0-20", abnormal: true, collectedAt: "2026-03-06T12:50:00.000Z" },
          { id: "lab-14004", name: "Creatinine", loinc: "2160-0", value: "0.8", unit: "mg/dL", referenceRange: "0.7-1.3", abnormal: false, collectedAt: "2026-03-06T12:50:00.000Z" }
        ],
        notes: [
          { id: "note-14001", type: "PROGRESS", title: "ED physician note", author: "Dr. B. Ahmed", content: "55M IVDU with expanding LLE cellulitis with purulent drainage. Prior MRSA infection 2025. PCN allergic (anaphylaxis). Blood cultures sent. Febrile to 38.9.", signed: true, createdAt: "2026-03-06T13:10:00.000Z" }
        ],
        orders: [
          { id: "ord-14001", name: "Blood cultures x2", category: "LAB", parameters: { priority: "STAT" }, status: "SIGNED", rationale: "Rule out bacteremia.", createdAt: "2026-03-06T12:40:00.000Z" },
          { id: "ord-14002", name: "CBC with differential", category: "LAB", parameters: { priority: "STAT" }, status: "SIGNED", rationale: "Assess leukocytosis.", createdAt: "2026-03-06T12:40:00.000Z" }
        ]
      }
    ],
    scenarios: [
      {
        id: "scn-1014",
        title: "MRSA cellulitis — empiric coverage with allergy consideration",
        objective: "As the attending physician, review inflammatory markers and drug allergies, place vancomycin and wound culture orders, document the MRSA risk, antibiotic choice, and allergy consideration, then sign the encounter.",
        rubric: [
          "Review relevant labs, vitals, and clinical notes",
          "Place order: Vancomycin IV",
          "Place order: Wound culture",
          "Document clinical assessment and plan",
          "Sign the encounter"
        ],
        requiredOrders: ["Vancomycin IV", "Wound culture"],
        requiredNoteElements: ["MRSA risk factors", "Antibiotic selection", "Allergy consideration"]
      }
    ]
  },

  // ── 15. Hyperkalemia ────────────────────────────────────────────────────
  {
    id: "pat-1015",
    mrn: "SYN-1015",
    fullName: "Helen Lee",
    age: 70,
    sex: "F",
    allergies: ["None known"],
    bannerFlags: ["ESRD on HD", "Missed dialysis x2"],
    summary: "Presents with generalized weakness and palpitations. Missed last two hemodialysis sessions. ECG shows peaked T waves.",
    encounters: [
      {
        id: "enc-1015",
        type: "Inpatient",
        reasonForVisit: "Hyperkalemia with ECG changes",
        provider: "Dr. Diana Frost",
        startedAt: "2026-03-07T01:20:00.000Z",
        status: "OPEN",
        labs: [
          { id: "lab-15001", name: "Potassium", loinc: "2823-3", value: "7.2", unit: "mEq/L", referenceRange: "3.5-5.0", abnormal: true, collectedAt: "2026-03-07T01:35:00.000Z" },
          { id: "lab-15002", name: "Creatinine", loinc: "2160-0", value: "8.4", unit: "mg/dL", referenceRange: "0.6-1.2", abnormal: true, collectedAt: "2026-03-07T01:35:00.000Z" },
          { id: "lab-15003", name: "BUN", loinc: "3094-0", value: "92", unit: "mg/dL", referenceRange: "7-20", abnormal: true, collectedAt: "2026-03-07T01:35:00.000Z" },
          { id: "lab-15004", name: "Bicarbonate", loinc: "1963-8", value: "16", unit: "mEq/L", referenceRange: "22-28", abnormal: true, collectedAt: "2026-03-07T01:35:00.000Z" },
          { id: "lab-15005", name: "Calcium", loinc: "17861-6", value: "7.8", unit: "mg/dL", referenceRange: "8.5-10.5", abnormal: true, collectedAt: "2026-03-07T01:35:00.000Z" }
        ],
        notes: [
          { id: "note-15001", type: "PROGRESS", title: "ED physician note", author: "Dr. W. Park", content: "70F ESRD missed HD x2. K 7.2 with ECG changes: peaked T waves and widened QRS. Calcium gluconate 1 g IV given emergently in ED. Nephrology paged for emergent HD.", signed: true, createdAt: "2026-03-07T01:50:00.000Z" }
        ],
        orders: [
          { id: "ord-15001", name: "ECG 12-lead", category: "LAB", parameters: { priority: "STAT" }, status: "SIGNED", rationale: "Evaluate for hyperkalemia-related changes.", createdAt: "2026-03-07T01:25:00.000Z" },
          { id: "ord-15002", name: "Basic metabolic panel", category: "LAB", parameters: { priority: "STAT" }, status: "SIGNED", rationale: "Confirm potassium level.", createdAt: "2026-03-07T01:25:00.000Z" }
        ]
      }
    ],
    scenarios: [
      {
        id: "scn-1015",
        title: "Hyperkalemia — emergent cardiac stabilization",
        objective: "As the attending physician, review potassium and ECG, place emergent calcium gluconate and insulin-dextrose, document the potassium level, ECG changes, and management cascade, then sign the encounter.",
        rubric: [
          "Review relevant labs, vitals, and clinical notes",
          "Place order: Calcium gluconate IV",
          "Place order: Insulin and dextrose IV",
          "Document comprehensive clinical assessment and plan",
          "Sign the encounter"
        ],
        requiredOrders: ["Calcium gluconate IV", "Insulin and dextrose IV"],
        requiredNoteElements: [
          "Potassium level",
          "ECG changes",
          "Emergent management",
          "Potassium shifting agents"
        ]
      }
    ]
  },

  // ── 16. Hepatic Encephalopathy ──────────────────────────────────────────
  {
    id: "pat-1016",
    mrn: "SYN-1016",
    fullName: "Frank Rodriguez",
    age: 62,
    sex: "M",
    allergies: ["Omeprazole"],
    bannerFlags: ["Cirrhosis MELD 24", "Ascites"],
    summary: "Found confused and disoriented by family. Known cirrhosis with prior variceal bleed. Asterixis noted on exam.",
    encounters: [
      {
        id: "enc-1016",
        type: "Inpatient",
        reasonForVisit: "Hepatic encephalopathy",
        provider: "Dr. Rachel Stone",
        startedAt: "2026-03-05T19:30:00.000Z",
        status: "OPEN",
        labs: [
          { id: "lab-16001", name: "Ammonia", loinc: "1988-5", value: "142", unit: "umol/L", referenceRange: "15-45", abnormal: true, collectedAt: "2026-03-05T19:50:00.000Z" },
          { id: "lab-16002", name: "INR", loinc: "6301-6", value: "2.2", unit: "", referenceRange: "0.9-1.1", abnormal: true, collectedAt: "2026-03-05T19:50:00.000Z" },
          { id: "lab-16003", name: "Albumin", loinc: "1751-7", value: "2.1", unit: "g/dL", referenceRange: "3.5-5.0", abnormal: true, collectedAt: "2026-03-05T19:50:00.000Z" },
          { id: "lab-16004", name: "Total bilirubin", loinc: "1975-2", value: "4.8", unit: "mg/dL", referenceRange: "0.1-1.2", abnormal: true, collectedAt: "2026-03-05T19:50:00.000Z" },
          { id: "lab-16005", name: "Creatinine", loinc: "2160-0", value: "1.8", unit: "mg/dL", referenceRange: "0.7-1.3", abnormal: true, collectedAt: "2026-03-05T19:50:00.000Z" }
        ],
        notes: [
          { id: "note-16001", type: "CONSULT", title: "Hepatology consult", author: "Dr. Y. Tanaka", content: "Decompensated cirrhosis with hepatic encephalopathy grade II-III. Asterixis present. Likely precipitant: medication non-adherence to lactulose. Recommend lactulose titration to 3-4 BM/day and rifaximin.", signed: true, createdAt: "2026-03-05T20:30:00.000Z" }
        ],
        orders: [
          { id: "ord-16001", name: "Ammonia level", category: "LAB", parameters: { priority: "STAT" }, status: "SIGNED", rationale: "Assess encephalopathy severity.", createdAt: "2026-03-05T19:40:00.000Z" },
          { id: "ord-16002", name: "Hepatic function panel", category: "LAB", parameters: { priority: "STAT" }, status: "SIGNED", rationale: "Baseline liver function.", createdAt: "2026-03-05T19:40:00.000Z" }
        ]
      }
    ],
    scenarios: [
      {
        id: "scn-1016",
        title: "Hepatic encephalopathy — lactulose titration and rifaximin",
        objective: "As the attending physician, review ammonia and hepatic function, place lactulose and rifaximin, document the encephalopathy grading, precipitant, and titration goals, then sign the encounter.",
        rubric: [
          "Review relevant labs, vitals, and clinical notes",
          "Place order: Lactulose oral",
          "Place order: Rifaximin oral",
          "Document comprehensive clinical assessment and plan",
          "Sign the encounter"
        ],
        requiredOrders: ["Lactulose oral", "Rifaximin oral"],
        requiredNoteElements: [
          "Ammonia level",
          "Mental status changes",
          "West Haven grade",
          "Precipitant identification",
          "Lactulose plan"
        ]
      }
    ]
  },

  // ── 17. Anaphylaxis ─────────────────────────────────────────────────────
  {
    id: "pat-1017",
    mrn: "SYN-1017",
    fullName: "Susan Clark",
    age: 34,
    sex: "F",
    allergies: ["Bee stings", "Ceftriaxone (new)"],
    bannerFlags: ["Asthma", "EpiPen prescribed"],
    summary: "Developed diffuse urticaria, angioedema, and wheezing within minutes of IV ceftriaxone. BP dropped to 78/42.",
    encounters: [
      {
        id: "enc-1017",
        type: "Inpatient",
        reasonForVisit: "Anaphylaxis to ceftriaxone",
        provider: "Dr. Kevin Marsh",
        startedAt: "2026-03-06T16:00:00.000Z",
        status: "OPEN",
        labs: [
          { id: "lab-17001", name: "Tryptase", loinc: "18190-9", value: "28.4", unit: "ng/mL", referenceRange: "<11.4", abnormal: true, collectedAt: "2026-03-06T16:30:00.000Z" },
          { id: "lab-17002", name: "WBC", loinc: "6690-2", value: "11.2", unit: "K/uL", referenceRange: "4.0-10.5", abnormal: true, collectedAt: "2026-03-06T16:30:00.000Z" },
          { id: "lab-17003", name: "Lactate", loinc: "2524-7", value: "2.8", unit: "mmol/L", referenceRange: "0.5-2.0", abnormal: true, collectedAt: "2026-03-06T16:30:00.000Z" }
        ],
        notes: [
          { id: "note-17001", type: "PROGRESS", title: "Nursing rapid response note", author: "RN M. Torres", content: "Patient developed urticaria, lip/tongue swelling, and audible wheezing within 5 minutes of ceftriaxone infusion start. Drug stopped immediately. IM epinephrine 0.3 mg administered to right thigh. BP 78/42 then 96/64 post-epi.", signed: true, createdAt: "2026-03-06T16:15:00.000Z" }
        ],
        orders: [
          { id: "ord-17001", name: "Tryptase level", category: "LAB", parameters: { priority: "STAT" }, status: "SIGNED", rationale: "Confirm anaphylaxis diagnosis.", createdAt: "2026-03-06T16:20:00.000Z" }
        ]
      }
    ],
    scenarios: [
      {
        id: "scn-1017",
        title: "Anaphylaxis — epinephrine infusion and allergen documentation",
        objective: "As the attending physician, review tryptase and vital sign trajectory, place epinephrine infusion and IV steroids, document the anaphylaxis diagnostic criteria, causative agent, airway assessment, epinephrine dosing, hemodynamic response, and biphasic reaction monitoring plan, then sign the encounter.",
        rubric: [
          "Review relevant labs, vitals, and clinical notes",
          "Place order: Epinephrine IV drip",
          "Place order: Methylprednisolone IV",
          "Document comprehensive clinical assessment and plan",
          "Sign the encounter"
        ],
        requiredOrders: ["Epinephrine IV drip", "Methylprednisolone IV"],
        requiredNoteElements: [
          "Causative agent",
          "Anaphylaxis criteria",
          "Epinephrine administration",
          "Airway assessment",
          "Hemodynamic response",
          "Biphasic reaction monitoring"
        ]
      }
    ]
  },

  // ── 18. Hip Fracture ────────────────────────────────────────────────────
  {
    id: "pat-1018",
    mrn: "SYN-1018",
    fullName: "Eleanor Harris",
    age: 84,
    sex: "F",
    allergies: ["Codeine"],
    bannerFlags: ["Osteoporosis", "Warfarin for AFib"],
    summary: "Fell at home and unable to bear weight. X-ray confirms left intertrochanteric hip fracture. On warfarin.",
    encounters: [
      {
        id: "enc-1018",
        type: "Inpatient",
        reasonForVisit: "Left hip fracture",
        provider: "Dr. Philip Dunn",
        startedAt: "2026-03-06T08:00:00.000Z",
        status: "OPEN",
        labs: [
          { id: "lab-18001", name: "Hemoglobin", loinc: "718-7", value: "10.2", unit: "g/dL", referenceRange: "12.0-16.0", abnormal: true, collectedAt: "2026-03-06T08:20:00.000Z" },
          { id: "lab-18002", name: "INR", loinc: "6301-6", value: "2.8", unit: "", referenceRange: "0.9-1.1", abnormal: true, collectedAt: "2026-03-06T08:20:00.000Z" },
          { id: "lab-18003", name: "Creatinine", loinc: "2160-0", value: "1.1", unit: "mg/dL", referenceRange: "0.6-1.2", abnormal: false, collectedAt: "2026-03-06T08:20:00.000Z" },
          { id: "lab-18004", name: "Platelet count", loinc: "777-3", value: "210", unit: "K/uL", referenceRange: "150-400", abnormal: false, collectedAt: "2026-03-06T08:20:00.000Z" }
        ],
        notes: [
          { id: "note-18001", type: "CONSULT", title: "Orthopedic surgery consult", author: "Dr. J. Alvarez", content: "Left intertrochanteric hip fracture on plain films. Needs ORIF. INR 2.8 supratherapeutic, must reverse before OR. Hold warfarin. Coordinate with medicine for reversal.", signed: true, createdAt: "2026-03-06T09:00:00.000Z" }
        ],
        orders: [
          { id: "ord-18001", name: "X-ray left hip", category: "IMAGING", parameters: { priority: "STAT" }, status: "SIGNED", rationale: "Evaluate fracture.", createdAt: "2026-03-06T08:10:00.000Z" },
          { id: "ord-18002", name: "CBC", category: "LAB", parameters: { priority: "STAT" }, status: "SIGNED", rationale: "Assess blood loss.", createdAt: "2026-03-06T08:10:00.000Z" }
        ]
      }
    ],
    scenarios: [
      {
        id: "scn-1018",
        title: "Hip fracture — anticoagulation reversal for surgical clearance",
        objective: "As the attending physician, review the fracture imaging and supratherapeutic INR, place vitamin K reversal and orthopedic consult, document the fracture type, reversal plan, and surgical disposition, then sign the encounter.",
        rubric: [
          "Review relevant labs, vitals, and clinical notes",
          "Place order: Vitamin K IV",
          "Place order: Orthopedic surgery consult",
          "Document clinical assessment and plan",
          "Sign the encounter"
        ],
        requiredOrders: ["Vitamin K IV", "Orthopedic surgery consult"],
        requiredNoteElements: ["Fracture type", "Anticoagulation reversal", "Surgical planning"]
      }
    ]
  },

  // ── 19. Severe Asthma Exacerbation ──────────────────────────────────────
  {
    id: "pat-1019",
    mrn: "SYN-1019",
    fullName: "Maria Lopez",
    age: 22,
    sex: "F",
    allergies: ["None known"],
    bannerFlags: ["Severe persistent asthma", "Prior intubation 2024"],
    summary: "Presents with severe dyspnea, inability to speak full sentences, and accessory muscle use. Peak flow 35% of predicted.",
    encounters: [
      {
        id: "enc-1019",
        type: "Inpatient",
        reasonForVisit: "Severe asthma exacerbation",
        provider: "Dr. Lisa Chang",
        startedAt: "2026-03-07T02:00:00.000Z",
        status: "OPEN",
        labs: [
          { id: "lab-19001", name: "ABG pH", loinc: "2744-1", value: "7.38", unit: "", referenceRange: "7.35-7.45", abnormal: false, collectedAt: "2026-03-07T02:15:00.000Z" },
          { id: "lab-19002", name: "ABG pCO2", loinc: "2019-8", value: "42", unit: "mmHg", referenceRange: "35-45", abnormal: false, collectedAt: "2026-03-07T02:15:00.000Z" },
          { id: "lab-19003", name: "ABG pO2", loinc: "2703-7", value: "62", unit: "mmHg", referenceRange: "80-100", abnormal: true, collectedAt: "2026-03-07T02:15:00.000Z" },
          { id: "lab-19004", name: "Potassium", loinc: "2823-3", value: "3.6", unit: "mEq/L", referenceRange: "3.5-5.0", abnormal: false, collectedAt: "2026-03-07T02:15:00.000Z" }
        ],
        notes: [
          { id: "note-19001", type: "PROGRESS", title: "ED physician note", author: "Dr. H. Nakamura", content: "22F with severe persistent asthma. Peak flow 35% predicted. Normal pCO2 in the setting of severe obstruction is concerning for impending respiratory failure. History of intubation 2024. Continuous nebs started.", signed: true, createdAt: "2026-03-07T02:30:00.000Z" }
        ],
        orders: [
          { id: "ord-19001", name: "ABG", category: "LAB", parameters: { priority: "STAT" }, status: "SIGNED", rationale: "Assess ventilatory status.", createdAt: "2026-03-07T02:05:00.000Z" },
          { id: "ord-19002", name: "Chest X-ray", category: "IMAGING", parameters: { priority: "STAT" }, status: "SIGNED", rationale: "Rule out pneumothorax.", createdAt: "2026-03-07T02:05:00.000Z" }
        ]
      }
    ],
    scenarios: [
      {
        id: "scn-1019",
        title: "Severe asthma — IV magnesium and systemic steroids",
        objective: "As the attending physician, review ABG (noting ominous normal pCO2), peak flow, and accessory muscle use, place IV magnesium and systemic steroids, document the severity classification, bronchodilator response, intubation readiness, and ICU escalation criteria, then sign the encounter.",
        rubric: [
          "Review relevant labs, vitals, and clinical notes",
          "Place order: Magnesium sulfate IV",
          "Place order: Methylprednisolone IV",
          "Document comprehensive clinical assessment and plan",
          "Sign the encounter"
        ],
        requiredOrders: ["Magnesium sulfate IV", "Methylprednisolone IV"],
        requiredNoteElements: [
          "Peak flow",
          "ABG with pCO2 interpretation",
          "Accessory muscle use",
          "Steroid therapy",
          "Bronchodilator response",
          "Intubation readiness"
        ]
      }
    ]
  },

  // ── 20. Alcohol Withdrawal ──────────────────────────────────────────────
  {
    id: "pat-1020",
    mrn: "SYN-1020",
    fullName: "Kevin Murphy",
    age: 46,
    sex: "M",
    allergies: ["None known"],
    bannerFlags: ["Alcohol use disorder", "Seizure history"],
    summary: "Admitted for elective procedure. Last drink 18 hours ago. Developing tremor, diaphoresis, and agitation. CIWA score 24.",
    encounters: [
      {
        id: "enc-1020",
        type: "Inpatient",
        reasonForVisit: "Acute alcohol withdrawal",
        provider: "Dr. Brian Foster",
        startedAt: "2026-03-06T07:00:00.000Z",
        status: "OPEN",
        labs: [
          { id: "lab-20001", name: "Ethanol level", loinc: "5643-2", value: "<10", unit: "mg/dL", referenceRange: "<10", abnormal: false, collectedAt: "2026-03-06T07:20:00.000Z" },
          { id: "lab-20002", name: "Magnesium", loinc: "19123-9", value: "1.3", unit: "mg/dL", referenceRange: "1.7-2.2", abnormal: true, collectedAt: "2026-03-06T07:20:00.000Z" },
          { id: "lab-20003", name: "Phosphate", loinc: "14879-1", value: "2.0", unit: "mg/dL", referenceRange: "2.5-4.5", abnormal: true, collectedAt: "2026-03-06T07:20:00.000Z" },
          { id: "lab-20004", name: "AST", loinc: "1920-8", value: "98", unit: "U/L", referenceRange: "10-40", abnormal: true, collectedAt: "2026-03-06T07:20:00.000Z" },
          { id: "lab-20005", name: "ALT", loinc: "1742-6", value: "64", unit: "U/L", referenceRange: "7-56", abnormal: true, collectedAt: "2026-03-06T07:20:00.000Z" },
          { id: "lab-20006", name: "Platelet count", loinc: "777-3", value: "112", unit: "K/uL", referenceRange: "150-400", abnormal: true, collectedAt: "2026-03-06T07:20:00.000Z" }
        ],
        notes: [
          { id: "note-20001", type: "PROGRESS", title: "Admission note", author: "Dr. B. Foster", content: "46M admitted pre-op, developing acute alcohol withdrawal. CIWA 24. Last drink 18 hours ago. History of withdrawal seizures and DTs in 2023. Tremulous, diaphoretic, agitated.", signed: true, createdAt: "2026-03-06T07:40:00.000Z" }
        ],
        orders: [
          { id: "ord-20001", name: "Comprehensive metabolic panel", category: "LAB", parameters: { priority: "STAT" }, status: "SIGNED", rationale: "Baseline metabolic assessment.", createdAt: "2026-03-06T07:10:00.000Z" },
          { id: "ord-20002", name: "Ethanol level", category: "LAB", parameters: { priority: "STAT" }, status: "SIGNED", rationale: "Confirm alcohol clearance.", createdAt: "2026-03-06T07:10:00.000Z" }
        ]
      }
    ],
    scenarios: [
      {
        id: "scn-1020",
        title: "Alcohol withdrawal — CIWA-guided benzodiazepine protocol",
        objective: "As the attending physician, review CIWA score and seizure history, place lorazepam and IV thiamine, document the withdrawal severity, benzodiazepine plan, and DT risk, then sign the encounter.",
        rubric: [
          "Review relevant labs, vitals, and clinical notes",
          "Place order: Lorazepam IV",
          "Place order: Thiamine IV",
          "Document comprehensive clinical assessment and plan",
          "Sign the encounter"
        ],
        requiredOrders: ["Lorazepam IV", "Thiamine IV"],
        requiredNoteElements: [
          "CIWA score",
          "Seizure history",
          "Last drink timing",
          "Benzodiazepine plan",
          "Delirium tremens risk"
        ]
      }
    ]
  },

  // ── 21. C. difficile Colitis ────────────────────────────────────────────
  {
    id: "pat-1021",
    mrn: "SYN-1021",
    fullName: "Ruth Phillips",
    age: 73,
    sex: "F",
    allergies: ["Clindamycin"],
    bannerFlags: ["Recent hospitalization", "Prior C. diff infection"],
    summary: "Readmitted with profuse watery diarrhea (8 episodes/day), abdominal cramping, and low-grade fever after recent cephalosporin course.",
    encounters: [
      {
        id: "enc-1021",
        type: "Inpatient",
        reasonForVisit: "Recurrent C. difficile colitis",
        provider: "Dr. Anne Sullivan",
        startedAt: "2026-03-05T13:00:00.000Z",
        status: "OPEN",
        labs: [
          { id: "lab-21001", name: "WBC", loinc: "6690-2", value: "28.4", unit: "K/uL", referenceRange: "4.0-10.5", abnormal: true, collectedAt: "2026-03-05T13:20:00.000Z" },
          { id: "lab-21002", name: "C. diff toxin PCR", loinc: "54067-4", value: "Positive", unit: "", referenceRange: "Negative", abnormal: true, collectedAt: "2026-03-05T13:30:00.000Z" },
          { id: "lab-21003", name: "Creatinine", loinc: "2160-0", value: "1.4", unit: "mg/dL", referenceRange: "0.6-1.2", abnormal: true, collectedAt: "2026-03-05T13:20:00.000Z" },
          { id: "lab-21004", name: "Albumin", loinc: "1751-7", value: "2.8", unit: "g/dL", referenceRange: "3.5-5.0", abnormal: true, collectedAt: "2026-03-05T13:20:00.000Z" },
          { id: "lab-21005", name: "Lactate", loinc: "2524-7", value: "1.6", unit: "mmol/L", referenceRange: "0.5-2.0", abnormal: false, collectedAt: "2026-03-05T13:20:00.000Z" }
        ],
        notes: [
          { id: "note-21001", type: "CONSULT", title: "Infectious disease consult", author: "Dr. G. Ibrahim", content: "Recurrent C. diff colitis. WBC 28.4 concerning for severe disease (WBC > 15K criteria met). Received cephalosporins during last admission 2 weeks ago. Recommend oral vancomycin 125 mg QID. Consider CT abdomen if clinical worsening to rule out megacolon.", signed: true, createdAt: "2026-03-05T14:00:00.000Z" }
        ],
        orders: [
          { id: "ord-21001", name: "C. diff toxin PCR", category: "LAB", parameters: { priority: "STAT" }, status: "SIGNED", rationale: "Confirm recurrent C. diff.", createdAt: "2026-03-05T13:10:00.000Z" },
          { id: "ord-21002", name: "Stool studies", category: "LAB", parameters: { priority: "Urgent" }, status: "SIGNED", rationale: "Rule out other enteric pathogens.", createdAt: "2026-03-05T13:10:00.000Z" }
        ]
      }
    ],
    scenarios: [
      {
        id: "scn-1021",
        title: "C. difficile colitis — severity-guided oral vancomycin",
        objective: "As the attending physician, review C. diff PCR and severity markers (WBC, creatinine), place oral vancomycin and CT abdomen, document the severity classification, prior antibiotic exposure, and treatment plan, then sign the encounter.",
        rubric: [
          "Review relevant labs, vitals, and clinical notes",
          "Place order: Vancomycin oral",
          "Place order: CT abdomen pelvis",
          "Document clinical assessment and plan",
          "Sign the encounter"
        ],
        requiredOrders: ["Vancomycin oral", "CT abdomen pelvis"],
        requiredNoteElements: ["C. diff severity", "Prior antibiotic exposure", "Oral vancomycin plan"]
      }
    ]
  },

  // ── 22. Thyroid Storm ───────────────────────────────────────────────────
  {
    id: "pat-1022",
    mrn: "SYN-1022",
    fullName: "Jennifer Adams",
    age: 38,
    sex: "F",
    allergies: ["Iodine (rash)"],
    bannerFlags: ["Graves disease", "Medication non-adherent"],
    summary: "Presents with fever 39.8 C, HR 156, agitation, and tremor. Non-adherent to propylthiouracil for 3 weeks.",
    encounters: [
      {
        id: "enc-1022",
        type: "Inpatient",
        reasonForVisit: "Thyroid storm",
        provider: "Dr. Carol Bennett",
        startedAt: "2026-03-07T04:30:00.000Z",
        status: "OPEN",
        labs: [
          { id: "lab-22001", name: "TSH", loinc: "3016-3", value: "<0.01", unit: "mIU/L", referenceRange: "0.4-4.0", abnormal: true, collectedAt: "2026-03-07T04:50:00.000Z" },
          { id: "lab-22002", name: "Free T4", loinc: "3024-7", value: "7.8", unit: "ng/dL", referenceRange: "0.8-1.8", abnormal: true, collectedAt: "2026-03-07T04:50:00.000Z" },
          { id: "lab-22003", name: "Free T3", loinc: "3051-0", value: "18.2", unit: "pg/mL", referenceRange: "2.3-4.2", abnormal: true, collectedAt: "2026-03-07T04:50:00.000Z" },
          { id: "lab-22004", name: "AST", loinc: "1920-8", value: "88", unit: "U/L", referenceRange: "10-40", abnormal: true, collectedAt: "2026-03-07T04:50:00.000Z" },
          { id: "lab-22005", name: "Calcium", loinc: "17861-6", value: "11.2", unit: "mg/dL", referenceRange: "8.5-10.5", abnormal: true, collectedAt: "2026-03-07T04:50:00.000Z" }
        ],
        notes: [
          { id: "note-22001", type: "CONSULT", title: "Endocrinology consult", author: "Dr. P. Sharma", content: "Burch-Wartofsky score 55 consistent with thyroid storm. Graves disease with PTU non-adherence x3 weeks. Needs PTU, beta-blocker for rate control, stress-dose hydrocortisone, and cooling measures. Iodine allergy limits SSKI use.", signed: true, createdAt: "2026-03-07T05:15:00.000Z" }
        ],
        orders: [
          { id: "ord-22001", name: "Thyroid function panel", category: "LAB", parameters: { priority: "STAT" }, status: "SIGNED", rationale: "Confirm thyrotoxicosis.", createdAt: "2026-03-07T04:40:00.000Z" },
          { id: "ord-22002", name: "CBC", category: "LAB", parameters: { priority: "STAT" }, status: "SIGNED", rationale: "Baseline before thionamide.", createdAt: "2026-03-07T04:40:00.000Z" }
        ]
      }
    ],
    scenarios: [
      {
        id: "scn-1022",
        title: "Thyroid storm — multi-drug thyroid blockade and rate control",
        objective: "As the attending physician, review TSH, free T4/T3, and vital sign instability, place PTU and IV propranolol for dual blockade and rate control, document the Burch-Wartofsky score, anti-thyroid therapy, rate control rationale, temperature management, and precipitant, then sign the encounter.",
        rubric: [
          "Review relevant labs, vitals, and clinical notes",
          "Place order: Propylthiouracil oral",
          "Place order: Propranolol IV",
          "Document comprehensive clinical assessment and plan",
          "Sign the encounter"
        ],
        requiredOrders: ["Propylthiouracil oral", "Propranolol IV"],
        requiredNoteElements: [
          "Thyroid hormone levels",
          "Burch-Wartofsky score",
          "Anti-thyroid therapy",
          "Beta-blocker rationale",
          "Temperature management",
          "Precipitating event"
        ]
      }
    ]
  },

  // ── 23. Sickle Cell Vaso-Occlusive Crisis ──────────────────────────────
  {
    id: "pat-1023",
    mrn: "SYN-1023",
    fullName: "Deshawn Carter",
    age: 24,
    sex: "M",
    allergies: ["Morphine (itching)"],
    bannerFlags: ["HbSS disease", "Chronic pain", "Cholecystectomy 2024"],
    summary: "Presents with severe bilateral lower extremity and low back pain. Temperature 38.4 C, SpO2 91% on room air.",
    encounters: [
      {
        id: "enc-1023",
        type: "Inpatient",
        reasonForVisit: "Sickle cell vaso-occlusive crisis",
        provider: "Dr. Angela Price",
        startedAt: "2026-03-06T20:00:00.000Z",
        status: "OPEN",
        labs: [
          { id: "lab-23001", name: "Hemoglobin", loinc: "718-7", value: "6.8", unit: "g/dL", referenceRange: "12.0-17.0", abnormal: true, collectedAt: "2026-03-06T20:20:00.000Z" },
          { id: "lab-23002", name: "Reticulocyte count", loinc: "17849-1", value: "12.4", unit: "%", referenceRange: "0.5-2.5", abnormal: true, collectedAt: "2026-03-06T20:20:00.000Z" },
          { id: "lab-23003", name: "LDH", loinc: "2532-0", value: "580", unit: "U/L", referenceRange: "140-280", abnormal: true, collectedAt: "2026-03-06T20:20:00.000Z" },
          { id: "lab-23004", name: "Total bilirubin", loinc: "1975-2", value: "3.8", unit: "mg/dL", referenceRange: "0.1-1.2", abnormal: true, collectedAt: "2026-03-06T20:20:00.000Z" },
          { id: "lab-23005", name: "WBC", loinc: "6690-2", value: "18.6", unit: "K/uL", referenceRange: "4.0-10.5", abnormal: true, collectedAt: "2026-03-06T20:20:00.000Z" }
        ],
        notes: [
          { id: "note-23001", type: "CONSULT", title: "Hematology consult", author: "Dr. N. Washington", content: "HbSS patient with VOC. Baseline Hb 8.5, currently 6.8 with elevated LDH 580 and reticulocyte count 12.4%. Active hemolysis. Fever 38.4 and SpO2 91% concerning for acute chest syndrome. Obtain CXR. Avoid morphine per allergy. Consider PCA with hydromorphone.", signed: true, createdAt: "2026-03-06T21:00:00.000Z" }
        ],
        orders: [
          { id: "ord-23001", name: "CBC with reticulocyte count", category: "LAB", parameters: { priority: "STAT" }, status: "SIGNED", rationale: "Assess hemolysis severity.", createdAt: "2026-03-06T20:10:00.000Z" },
          { id: "ord-23002", name: "Type and screen", category: "LAB", parameters: { priority: "STAT" }, status: "SIGNED", rationale: "Prepare for possible transfusion.", createdAt: "2026-03-06T20:10:00.000Z" }
        ]
      }
    ],
    scenarios: [
      {
        id: "scn-1023",
        title: "Sickle cell VOC — pain management and ACS screening",
        objective: "As the attending physician, review hemolysis markers and hemoglobin, place hydromorphone PCA (noting morphine allergy) and CXR for ACS screening, document the pain assessment, ACS evaluation, and transfusion threshold, then sign the encounter.",
        rubric: [
          "Review relevant labs, vitals, and clinical notes",
          "Place order: Hydromorphone PCA",
          "Place order: Chest X-ray",
          "Document comprehensive clinical assessment and plan",
          "Sign the encounter"
        ],
        requiredOrders: ["Hydromorphone PCA", "Chest X-ray"],
        requiredNoteElements: [
          "Hemoglobin baseline",
          "Pain assessment",
          "Acute chest syndrome screening",
          "Morphine allergy and opioid selection",
          "Transfusion threshold"
        ]
      }
    ]
  },

  // ── 24. Bacterial Meningitis ────────────────────────────────────────────
  {
    id: "pat-1024",
    mrn: "SYN-1024",
    fullName: "Emily Turner",
    age: 19,
    sex: "F",
    allergies: ["None known"],
    bannerFlags: ["College student", "Meningococcal vaccine pending"],
    summary: "Presents with severe headache, neck stiffness, photophobia, fever 39.6 C, and a petechial rash on trunk.",
    encounters: [
      {
        id: "enc-1024",
        type: "Inpatient",
        reasonForVisit: "Suspected bacterial meningitis",
        provider: "Dr. Victor Reyes",
        startedAt: "2026-03-07T00:15:00.000Z",
        status: "OPEN",
        labs: [
          { id: "lab-24001", name: "WBC", loinc: "6690-2", value: "19.2", unit: "K/uL", referenceRange: "4.0-10.5", abnormal: true, collectedAt: "2026-03-07T00:30:00.000Z" },
          { id: "lab-24002", name: "CSF WBC", loinc: "26464-8", value: "2200", unit: "cells/uL", referenceRange: "0-5", abnormal: true, collectedAt: "2026-03-07T00:45:00.000Z" },
          { id: "lab-24003", name: "CSF glucose", loinc: "2342-4", value: "18", unit: "mg/dL", referenceRange: "40-70", abnormal: true, collectedAt: "2026-03-07T00:45:00.000Z" },
          { id: "lab-24004", name: "CSF protein", loinc: "2880-3", value: "280", unit: "mg/dL", referenceRange: "15-45", abnormal: true, collectedAt: "2026-03-07T00:45:00.000Z" },
          { id: "lab-24005", name: "Lactate", loinc: "2524-7", value: "3.2", unit: "mmol/L", referenceRange: "0.5-2.0", abnormal: true, collectedAt: "2026-03-07T00:30:00.000Z" }
        ],
        notes: [
          { id: "note-24001", type: "PROGRESS", title: "ED physician note", author: "Dr. D. Okafor", content: "19F college student with classic meningitis syndrome: headache, nuchal rigidity, photophobia, fever 39.6. Petechial rash raises concern for N. meningitidis. LP performed. CSF WBC 2200, glucose 18, protein 280 consistent with bacterial meningitis. Empiric abx started.", signed: true, createdAt: "2026-03-07T01:00:00.000Z" }
        ],
        orders: [
          { id: "ord-24001", name: "Lumbar puncture", category: "LAB", parameters: { priority: "STAT" }, status: "SIGNED", rationale: "Obtain CSF for analysis.", createdAt: "2026-03-07T00:20:00.000Z" },
          { id: "ord-24002", name: "Blood cultures x2", category: "LAB", parameters: { priority: "STAT" }, status: "SIGNED", rationale: "Identify causative organism.", createdAt: "2026-03-07T00:20:00.000Z" }
        ]
      }
    ],
    scenarios: [
      {
        id: "scn-1024",
        title: "Bacterial meningitis — empiric antibiotics and adjunctive steroids",
        objective: "As the attending physician, review CSF analysis (cell count, glucose, protein, Gram stain), place IV ceftriaxone and adjunctive dexamethasone, document the meningeal exam, CSF interpretation, Gram stain findings, empiric regimen rationale, dexamethasone timing, and isolation precautions, then sign the encounter.",
        rubric: [
          "Review relevant labs, vitals, and clinical notes",
          "Place order: Ceftriaxone IV",
          "Place order: Dexamethasone IV",
          "Document comprehensive clinical assessment and plan",
          "Sign the encounter"
        ],
        requiredOrders: ["Ceftriaxone IV", "Dexamethasone IV"],
        requiredNoteElements: [
          "CSF analysis",
          "Meningeal signs",
          "CSF glucose-to-serum ratio",
          "Gram stain results",
          "Empiric antibiotic rationale",
          "Dexamethasone timing rationale",
          "Droplet precautions"
        ]
      }
    ]
  },

  // ── 25. Post-Operative Ileus ────────────────────────────────────────────
  {
    id: "pat-1025",
    mrn: "SYN-1025",
    fullName: "George Robinson",
    age: 67,
    sex: "M",
    allergies: ["Latex"],
    bannerFlags: ["POD 3 colectomy", "Type 2 DM"],
    summary: "Post-operative day 3 after right hemicolectomy for colon cancer. Developing abdominal distension, nausea, absent bowel sounds, no flatus.",
    encounters: [
      {
        id: "enc-1025",
        type: "Inpatient",
        reasonForVisit: "Post-operative ileus",
        provider: "Dr. Martin Hayes",
        startedAt: "2026-03-04T06:00:00.000Z",
        status: "OPEN",
        labs: [
          { id: "lab-25001", name: "Potassium", loinc: "2823-3", value: "3.1", unit: "mEq/L", referenceRange: "3.5-5.0", abnormal: true, collectedAt: "2026-03-07T06:20:00.000Z" },
          { id: "lab-25002", name: "Magnesium", loinc: "19123-9", value: "1.5", unit: "mg/dL", referenceRange: "1.7-2.2", abnormal: true, collectedAt: "2026-03-07T06:20:00.000Z" },
          { id: "lab-25003", name: "WBC", loinc: "6690-2", value: "11.8", unit: "K/uL", referenceRange: "4.0-10.5", abnormal: true, collectedAt: "2026-03-07T06:20:00.000Z" },
          { id: "lab-25004", name: "Lactate", loinc: "2524-7", value: "1.2", unit: "mmol/L", referenceRange: "0.5-2.0", abnormal: false, collectedAt: "2026-03-07T06:20:00.000Z" },
          { id: "lab-25005", name: "Glucose", loinc: "2345-7", value: "188", unit: "mg/dL", referenceRange: "70-110", abnormal: true, collectedAt: "2026-03-07T06:20:00.000Z" }
        ],
        notes: [
          { id: "note-25001", type: "PROGRESS", title: "Surgical attending note", author: "Dr. M. Hayes", content: "POD 3 right hemicolectomy for ascending colon adenocarcinoma. Developing ileus: abdomen distended, tympanitic, absent bowel sounds. No signs of anastomotic leak (afebrile, lactate normal). KUB shows dilated loops without free air. Recommend NPO, NG tube decompression, aggressive electrolyte repletion.", signed: true, createdAt: "2026-03-07T07:00:00.000Z" }
        ],
        orders: [
          { id: "ord-25001", name: "KUB X-ray", category: "IMAGING", parameters: { priority: "Urgent" }, status: "SIGNED", rationale: "Assess for obstruction vs ileus.", createdAt: "2026-03-07T06:10:00.000Z" },
          { id: "ord-25002", name: "Basic metabolic panel", category: "LAB", parameters: { priority: "STAT" }, status: "SIGNED", rationale: "Evaluate electrolytes.", createdAt: "2026-03-07T06:10:00.000Z" }
        ]
      }
    ],
    scenarios: [
      {
        id: "scn-1025",
        title: "Post-op ileus — decompression and electrolyte correction",
        objective: "As the attending physician, review post-operative labs and imaging, place NGT decompression and IV potassium repletion, document the bowel status, electrolyte plan, and NPO rationale, then sign the encounter.",
        rubric: [
          "Review relevant labs, vitals, and clinical notes",
          "Place order: Nasogastric tube placement",
          "Place order: Potassium chloride IV",
          "Document clinical assessment and plan",
          "Sign the encounter"
        ],
        requiredOrders: ["Nasogastric tube placement", "Potassium chloride IV"],
        requiredNoteElements: ["Bowel function status", "Electrolyte correction", "NPO status"]
      }
    ]
  }
];
