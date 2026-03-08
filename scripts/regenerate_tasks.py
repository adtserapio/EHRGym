#!/usr/bin/env python3
"""Regenerate all 25 task JSONs with difficulty-varied note elements.

Distribution:
  Basic  (3 notes)  — 5 tasks   (straightforward, guideline-driven)
  Medium (4-5 notes) — 10 tasks  (requires some clinical reasoning)
  Hard   (6-7 notes) — 10 tasks  (time-sensitive, multi-system, high-acuity)
"""
import json, os

TASKS_DIR = os.path.join(os.path.dirname(__file__), '..', 'tasks', 'examples')

# ──────────────────── BASIC (3 note elements) ────────────────────

tasks = [
    # ── 1. CAP (basic: stable patient, established dx, monitoring) ──
    {
        "file": "cap-pneumonia-followup.json",
        "id": "cap-pneumonia-followup",
        "title": "CAP — antibiotic stewardship and imaging follow-up",
        "patient_id": "pat-1002",
        "encounter_id": "enc-1002",
        "role": "Attending Physician",
        "objective": "As the attending physician, review the chest imaging and culture results, document the antibiotic course and respiratory status, order a follow-up chest X-ray, then sign the encounter.",
        "required_orders": ["Chest X-ray"],
        "required_note_elements": [
            "Antibiotic exposure",
            "Respiratory symptoms",
            "Follow-up plan"
        ],
        "scoring": {
            "base_reward": 1.0,
            "substeps": {
                "order:Chest X-ray": 0.20,
                "note_element:Antibiotic exposure": 0.20,
                "note_element:Respiratory symptoms": 0.15,
                "note_element:Follow-up plan": 0.15,
                "encounter_signed": 0.30
            }
        }
    },
    # ── 2. MRSA cellulitis (basic: skin infection, allergy check) ──
    {
        "file": "mrsa-cellulitis.json",
        "id": "mrsa-cellulitis",
        "title": "MRSA cellulitis — empiric coverage with allergy consideration",
        "patient_id": "pat-1014",
        "encounter_id": "enc-1014",
        "role": "Attending Physician",
        "objective": "As the attending physician, review inflammatory markers and drug allergies, place vancomycin and wound culture orders, document the MRSA risk, antibiotic choice, and allergy consideration, then sign the encounter.",
        "required_orders": ["Vancomycin IV", "Wound culture"],
        "required_note_elements": [
            "MRSA risk factors",
            "Antibiotic selection",
            "Allergy consideration"
        ],
        "scoring": {
            "base_reward": 1.0,
            "substeps": {
                "order:Vancomycin IV": 0.18,
                "order:Wound culture": 0.12,
                "note_element:MRSA risk factors": 0.15,
                "note_element:Antibiotic selection": 0.15,
                "note_element:Allergy consideration": 0.12,
                "encounter_signed": 0.28
            }
        }
    },
    # ── 3. Hip fracture (basic: clear imaging, consult, reversal) ──
    {
        "file": "hip-fracture.json",
        "id": "hip-fracture",
        "title": "Hip fracture — anticoagulation reversal for surgical clearance",
        "patient_id": "pat-1018",
        "encounter_id": "enc-1018",
        "role": "Attending Physician",
        "objective": "As the attending physician, review the fracture imaging and supratherapeutic INR, place vitamin K reversal and orthopedic consult, document the fracture type, reversal plan, and surgical disposition, then sign the encounter.",
        "required_orders": ["Vitamin K IV", "Orthopedic surgery consult"],
        "required_note_elements": [
            "Fracture type",
            "Anticoagulation reversal",
            "Surgical planning"
        ],
        "scoring": {
            "base_reward": 1.0,
            "substeps": {
                "order:Vitamin K IV": 0.18,
                "order:Orthopedic surgery consult": 0.14,
                "note_element:Fracture type": 0.15,
                "note_element:Anticoagulation reversal": 0.13,
                "note_element:Surgical planning": 0.12,
                "encounter_signed": 0.28
            }
        }
    },
    # ── 4. Post-op ileus (basic: clear post-surgical, supportive care) ──
    {
        "file": "postop-ileus.json",
        "id": "postop-ileus",
        "title": "Post-op ileus — decompression and electrolyte correction",
        "patient_id": "pat-1025",
        "encounter_id": "enc-1025",
        "role": "Attending Physician",
        "objective": "As the attending physician, review post-operative labs and imaging, place NGT decompression and IV potassium repletion, document the bowel status, electrolyte plan, and NPO rationale, then sign the encounter.",
        "required_orders": ["Nasogastric tube placement", "Potassium chloride IV"],
        "required_note_elements": [
            "Bowel function status",
            "Electrolyte correction",
            "NPO status"
        ],
        "scoring": {
            "base_reward": 1.0,
            "substeps": {
                "order:Nasogastric tube placement": 0.18,
                "order:Potassium chloride IV": 0.12,
                "note_element:Bowel function status": 0.15,
                "note_element:Electrolyte correction": 0.13,
                "note_element:NPO status": 0.12,
                "encounter_signed": 0.30
            }
        }
    },
    # ── 5. C. diff colitis (basic: guideline-driven severity & tx) ──
    {
        "file": "cdiff-colitis.json",
        "id": "cdiff-colitis",
        "title": "C. difficile colitis — severity-guided oral vancomycin",
        "patient_id": "pat-1021",
        "encounter_id": "enc-1021",
        "role": "Attending Physician",
        "objective": "As the attending physician, review C. diff PCR and severity markers (WBC, creatinine), place oral vancomycin and CT abdomen, document the severity classification, prior antibiotic exposure, and treatment plan, then sign the encounter.",
        "required_orders": ["Vancomycin oral", "CT abdomen pelvis"],
        "required_note_elements": [
            "C. diff severity",
            "Prior antibiotic exposure",
            "Oral vancomycin plan"
        ],
        "scoring": {
            "base_reward": 1.0,
            "substeps": {
                "order:Vancomycin oral": 0.18,
                "order:CT abdomen pelvis": 0.12,
                "note_element:C. diff severity": 0.18,
                "note_element:Prior antibiotic exposure": 0.12,
                "note_element:Oral vancomycin plan": 0.12,
                "encounter_signed": 0.28
            }
        }
    },

    # ──────────────────── MEDIUM (4-5 note elements) ────────────────────

    # ── 6. AKI chart review (medium: 4 notes) ──
    {
        "file": "aki-chart-review.json",
        "id": "aki-chart-review",
        "title": "AKI chart review — fluid resuscitation and renal monitoring",
        "patient_id": "pat-1001",
        "encounter_id": "enc-1001",
        "role": "Attending Physician",
        "objective": "As the attending physician, review the creatinine trend and urine output, assess volume status, place IV fluid and repeat BMP orders, document your renal assessment with differential, then sign the encounter.",
        "required_orders": ["Basic metabolic panel", "Normal saline bolus"],
        "required_note_elements": [
            "Creatinine trend",
            "Volume assessment",
            "Urine output",
            "AKI differential diagnosis"
        ],
        "scoring": {
            "base_reward": 1.0,
            "substeps": {
                "order:Normal saline bolus": 0.15,
                "order:Basic metabolic panel": 0.08,
                "note_element:Creatinine trend": 0.15,
                "note_element:Volume assessment": 0.13,
                "note_element:Urine output": 0.10,
                "note_element:AKI differential diagnosis": 0.14,
                "encounter_signed": 0.25
            }
        }
    },
    # ── 7. Upper GI bleed (medium: 5 notes) ──
    {
        "file": "upper-gi-bleed.json",
        "id": "upper-gi-bleed",
        "title": "Upper GI bleed — transfusion and acid suppression",
        "patient_id": "pat-1005",
        "encounter_id": "enc-1005",
        "role": "Attending Physician",
        "objective": "As the attending physician, review hemoglobin trend and coag panel, place PRBC transfusion and IV pantoprazole, document the bleed severity, hemodynamics, and GI consultation need, then sign the encounter.",
        "required_orders": ["Packed red blood cells", "Pantoprazole IV"],
        "required_note_elements": [
            "Hemoglobin trend",
            "Hemodynamic status",
            "Glasgow-Blatchford score",
            "Transfusion plan",
            "GI consultation indication"
        ],
        "scoring": {
            "base_reward": 1.0,
            "substeps": {
                "order:Packed red blood cells": 0.15,
                "order:Pantoprazole IV": 0.08,
                "note_element:Hemoglobin trend": 0.12,
                "note_element:Hemodynamic status": 0.10,
                "note_element:Glasgow-Blatchford score": 0.10,
                "note_element:Transfusion plan": 0.10,
                "note_element:GI consultation indication": 0.10,
                "encounter_signed": 0.25
            }
        }
    },
    # ── 8. COPD exacerbation (medium: 4 notes) ──
    {
        "file": "copd-exacerbation.json",
        "id": "copd-exacerbation",
        "title": "COPD exacerbation — systemic steroids and bronchodilators",
        "patient_id": "pat-1006",
        "encounter_id": "enc-1006",
        "role": "Attending Physician",
        "objective": "As the attending physician, review the ABG showing hypercapnic respiratory failure, place IV steroids and nebulizer, document the respiratory acidosis, ABG findings, oxygen needs, and steroid plan, then sign the encounter.",
        "required_orders": ["Methylprednisolone IV", "Albuterol nebulizer"],
        "required_note_elements": [
            "Respiratory acidosis",
            "ABG interpretation",
            "Oxygen requirements",
            "Steroid plan"
        ],
        "scoring": {
            "base_reward": 1.0,
            "substeps": {
                "order:Methylprednisolone IV": 0.15,
                "order:Albuterol nebulizer": 0.10,
                "note_element:Respiratory acidosis": 0.14,
                "note_element:ABG interpretation": 0.12,
                "note_element:Oxygen requirements": 0.10,
                "note_element:Steroid plan": 0.12,
                "encounter_signed": 0.27
            }
        }
    },
    # ── 9. Acute pancreatitis (medium: 5 notes) ──
    {
        "file": "acute-pancreatitis.json",
        "id": "acute-pancreatitis",
        "title": "Acute pancreatitis — aggressive hydration and imaging",
        "patient_id": "pat-1010",
        "encounter_id": "enc-1010",
        "role": "Attending Physician",
        "objective": "As the attending physician, review lipase and severity markers, place aggressive fluid resuscitation and CT imaging, document the etiology workup, severity scoring, and nutrition plan, then sign the encounter.",
        "required_orders": ["Lactated Ringer bolus", "CT abdomen with contrast"],
        "required_note_elements": [
            "Lipase elevation",
            "Gallstone evaluation",
            "Ranson criteria",
            "Fluid management",
            "NPO and nutrition plan"
        ],
        "scoring": {
            "base_reward": 1.0,
            "substeps": {
                "order:Lactated Ringer bolus": 0.13,
                "order:CT abdomen with contrast": 0.10,
                "note_element:Lipase elevation": 0.12,
                "note_element:Gallstone evaluation": 0.10,
                "note_element:Ranson criteria": 0.10,
                "note_element:Fluid management": 0.10,
                "note_element:NPO and nutrition plan": 0.10,
                "encounter_signed": 0.25
            }
        }
    },
    # ── 10. Hyperkalemia (medium: 4 notes) ──
    {
        "file": "hyperkalemia.json",
        "id": "hyperkalemia",
        "title": "Hyperkalemia — emergent cardiac stabilization",
        "patient_id": "pat-1015",
        "encounter_id": "enc-1015",
        "role": "Attending Physician",
        "objective": "As the attending physician, review potassium and ECG, place emergent calcium gluconate and insulin-dextrose, document the potassium level, ECG changes, and management cascade, then sign the encounter.",
        "required_orders": ["Calcium gluconate IV", "Insulin and dextrose IV"],
        "required_note_elements": [
            "Potassium level",
            "ECG changes",
            "Emergent management",
            "Potassium shifting agents"
        ],
        "scoring": {
            "base_reward": 1.0,
            "substeps": {
                "order:Calcium gluconate IV": 0.18,
                "order:Insulin and dextrose IV": 0.12,
                "note_element:Potassium level": 0.12,
                "note_element:ECG changes": 0.12,
                "note_element:Emergent management": 0.10,
                "note_element:Potassium shifting agents": 0.10,
                "encounter_signed": 0.26
            }
        }
    },
    # ── 11. Hepatic encephalopathy (medium: 5 notes) ──
    {
        "file": "hepatic-encephalopathy.json",
        "id": "hepatic-encephalopathy",
        "title": "Hepatic encephalopathy — lactulose titration and rifaximin",
        "patient_id": "pat-1016",
        "encounter_id": "enc-1016",
        "role": "Attending Physician",
        "objective": "As the attending physician, review ammonia and hepatic function, place lactulose and rifaximin, document the encephalopathy grading, precipitant, and titration goals, then sign the encounter.",
        "required_orders": ["Lactulose oral", "Rifaximin oral"],
        "required_note_elements": [
            "Ammonia level",
            "Mental status changes",
            "West Haven grade",
            "Precipitant identification",
            "Lactulose plan"
        ],
        "scoring": {
            "base_reward": 1.0,
            "substeps": {
                "order:Lactulose oral": 0.14,
                "order:Rifaximin oral": 0.09,
                "note_element:Ammonia level": 0.12,
                "note_element:Mental status changes": 0.10,
                "note_element:West Haven grade": 0.10,
                "note_element:Precipitant identification": 0.12,
                "note_element:Lactulose plan": 0.10,
                "encounter_signed": 0.23
            }
        }
    },
    # ── 12. Alcohol withdrawal (medium: 5 notes) ──
    {
        "file": "alcohol-withdrawal.json",
        "id": "alcohol-withdrawal",
        "title": "Alcohol withdrawal — CIWA-guided benzodiazepine protocol",
        "patient_id": "pat-1020",
        "encounter_id": "enc-1020",
        "role": "Attending Physician",
        "objective": "As the attending physician, review CIWA score and seizure history, place lorazepam and IV thiamine, document the withdrawal severity, benzodiazepine plan, and DT risk, then sign the encounter.",
        "required_orders": ["Lorazepam IV", "Thiamine IV"],
        "required_note_elements": [
            "CIWA score",
            "Seizure history",
            "Last drink timing",
            "Benzodiazepine plan",
            "Delirium tremens risk"
        ],
        "scoring": {
            "base_reward": 1.0,
            "substeps": {
                "order:Lorazepam IV": 0.14,
                "order:Thiamine IV": 0.09,
                "note_element:CIWA score": 0.12,
                "note_element:Seizure history": 0.10,
                "note_element:Last drink timing": 0.10,
                "note_element:Benzodiazepine plan": 0.12,
                "note_element:Delirium tremens risk": 0.10,
                "encounter_signed": 0.23
            }
        }
    },
    # ── 13. Sickle cell crisis (medium: 5 notes) ──
    {
        "file": "sickle-cell-crisis.json",
        "id": "sickle-cell-crisis",
        "title": "Sickle cell VOC — pain management and ACS screening",
        "patient_id": "pat-1023",
        "encounter_id": "enc-1023",
        "role": "Attending Physician",
        "objective": "As the attending physician, review hemolysis markers and hemoglobin, place hydromorphone PCA (noting morphine allergy) and CXR for ACS screening, document the pain assessment, ACS evaluation, and transfusion threshold, then sign the encounter.",
        "required_orders": ["Hydromorphone PCA", "Chest X-ray"],
        "required_note_elements": [
            "Hemoglobin baseline",
            "Pain assessment",
            "Acute chest syndrome screening",
            "Morphine allergy and opioid selection",
            "Transfusion threshold"
        ],
        "scoring": {
            "base_reward": 1.0,
            "substeps": {
                "order:Hydromorphone PCA": 0.14,
                "order:Chest X-ray": 0.09,
                "note_element:Hemoglobin baseline": 0.10,
                "note_element:Pain assessment": 0.12,
                "note_element:Acute chest syndrome screening": 0.12,
                "note_element:Morphine allergy and opioid selection": 0.10,
                "note_element:Transfusion threshold": 0.10,
                "encounter_signed": 0.23
            }
        }
    },
    # ── 14. CHF exacerbation (medium: 5 notes) ──
    {
        "file": "chf-exacerbation.json",
        "id": "chf-exacerbation",
        "title": "CHF exacerbation — IV diuresis and volume management",
        "patient_id": "pat-1007",
        "encounter_id": "enc-1007",
        "role": "Attending Physician",
        "objective": "As the attending physician, review BNP, electrolytes, and daily weights, place IV furosemide and renal monitoring, document the volume overload assessment and diuresis strategy, then sign the encounter.",
        "required_orders": ["Furosemide IV", "Basic metabolic panel"],
        "required_note_elements": [
            "Volume status",
            "BNP level",
            "Daily weight trend",
            "Ejection fraction",
            "Diuretic plan"
        ],
        "scoring": {
            "base_reward": 1.0,
            "substeps": {
                "order:Furosemide IV": 0.15,
                "order:Basic metabolic panel": 0.07,
                "note_element:Volume status": 0.13,
                "note_element:BNP level": 0.10,
                "note_element:Daily weight trend": 0.10,
                "note_element:Ejection fraction": 0.10,
                "note_element:Diuretic plan": 0.12,
                "encounter_signed": 0.23
            }
        }
    },
    # ── 15. PE workup (medium: 5 notes) ──
    {
        "file": "pe-workup.json",
        "id": "pe-workup",
        "title": "PE — diagnostic imaging and empiric anticoagulation",
        "patient_id": "pat-1008",
        "encounter_id": "enc-1008",
        "role": "Attending Physician",
        "objective": "As the attending physician, review D-dimer and Wells criteria, place CTA chest and heparin drip, document the PE probability, hemodynamics, and anticoagulation rationale, then sign the encounter.",
        "required_orders": ["CT angiography chest", "Heparin drip"],
        "required_note_elements": [
            "D-dimer elevation",
            "Wells score",
            "Hypoxia evaluation",
            "Right heart strain",
            "Anticoagulation plan"
        ],
        "scoring": {
            "base_reward": 1.0,
            "substeps": {
                "order:CT angiography chest": 0.13,
                "order:Heparin drip": 0.13,
                "note_element:D-dimer elevation": 0.10,
                "note_element:Wells score": 0.12,
                "note_element:Hypoxia evaluation": 0.10,
                "note_element:Right heart strain": 0.10,
                "note_element:Anticoagulation plan": 0.10,
                "encounter_signed": 0.22
            }
        }
    },

    # ──────────────────── HARD (6-7 note elements) ────────────────────

    # ── 16. DKA management (hard: 7 notes) ──
    {
        "file": "dka-management.json",
        "id": "dka-management",
        "title": "DKA — insulin protocol and anion-gap monitoring",
        "patient_id": "pat-1003",
        "encounter_id": "enc-1003",
        "role": "Attending Physician",
        "objective": "As the attending physician, review the metabolic panel (glucose, anion gap, pH, bicarbonate), start an insulin drip with serial BMP monitoring, document the DKA severity, precipitant workup, fluid and insulin management, potassium monitoring, and gap closure criteria, then sign the encounter.",
        "required_orders": ["Insulin drip", "Basic metabolic panel"],
        "required_note_elements": [
            "Anion gap",
            "Blood glucose level",
            "Serum bicarbonate",
            "Fluid resuscitation",
            "Insulin management",
            "DKA precipitant",
            "Potassium monitoring"
        ],
        "scoring": {
            "base_reward": 1.0,
            "substeps": {
                "order:Insulin drip": 0.14,
                "order:Basic metabolic panel": 0.05,
                "note_element:Anion gap": 0.10,
                "note_element:Blood glucose level": 0.08,
                "note_element:Serum bicarbonate": 0.08,
                "note_element:Fluid resuscitation": 0.09,
                "note_element:Insulin management": 0.10,
                "note_element:DKA precipitant": 0.09,
                "note_element:Potassium monitoring": 0.08,
                "encounter_signed": 0.19
            }
        }
    },
    # ── 17. Acute coronary syndrome (hard: 7 notes) ──
    {
        "file": "acute-coronary-syndrome.json",
        "id": "acute-coronary-syndrome",
        "title": "STEMI — anticoagulation and cardiac workup",
        "patient_id": "pat-1004",
        "encounter_id": "enc-1004",
        "role": "Attending Physician",
        "objective": "As the attending physician, review serial troponins and ECG findings, place heparin drip and echocardiogram, document the full ACS assessment including risk stratification, ECG interpretation, antiplatelet and anticoagulation rationale, and cardiology consultation, then sign the encounter.",
        "required_orders": ["Heparin drip", "Echocardiogram"],
        "required_note_elements": [
            "Troponin trend",
            "ECG interpretation",
            "ST elevation",
            "Chest pain characterization",
            "TIMI risk score",
            "Antiplatelet therapy",
            "Cardiology consultation"
        ],
        "scoring": {
            "base_reward": 1.0,
            "substeps": {
                "order:Heparin drip": 0.13,
                "order:Echocardiogram": 0.05,
                "note_element:Troponin trend": 0.10,
                "note_element:ECG interpretation": 0.10,
                "note_element:ST elevation": 0.08,
                "note_element:Chest pain characterization": 0.08,
                "note_element:TIMI risk score": 0.09,
                "note_element:Antiplatelet therapy": 0.09,
                "note_element:Cardiology consultation": 0.08,
                "encounter_signed": 0.20
            }
        }
    },
    # ── 18. Urosepsis (hard: 7 notes) ──
    {
        "file": "urosepsis.json",
        "id": "urosepsis",
        "title": "Urosepsis — SEP-1 bundle compliance",
        "patient_id": "pat-1009",
        "encounter_id": "enc-1009",
        "role": "Attending Physician",
        "objective": "As the attending physician, review lactate, urinalysis, and blood cultures, place empiric IV antibiotics and fluid resuscitation within the SEP-1 bundle, document the full sepsis workup including source, bundle timing, hemodynamic response, and reassessment, then sign the encounter.",
        "required_orders": ["Ceftriaxone IV", "Normal saline bolus"],
        "required_note_elements": [
            "Sepsis criteria",
            "Lactate level",
            "Source identification",
            "Blood culture timing",
            "Hemodynamic response to fluids",
            "Antibiotic selection rationale",
            "Reassessment plan"
        ],
        "scoring": {
            "base_reward": 1.0,
            "substeps": {
                "order:Ceftriaxone IV": 0.12,
                "order:Normal saline bolus": 0.07,
                "note_element:Sepsis criteria": 0.10,
                "note_element:Lactate level": 0.09,
                "note_element:Source identification": 0.09,
                "note_element:Blood culture timing": 0.08,
                "note_element:Hemodynamic response to fluids": 0.09,
                "note_element:Antibiotic selection rationale": 0.09,
                "note_element:Reassessment plan": 0.08,
                "encounter_signed": 0.19
            }
        }
    },
    # ── 19. New-onset AFib (hard: 6 notes) ──
    {
        "file": "new-onset-afib.json",
        "id": "new-onset-afib",
        "title": "New-onset AFib with RVR — rate control and stroke risk",
        "patient_id": "pat-1011",
        "encounter_id": "enc-1011",
        "role": "Attending Physician",
        "objective": "As the attending physician, review electrolytes, thyroid function, and telemetry, place IV diltiazem and potassium repletion, document the rhythm analysis, CHA2DS2-VASc score, rate control strategy, and anticoagulation decision, then sign the encounter.",
        "required_orders": ["Diltiazem IV", "Potassium chloride IV"],
        "required_note_elements": [
            "Heart rate",
            "Rhythm interpretation",
            "CHA2DS2-VASc score",
            "Rate control strategy",
            "Anticoagulation decision",
            "Hemodynamic stability"
        ],
        "scoring": {
            "base_reward": 1.0,
            "substeps": {
                "order:Diltiazem IV": 0.13,
                "order:Potassium chloride IV": 0.05,
                "note_element:Heart rate": 0.09,
                "note_element:Rhythm interpretation": 0.10,
                "note_element:CHA2DS2-VASc score": 0.12,
                "note_element:Rate control strategy": 0.12,
                "note_element:Anticoagulation decision": 0.12,
                "note_element:Hemodynamic stability": 0.08,
                "encounter_signed": 0.19
            }
        }
    },
    # ── 20. Hyponatremia workup (hard: 7 notes) ──
    {
        "file": "hyponatremia-workup.json",
        "id": "hyponatremia-workup",
        "title": "Severe hyponatremia — SIADH diagnosis and safe correction",
        "patient_id": "pat-1012",
        "encounter_id": "enc-1012",
        "role": "Attending Physician",
        "objective": "As the attending physician, review sodium, serum and urine osmolality, and urine sodium, place hypertonic saline with serial BMP monitoring, document the hyponatremia classification, SIADH diagnostic criteria, and safe correction rate plan with osmotic demyelination risk, then sign the encounter.",
        "required_orders": ["Sodium chloride 3% IV", "Basic metabolic panel"],
        "required_note_elements": [
            "Sodium level",
            "Serum osmolality",
            "Urine osmolality",
            "Urine sodium",
            "Volume status classification",
            "SIADH assessment",
            "Correction rate goal"
        ],
        "scoring": {
            "base_reward": 1.0,
            "substeps": {
                "order:Sodium chloride 3% IV": 0.12,
                "order:Basic metabolic panel": 0.05,
                "note_element:Sodium level": 0.09,
                "note_element:Serum osmolality": 0.09,
                "note_element:Urine osmolality": 0.08,
                "note_element:Urine sodium": 0.08,
                "note_element:Volume status classification": 0.09,
                "note_element:SIADH assessment": 0.11,
                "note_element:Correction rate goal": 0.10,
                "encounter_signed": 0.19
            }
        }
    },
    # ── 21. Acute ischemic stroke (hard: 7 notes) ──
    {
        "file": "acute-ischemic-stroke.json",
        "id": "acute-ischemic-stroke",
        "title": "Acute ischemic stroke — thrombolysis decision",
        "patient_id": "pat-1013",
        "encounter_id": "enc-1013",
        "role": "Attending Physician",
        "objective": "As the attending physician, review CT head, INR, platelets, and glucose, assess tPA eligibility, place alteplase and CTA orders, document the NIHSS, time last known well, contraindication screen, eligibility determination, BP management, and neurology consultation, then sign the encounter.",
        "required_orders": ["Alteplase IV", "CT angiography head and neck"],
        "required_note_elements": [
            "NIHSS score",
            "Time last known well",
            "CT head interpretation",
            "tPA contraindication screen",
            "tPA eligibility",
            "Blood pressure management",
            "Neurology consultation"
        ],
        "scoring": {
            "base_reward": 1.0,
            "substeps": {
                "order:Alteplase IV": 0.16,
                "order:CT angiography head and neck": 0.05,
                "note_element:NIHSS score": 0.09,
                "note_element:Time last known well": 0.10,
                "note_element:CT head interpretation": 0.08,
                "note_element:tPA contraindication screen": 0.10,
                "note_element:tPA eligibility": 0.09,
                "note_element:Blood pressure management": 0.08,
                "note_element:Neurology consultation": 0.06,
                "encounter_signed": 0.19
            }
        }
    },
    # ── 22. Anaphylaxis (hard: 6 notes) ──
    {
        "file": "anaphylaxis.json",
        "id": "anaphylaxis",
        "title": "Anaphylaxis — epinephrine infusion and allergen documentation",
        "patient_id": "pat-1017",
        "encounter_id": "enc-1017",
        "role": "Attending Physician",
        "objective": "As the attending physician, review tryptase and vital sign trajectory, place epinephrine infusion and IV steroids, document the anaphylaxis diagnostic criteria, causative agent, airway assessment, epinephrine dosing, hemodynamic response, and biphasic reaction monitoring plan, then sign the encounter.",
        "required_orders": ["Epinephrine IV drip", "Methylprednisolone IV"],
        "required_note_elements": [
            "Causative agent",
            "Anaphylaxis criteria",
            "Epinephrine administration",
            "Airway assessment",
            "Hemodynamic response",
            "Biphasic reaction monitoring"
        ],
        "scoring": {
            "base_reward": 1.0,
            "substeps": {
                "order:Epinephrine IV drip": 0.17,
                "order:Methylprednisolone IV": 0.05,
                "note_element:Causative agent": 0.10,
                "note_element:Anaphylaxis criteria": 0.10,
                "note_element:Epinephrine administration": 0.12,
                "note_element:Airway assessment": 0.10,
                "note_element:Hemodynamic response": 0.08,
                "note_element:Biphasic reaction monitoring": 0.08,
                "encounter_signed": 0.20
            }
        }
    },
    # ── 23. Asthma exacerbation (hard: 6 notes) ──
    {
        "file": "asthma-exacerbation.json",
        "id": "asthma-exacerbation",
        "title": "Severe asthma — IV magnesium and systemic steroids",
        "patient_id": "pat-1019",
        "encounter_id": "enc-1019",
        "role": "Attending Physician",
        "objective": "As the attending physician, review ABG (noting ominous normal pCO2), peak flow, and accessory muscle use, place IV magnesium and systemic steroids, document the severity classification, bronchodilator response, intubation readiness, and ICU escalation criteria, then sign the encounter.",
        "required_orders": ["Magnesium sulfate IV", "Methylprednisolone IV"],
        "required_note_elements": [
            "Peak flow",
            "ABG with pCO2 interpretation",
            "Accessory muscle use",
            "Steroid therapy",
            "Bronchodilator response",
            "Intubation readiness"
        ],
        "scoring": {
            "base_reward": 1.0,
            "substeps": {
                "order:Magnesium sulfate IV": 0.12,
                "order:Methylprednisolone IV": 0.12,
                "note_element:Peak flow": 0.09,
                "note_element:ABG with pCO2 interpretation": 0.10,
                "note_element:Accessory muscle use": 0.08,
                "note_element:Steroid therapy": 0.09,
                "note_element:Bronchodilator response": 0.09,
                "note_element:Intubation readiness": 0.10,
                "encounter_signed": 0.21
            }
        }
    },
    # ── 24. Thyroid storm (hard: 6 notes) ──
    {
        "file": "thyroid-storm.json",
        "id": "thyroid-storm",
        "title": "Thyroid storm — multi-drug thyroid blockade and rate control",
        "patient_id": "pat-1022",
        "encounter_id": "enc-1022",
        "role": "Attending Physician",
        "objective": "As the attending physician, review TSH, free T4/T3, and vital sign instability, place PTU and IV propranolol for dual blockade and rate control, document the Burch-Wartofsky score, anti-thyroid therapy, rate control rationale, temperature management, and precipitant, then sign the encounter.",
        "required_orders": ["Propylthiouracil oral", "Propranolol IV"],
        "required_note_elements": [
            "Thyroid hormone levels",
            "Burch-Wartofsky score",
            "Anti-thyroid therapy",
            "Beta-blocker rationale",
            "Temperature management",
            "Precipitating event"
        ],
        "scoring": {
            "base_reward": 1.0,
            "substeps": {
                "order:Propylthiouracil oral": 0.12,
                "order:Propranolol IV": 0.12,
                "note_element:Thyroid hormone levels": 0.10,
                "note_element:Burch-Wartofsky score": 0.11,
                "note_element:Anti-thyroid therapy": 0.09,
                "note_element:Beta-blocker rationale": 0.08,
                "note_element:Temperature management": 0.08,
                "note_element:Precipitating event": 0.09,
                "encounter_signed": 0.21
            }
        }
    },
    # ── 25. Bacterial meningitis (hard: 7 notes) ──
    {
        "file": "bacterial-meningitis.json",
        "id": "bacterial-meningitis",
        "title": "Bacterial meningitis — empiric antibiotics and adjunctive steroids",
        "patient_id": "pat-1024",
        "encounter_id": "enc-1024",
        "role": "Attending Physician",
        "objective": "As the attending physician, review CSF analysis (cell count, glucose, protein, Gram stain), place IV ceftriaxone and adjunctive dexamethasone, document the meningeal exam, CSF interpretation, Gram stain findings, empiric regimen rationale, dexamethasone timing, and isolation precautions, then sign the encounter.",
        "required_orders": ["Ceftriaxone IV", "Dexamethasone IV"],
        "required_note_elements": [
            "CSF analysis",
            "Meningeal signs",
            "CSF glucose-to-serum ratio",
            "Gram stain results",
            "Empiric antibiotic rationale",
            "Dexamethasone timing rationale",
            "Droplet precautions"
        ],
        "scoring": {
            "base_reward": 1.0,
            "substeps": {
                "order:Ceftriaxone IV": 0.14,
                "order:Dexamethasone IV": 0.06,
                "note_element:CSF analysis": 0.10,
                "note_element:Meningeal signs": 0.09,
                "note_element:CSF glucose-to-serum ratio": 0.08,
                "note_element:Gram stain results": 0.08,
                "note_element:Empiric antibiotic rationale": 0.09,
                "note_element:Dexamethasone timing rationale": 0.08,
                "note_element:Droplet precautions": 0.08,
                "encounter_signed": 0.20
            }
        }
    }
]


def main():
    difficulty_map = {}
    for task in tasks:
        fn = task.pop("file")
        path = os.path.join(TASKS_DIR, fn)
        subs = task["scoring"]["substeps"]
        total = round(sum(subs.values()), 2)
        assert total == 1.0, f"{fn}: weights sum to {total}, not 1.0"
        for o in task["required_orders"]:
            assert f"order:{o}" in subs, f"{fn}: missing substep for order:{o}"
        for e in task["required_note_elements"]:
            assert f"note_element:{e}" in subs, f"{fn}: missing substep for note_element:{e}"
        assert "encounter_signed" in subs, f"{fn}: missing encounter_signed"
        with open(path, "w") as f:
            json.dump(task, f, indent=2)
            f.write("\n")
        n = len(task["required_note_elements"])
        diff = "BASIC" if n <= 3 else ("MEDIUM" if n <= 5 else "HARD")
        difficulty_map.setdefault(diff, []).append(fn)
        print(f"  [{diff:6s}] {fn:40s} notes={n} substeps={len(subs)} sum={total:.2f}")

    print(f"\nWrote {len(tasks)} task files.")
    for d in ["BASIC", "MEDIUM", "HARD"]:
        items = difficulty_map.get(d, [])
        print(f"  {d}: {len(items)} tasks")


if __name__ == "__main__":
    main()
