#!/usr/bin/env python3
"""
Generate synthetic action bundles (rollouts) for all 25 tasks.

Each rollout creates a deterministic action sequence that:
1. Clicks the patient card from the dashboard
2. Navigates to Notes, writes a clinically appropriate SOAP note
   mentioning all required note elements
3. Navigates to Orders, places each required order
4. Signs the encounter

Output: tasks/examples/<task-id>-actions.json for each task.
"""

import json
import glob
import os
import textwrap
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TASKS_DIR = ROOT / "tasks" / "examples"
SEED_FILE = ROOT / "shared" / "seed-data.ts"

# ── Clinically realistic SOAP note templates per task ──
# Each maps task_id -> { subjective, objective_note, assessment, plan }
# Note elements are woven naturally into the text so the rubric matcher finds them.

SOAP_TEMPLATES: dict[str, dict[str, str]] = {
    "aki-chart-review": {
        "S": "Patient reports decreased oral intake over past 3 days, feeling weak and lightheaded. Denies dysuria, hematuria, or flank pain.",
        "O": "Creatinine trend: 0.9 -> 1.4 -> 2.3 over 48 hours. Urine output 15 mL/hr over last 6 hours. BUN/Cr ratio elevated. Volume assessment: mucous membranes dry, skin tenting present, orthostatic positive. No peripheral edema.",
        "A": "AKI stage 2 (KDIGO), likely prerenal. AKI differential diagnosis includes prerenal azotemia (most likely given volume depletion), ATN, and obstructive causes. FENa pending.",
        "P": "IV normal saline bolus 1L now, then 125 mL/hr. Repeat basic metabolic panel in 4-6 hours. Strict I/Os. Hold nephrotoxins. Renal consult if no improvement in 24 hours."
    },
    "cap-pneumonia-followup": {
        "S": "Patient reports improved cough, less sputum production. Still with mild dyspnea on exertion. Tolerating PO antibiotics.",
        "O": "Antibiotic exposure: completed 48 hours of IV ceftriaxone/azithromycin, transitioned to PO amoxicillin-clavulanate. Respiratory symptoms: RR 18, SpO2 96% on RA, diminished breath sounds at right base. Temp 37.2.",
        "A": "Community-acquired pneumonia, improving on appropriate antibiotic therapy. Clinical response adequate at 48 hours.",
        "P": "Chest X-ray to assess interval change. Follow-up plan: complete 5-day total antibiotic course. If continued improvement, discharge with PO antibiotics and PCP follow-up in 1 week."
    },
    "dka-management": {
        "S": "Patient brought in by family, confused and vomiting for 2 days. Missed insulin doses. Reports polyuria and polydipsia.",
        "O": "Blood glucose level 487 mg/dL. Anion gap 28 (Na 138 - Cl 98 - HCO3 12). Serum bicarbonate 12 mEq/L. pH 7.18 on VBG. Potassium 5.2 (likely spurious in setting of acidosis). Phosphate low. Ketones large in urine and serum.",
        "A": "DKA, severe (pH <7.2, bicarb <15, anion gap >25). DKA precipitant: medication non-compliance, assess for infection. Potassium monitoring critical as insulin will shift K intracellularly.",
        "P": "Insulin drip per DKA protocol (0.1 units/kg/hr after bolus). Fluid resuscitation: NS 1L bolus then 500 mL/hr. Basic metabolic panel q2h. Potassium chloride 20 mEq in each liter when K <5.0. Insulin management: transition to subQ when anion gap closes and patient tolerating PO. Monitor for cerebral edema."
    },
    "acute-coronary-syndrome": {
        "S": "Patient reports crushing substernal chest pain radiating to left arm, onset 2 hours ago at rest. Associated diaphoresis, nausea. Pain 8/10. Not relieved by rest.",
        "O": "Troponin trend: 0.04 -> 2.8 -> 8.1 ng/mL (rising). ECG interpretation: ST elevation in leads II, III, aVF consistent with inferior MI. ST elevation >2mm in inferior leads. BP 108/72, HR 88, SpO2 97%. Chest pain characterization: typical angina with high-risk features.",
        "A": "STEMI, inferior wall. TIMI risk score 5/7 (high risk). Cardiology consultation requested emergently for primary PCI.",
        "P": "Heparin drip per ACS protocol. Antiplatelet therapy: aspirin 325mg and clopidogrel 600mg load given. Echocardiogram to assess wall motion and EF. NPO for potential cath. IV access x2. Continuous telemetry. Cardiology consultation for emergent catheterization."
    },
    "upper-gi-bleed": {
        "S": "Patient reports 3 episodes of hematemesis (coffee-ground emesis) and 2 melanotic stools since yesterday. Feels dizzy when standing.",
        "O": "Hemoglobin trend: 10.2 -> 8.1 -> 7.4 g/dL over 12 hours. Hemodynamic status: HR 112, BP 92/58, orthostatic positive. Lactate 2.8. Glasgow-Blatchford score 14 (high risk, requires intervention). INR 1.1, platelets 185K.",
        "A": "Acute upper GI hemorrhage with hemodynamic instability. Transfusion plan: transfuse below Hgb 7 threshold, target 7-9 g/dL. GI consultation indication: high Blatchford score, hemodynamic instability, and active bleeding require urgent endoscopy.",
        "P": "Packed red blood cells 2 units, crossmatched and transfusing now. Pantoprazole IV 80mg bolus then 8mg/hr continuous infusion. NPO for EGD. Two large-bore IVs. Type and screen x4 units. GI consultation placed for urgent EGD."
    },
    "copd-exacerbation": {
        "S": "Patient reports worsening dyspnea over 3 days, increased sputum production and purulence. Using home nebulizer without relief. Smoked 40 pack-years, quit 2 years ago.",
        "O": "ABG interpretation: pH 7.30, pCO2 55, pO2 58, HCO3 27 — acute on chronic respiratory acidosis. Oxygen requirements: 3L NC to maintain SpO2 89-92%. RR 24, accessory muscle use noted. CXR with hyperinflation, no consolidation.",
        "A": "Acute COPD exacerbation with respiratory acidosis. Likely infectious trigger given purulent sputum.",
        "P": "Methylprednisolone IV 125mg now, then 60mg q6h. Albuterol nebulizer q4h standing + q2h PRN. Azithromycin for infectious trigger. Steroid plan: IV x 48h then transition to PO prednisone 40mg taper. BIPAP if worsening hypercapnia. ICU transfer if respiratory failure."
    },
    "chf-exacerbation": {
        "S": "Patient reports progressive dyspnea on exertion over 1 week, now short of breath at rest. Three-pillow orthopnea, PND. Gained 8 lbs in 5 days. Ate high-sodium foods. Missed 2 days of diuretics.",
        "O": "BNP level 1840 pg/mL (baseline 200). Volume status: JVP elevated to 14 cm, 2+ bilateral lower extremity edema, bibasilar crackles. Daily weight trend: 85 -> 87 -> 89 -> 92 kg. Ejection fraction 25% on last echo (6 months ago). SpO2 91% on 2L NC.",
        "A": "Acute decompensated heart failure, NYHA class IV. Triggered by dietary indiscretion and medication non-adherence. Diuretic plan: aggressive IV diuresis targeting 1-2L net negative per day.",
        "P": "Furosemide IV 80mg bolus now (2x home dose), then 40mg IV q8h. Basic metabolic panel q12h for electrolyte monitoring. Strict I/Os, daily weights. Fluid restrict 1.5L/day. Sodium restrict <2g/day. Resume home ACEi and BB once euvolemic. Echo if not improving."
    },
    "pe-workup": {
        "S": "Patient reports sudden-onset pleuritic chest pain and dyspnea since this morning. Recent 12-hour flight 5 days ago. No calf swelling noticed.",
        "O": "D-dimer elevation: 4200 ng/mL (normal <500). Wells score: 6 (recent travel, HR>100, clinical signs of DVT absent, PE most likely diagnosis). Hypoxia evaluation: SpO2 91% on RA, ABG pO2 62. HR 108. Right heart strain: troponin mildly elevated at 0.08, BNP 340.",
        "A": "Acute pulmonary embolism, confirmed. Submassive PE given RV strain markers. Anticoagulation plan: systemic anticoagulation indicated; no contraindications identified.",
        "P": "CT angiography chest confirmed bilateral PE. Heparin drip per PE protocol with target aPTT 60-80. Echocardiogram to evaluate RV function. Transition to DOAC upon clinical stability. IVC filter discussion if anticoagulation contraindicated. Monitor for hemodynamic deterioration."
    },
    "urosepsis": {
        "S": "Patient from nursing facility, found confused and febrile. Staff reports foul-smelling urine and decreased intake. History of recurrent UTIs and indwelling catheter.",
        "O": "Sepsis criteria: SIRS-positive (temp 39.2, HR 118, WBC 18.4). Lactate level 4.2 mmol/L. Source identification: UA with >100 WBC, nitrite positive, leukocyte esterase 3+. Blood culture timing: 2 sets drawn prior to antibiotics. Hemodynamic response to fluids: MAP improved from 58 to 68 after 1L bolus.",
        "A": "Urosepsis with septic shock (lactate >4 despite fluids). Antibiotic selection rationale: ceftriaxone IV for empiric gram-negative coverage, broad-spectrum appropriate given nursing facility residence and catheter. Reassessment plan: repeat lactate in 4 hours, assess fluid responsiveness.",
        "P": "Ceftriaxone IV 2g now. Normal saline bolus 30 mL/kg (2L total). Norepinephrine if MAP <65 after fluids. Repeat lactate q4h. Foley catheter change. Urine and blood cultures pending. Reassessment plan: 6-hour sepsis bundle compliance check."
    },
    "acute-pancreatitis": {
        "S": "Patient reports severe epigastric pain radiating to the back, onset after a large meal with alcohol. Nausea with multiple episodes of vomiting. Unable to eat.",
        "O": "Lipase elevation: 1840 U/L (>3x ULN). Gallstone evaluation: RUQ ultrasound shows cholelithiasis without CBD dilation. ALT mildly elevated. Ranson criteria at admission: WBC 14.2, glucose 220, age >55 = 3 criteria (moderate severity). Calcium 8.1, LDH 350.",
        "A": "Acute gallstone pancreatitis, moderate severity by Ranson criteria. Fluid management is priority to prevent pancreatic necrosis. NPO and nutrition plan: NPO initially, advance to low-fat diet as pain improves and lipase trends down.",
        "P": "Lactated Ringer bolus 1L now, then 250 mL/hr aggressive hydration. CT abdomen with contrast to evaluate for necrosis or complications. Pain control with IV hydromorphone. NPO and nutrition plan: advance diet as tolerated. Surgical consult for cholecystectomy during this admission once pancreatitis resolves."
    },
    "new-onset-afib": {
        "S": "Patient reports palpitations, chest fluttering, and mild dizziness since yesterday. No syncope, chest pain, or dyspnea at rest. No prior history of arrhythmia.",
        "O": "Heart rate 148 bpm, irregular. Rhythm interpretation: 12-lead ECG shows atrial fibrillation with rapid ventricular response, no ST changes. BP 128/82. CHA2DS2-VASc score: 4 (age 71, female, HTN, DM). TSH normal. K+ 3.2 (low). Mg 1.6 (low).",
        "A": "New-onset atrial fibrillation with RVR. Hemodynamic stability: hemodynamically stable with preserved BP. Rate control strategy: IV diltiazem preferred given normal EF and no severe asthma. Anticoagulation decision: CHA2DS2-VASc 4 — anticoagulation strongly indicated for stroke prevention.",
        "P": "Diltiazem IV 20mg bolus, then 10mg/hr drip titrated to HR <110. Potassium chloride IV 40 mEq for repletion. MgSO4 2g IV. Echocardiogram to assess EF and LA size. Start apixaban 5mg BID once rate controlled. Continuous telemetry."
    },
    "hyponatremia-workup": {
        "S": "Patient reports 4 days of progressive confusion, headache, and nausea. Family notes increasing lethargy. No recent medication changes. Decreased fluid intake.",
        "O": "Sodium level 118 mEq/L. Serum osmolality 248 mOsm/kg (hypotonic). Urine osmolality 580 mOsm/kg (inappropriately concentrated). Urine sodium 45 mEq/L (elevated). Volume status classification: euvolemic — no edema, no signs of dehydration, normal JVP. SIADH assessment: meets criteria (euvolemic hypotonic hyponatremia with inappropriately concentrated urine and elevated urine sodium, TSH and cortisol normal).",
        "A": "Severe symptomatic hypotonic hyponatremia secondary to SIADH. CT head negative for mass. Correction rate goal: raise sodium no more than 8 mEq/L in first 24 hours to prevent osmotic demyelination syndrome.",
        "P": "Sodium chloride 3% IV at 30 mL/hr. Basic metabolic panel q4h for sodium monitoring. Correction rate goal: target Na 124-126 by 24 hours. Fluid restriction 1L/day. Desmopressin rescue available if overcorrection. Neurology consult for altered mental status."
    },
    "acute-ischemic-stroke": {
        "S": "Patient brought by EMS with sudden-onset right-sided weakness and difficulty speaking. Wife witnessed onset at 14:30, called 911 immediately.",
        "O": "NIHSS score 14 (moderate-severe deficit). Time last known well: 90 minutes ago. CT head interpretation: no hemorrhage, no early ischemic changes, ASPECTS 9. INR 1.0, platelets 210K, glucose 142. tPA contraindication screen: no recent surgery, no bleeding, no anticoagulation, no prior ICH. tPA eligibility: eligible — within 4.5-hour window, NIHSS >4, no exclusion criteria. Blood pressure management: BP 172/94, acceptable for thrombolysis (below 185/110).",
        "A": "Acute ischemic stroke, left MCA territory. Patient is tPA eligible. Neurology consultation: neurology at bedside, agrees with thrombolysis.",
        "P": "Alteplase IV 0.9 mg/kg (10% bolus, 90% over 60 min). CT angiography head and neck for large vessel occlusion evaluation. BP monitoring q15 min during infusion. Admit to neuro ICU. Hold anticoagulation and antiplatelets for 24 hours. Repeat CT head at 24 hours. Neurology consultation for ongoing management."
    },
    "mrsa-cellulitis": {
        "S": "Patient reports spreading redness and warmth on right lower leg for 3 days, worsening despite oral cephalexin. Purulent drainage from a central site. History of prior MRSA infection 1 year ago.",
        "O": "Erythema 12x8 cm with central fluctuance, warmth, and tenderness. MRSA risk factors: prior MRSA infection, failed outpatient beta-lactam therapy. WBC 13.2. No crepitus. Allergy consideration: patient reports sulfa allergy (rash, non-anaphylactic) — TMP-SMX avoided.",
        "A": "Purulent cellulitis with high suspicion for MRSA. Antibiotic selection: vancomycin IV given failed outpatient therapy, prior MRSA, and allergy consideration limiting oral alternatives.",
        "P": "Vancomycin IV dosed by pharmacy per weight/renal function. Wound culture of purulent drainage for sensitivities. Mark erythema borders. Elevate extremity. I&D if fluctuance increases. Trough level before 4th dose."
    },
    "hyperkalemia": {
        "S": "Patient reports generalized weakness and paresthesias in hands. Missed dialysis session 2 days ago. History of CKD stage 4 and heart failure.",
        "O": "Potassium level 7.1 mEq/L. ECG changes: peaked T waves, widened QRS (130ms), loss of P waves. Cr 5.8, BUN 72. No ST changes suggestive of ischemia.",
        "A": "Severe hyperkalemia with cardiac toxicity. Emergent management required immediately given ECG changes. Potassium shifting agents: insulin/dextrose and sodium bicarbonate to temporize while arranging dialysis.",
        "P": "Calcium gluconate IV 2g over 5 minutes for cardiac membrane stabilization. Insulin and dextrose IV: regular insulin 10 units IV + D50 50mL. Sodium bicarbonate 50 mEq IV. Albuterol nebulizer 10mg. Kayexalate 30g PO. Emergent nephrology consult for dialysis. Continuous telemetry. Repeat K+ in 1 hour."
    },
    "hepatic-encephalopathy": {
        "S": "Family reports patient has been increasingly confused and sleepy over 2 days. Patient not making sense, unable to care for himself. Denies alcohol use recently. History of cirrhosis secondary to hepatitis C.",
        "O": "Ammonia level 142 mcmol/L (elevated). Mental status changes: oriented to person only, asterixis present, unable to perform serial 7s. West Haven grade III (somnolent but arousable, markedly confused). Precipitant identification: UA positive for UTI, also recent constipation (last BM 4 days ago).",
        "A": "Hepatic encephalopathy, West Haven grade III. Precipitants include UTI and constipation. Lactulose plan: aggressive titration to 3-4 bowel movements per day.",
        "P": "Lactulose oral 30mL q2h until bowel movement, then titrate to 3-4 BMs/day. Rifaximin oral 550mg BID as adjunct. Treat UTI with ceftriaxone. Protein restriction is NOT recommended per current guidelines. Monitor ammonia trend. Fall precautions. Aspiration precautions given mental status."
    },
    "anaphylaxis": {
        "S": "Patient ate shrimp 30 minutes ago, developed diffuse urticaria, lip swelling, throat tightness, and difficulty breathing. EpiPen administered by paramedics en route.",
        "O": "Causative agent: shrimp (shellfish) — confirmed food allergy trigger. Anaphylaxis criteria: met — acute onset with skin involvement (urticaria), respiratory compromise (stridor, wheezing), and hypotension (BP 82/50). Airway assessment: stridor improved post-epinephrine, no intubation required currently but equipment at bedside. Epinephrine administration: IM epi given prehospital, repeat dose given in ED. Hemodynamic response: BP improved to 102/68 after IV fluids and epi.",
        "A": "Anaphylaxis secondary to shellfish ingestion. Biphasic reaction monitoring: must observe minimum 6 hours given severity, risk of recurrence.",
        "P": "Epinephrine IV drip at 0.1 mcg/kg/min, titrate to MAP >65. Methylprednisolone IV 125mg to prevent biphasic reaction. Famotidine 20mg IV. Continuous monitoring. Biphasic reaction monitoring: observe minimum 6 hours. Allergen documentation in chart. EpiPen prescription and allergy clinic referral at discharge."
    },
    "hip-fracture": {
        "S": "Patient fell at home, unable to bear weight on left leg. On warfarin for atrial fibrillation. Last dose was this morning.",
        "O": "X-ray confirms left intertrochanteric hip fracture. INR 3.8 (supratherapeutic). Fracture type: intertrochanteric, stable pattern. Anticoagulation reversal needed prior to surgical fixation. Hemoglobin 11.2, otherwise pre-op labs within normal limits.",
        "A": "Left intertrochanteric hip fracture requiring operative fixation. Anticoagulation reversal: supratherapeutic INR requires correction before surgery. Surgical planning: target INR <1.5 for safe operative intervention.",
        "P": "Vitamin K IV 10mg for INR reversal. Orthopedic surgery consult for operative planning. Pain management with femoral nerve block. DVT prophylaxis with mechanical compression (hold chemical prophylaxis). Repeat INR in 6 hours. Surgical planning: target surgery within 24-48 hours once INR corrected."
    },
    "asthma-exacerbation": {
        "S": "Patient reports progressive wheezing and dyspnea over 6 hours. Used rescue inhaler 8 times without improvement. Unable to speak in full sentences.",
        "O": "Peak flow 150 L/min (35% predicted). ABG with pCO2 interpretation: pCO2 42 — normal but concerning in setting of acute asthma (expected hypocapnia), suggests impending respiratory failure. Accessory muscle use: sternocleidomastoid and intercostal retractions present. SpO2 90% on 4L NC. Breath sounds: diffuse expiratory wheezes, poor air movement bilaterally.",
        "A": "Severe acute asthma exacerbation (near-fatal features: normalizing pCO2, poor air movement). Steroid therapy: IV methylprednisolone for severe exacerbation refractory to bronchodilators. Bronchodilator response: minimal improvement after 3 rounds of albuterol/ipratropium. Intubation readiness: RSI equipment at bedside given impending respiratory failure risk.",
        "P": "Magnesium sulfate IV 2g over 20 minutes. Methylprednisolone IV 125mg now. Continuous albuterol nebulization. Steroid therapy: continue IV steroids q6h, transition to PO prednisone when improving. Bronchodilator response: reassess in 1 hour. Intubation readiness: anesthesia notified, ketamine preferred induction agent if needed. ICU bed requested."
    },
    "alcohol-withdrawal": {
        "S": "Patient admitted for elective surgery, last drink approximately 18 hours ago. Developing progressive tremor, anxiety, and diaphoresis. History of prior withdrawal seizures and one episode of delirium tremens in 2023.",
        "O": "CIWA score 24 (severe withdrawal). Vitals: HR 118, BP 162/98, temp 37.8. Seizure history: prior DT and withdrawal seizures — high risk for complicated withdrawal. Last drink timing: 18 hours, consistent with onset of major withdrawal symptoms. Magnesium 1.3, phosphate 2.0 (both low). LFTs: AST 98, ALT 64. Platelets 112K.",
        "A": "Acute alcohol withdrawal, severe (CIWA 24). Delirium tremens risk: HIGH given prior history of DTs and seizures. Benzodiazepine plan: symptom-triggered protocol with CIWA scoring q1h, lorazepam preferred given hepatic impairment.",
        "P": "Lorazepam IV 2mg q1h for CIWA >15, may repeat q15 min for CIWA >20. Thiamine IV 500mg daily x3 days (high-dose for Wernicke prophylaxis). Folate, MgSO4, and phosphate repletion. Benzodiazepine plan: CIWA-guided dosing with 1:1 sitter. Delirium tremens risk: ICU transfer if CIWA remains >25 or benzodiazepine requirement exceeds 10mg in first hour. Seizure precautions."
    },
    "cdiff-colitis": {
        "S": "Patient reports 8 episodes of watery diarrhea daily for 3 days. Recently completed a course of ciprofloxacin for UTI 1 week ago. Abdominal cramping and low-grade fever.",
        "O": "C. diff severity: WBC 22.4, creatinine 1.6 (above baseline of 1.0), temperature 38.4 — meets criteria for severe C. difficile infection. Prior antibiotic exposure: ciprofloxacin completed 7 days ago (high-risk fluoroquinolone). CT shows colonic wall thickening without megacolon.",
        "A": "Severe C. difficile colitis per IDSA criteria (WBC >15K, Cr >1.5x baseline). Oral vancomycin plan: first-line for severe C. diff per IDSA/SHEA 2021 guidelines.",
        "P": "Vancomycin oral 125mg QID for 10 days. CT abdomen pelvis to rule out toxic megacolon and complications. Contact precautions. Rehydrate aggressively. Probiotics are NOT recommended during active infection. Oral vancomycin plan: if no improvement in 48 hours, escalate to vancomycin 500mg QID + IV metronidazole. Monitor for fulminant disease."
    },
    "thyroid-storm": {
        "S": "Patient presents with agitation, fever, and palpitations. History of Graves' disease, stopped methimazole on her own 2 weeks ago. Husband reports progressive confusion.",
        "O": "Thyroid hormone levels: free T4 5.8 ng/dL (markedly elevated), TSH <0.01. HR 142, irregular. Temp 39.8 C. Burch-Wartofsky score 55 (suggestive of thyroid storm). Precipitating event: medication non-compliance with methimazole discontinuation.",
        "A": "Thyroid storm (Burch-Wartofsky >45). Anti-thyroid therapy: PTU preferred over methimazole in storm due to additional inhibition of T4-to-T3 conversion. Beta-blocker rationale: propranolol preferred for adrenergic symptom control AND additional inhibition of peripheral T4-to-T3 conversion. Temperature management: active cooling required.",
        "P": "Propylthiouracil oral 200mg q4h loading. Propranolol IV 1mg q5-10 min until HR <100, then PO 60mg q6h. Beta-blocker rationale: propranolol for dual benefit of rate control and T4-to-T3 conversion block. SSKI (potassium iodide) after 1 hour of PTU loading. Hydrocortisone 100mg IV q8h (relative adrenal insufficiency). Temperature management: acetaminophen, cooling blanket. Avoid aspirin (displaces thyroid hormone from TBG). ICU admission."
    },
    "sickle-cell-crisis": {
        "S": "Patient reports severe bilateral lower extremity and back pain since yesterday, rated 10/10. Usual crisis pattern. Denies cough, chest pain, or fever. Last crisis was 3 months ago.",
        "O": "Hemoglobin baseline 8.2 (current 7.4, below baseline). Pain assessment: 10/10 bilateral legs and back, consistent with prior VOC pattern. Acute chest syndrome screening: CXR clear, no infiltrates, SpO2 96% on RA, no chest pain, temp 37.1. Morphine allergy and opioid selection: documented morphine allergy (causes severe itching and hives) — hydromorphone selected. Reticulocyte count 8.2%. LDH 340.",
        "A": "Vaso-occlusive crisis, uncomplicated. Hemoglobin below baseline. Acute chest syndrome screening negative but must continue monitoring. Transfusion threshold: consider transfusion if Hgb drops below 6 or develops ACS.",
        "P": "Hydromorphone PCA per sickle cell protocol (demand dose 0.2mg, lockout 8 min). Chest X-ray to rule out ACS (clear currently). Morphine allergy and opioid selection: hydromorphone is appropriate alternative. IV fluids at 1.5x maintenance. Incentive spirometry q2h for ACS prevention. Transfusion threshold: transfuse if Hgb <6 or signs of ACS. Daily CBC, retic, LDH."
    },
    "bacterial-meningitis": {
        "S": "Patient is a 19-year-old college student presenting with severe headache, neck stiffness, and photophobia for 12 hours. Fever to 39.6 at home. Roommate reports she has been increasingly confused.",
        "O": "CSF analysis: WBC 2200 cells/uL (97% PMN), protein 280, glucose 18. CSF glucose-to-serum ratio: 18/90 = 0.20 (markedly low, <0.4 supports bacterial etiology). Gram stain results: gram-negative diplococci seen, consistent with N. meningitidis. Meningeal signs: nuchal rigidity, positive Kernig and Brudzinski signs. Petechial rash on trunk.",
        "A": "Acute bacterial meningitis, most likely Neisseria meningitidis. Empiric antibiotic rationale: ceftriaxone for CNS penetration and meningococcal coverage. Dexamethasone timing rationale: given BEFORE or with first dose of antibiotics to reduce inflammation and mortality (S. pneumoniae data extrapolated, continued per current guidelines). Droplet precautions: required for suspected N. meningitidis until 24 hours of effective antibiotic therapy.",
        "P": "Ceftriaxone IV 2g q12h. Dexamethasone IV 0.15 mg/kg q6h x4 days (started before antibiotics). Dexamethasone timing rationale: optimal benefit when given before or with first antibiotic dose. Droplet precautions implemented. Close contacts require chemoprophylaxis with rifampin or ciprofloxacin. Public health notification for meningococcal disease. Repeat LP not needed if clinical improvement."
    },
    "postop-ileus": {
        "S": "Patient is post-operative day 3 from right hemicolectomy. Reports progressive abdominal bloating, nausea, and has not passed gas or had a bowel movement since surgery.",
        "O": "Bowel function status: absent bowel sounds, abdomen distended and tympanitic, no flatus, no BM since surgery. KUB: dilated loops of small bowel with air-fluid levels, no free air. Electrolyte correction needed: K 3.1, Mg 1.5 (both low — can worsen ileus). NPO status: patient remained NPO, tolerating only ice chips.",
        "A": "Post-operative ileus, POD 3. No signs of anastomotic leak (afebrile, lactate normal, no peritoneal signs). Electrolyte correction: hypokalemia and hypomagnesemia may be contributing to ileus and need aggressive correction.",
        "P": "Nasogastric tube placement for decompression. Potassium chloride IV 40 mEq in 100mL over 4 hours. MgSO4 2g IV. NPO status maintained. Ambulation encouraged. Hold opioids, switch to acetaminophen/ketorolac for pain. Reassess bowel function in 24 hours. If no improvement in 48h, consider CT to rule out mechanical obstruction."
    },
}


def build_note_text(task: dict) -> str:
    """Build a complete progress note from the SOAP template."""
    tid = task["id"]
    tmpl = SOAP_TEMPLATES.get(tid)
    if not tmpl:
        # Fallback: generate generic note mentioning all elements
        elements = task["required_note_elements"]
        elements_text = ". ".join(elements)
        return f"S: Patient reports symptoms.\nO: {elements_text}. Labs reviewed.\nA: {task['title'].split(' — ')[0]}.\nP: Continue management per protocol."

    return f"S: {tmpl['S']}\nO: {tmpl['O']}\nA: {tmpl['A']}\nP: {tmpl['P']}"


def build_order_category(order_name: str) -> str:
    """Heuristically determine order category."""
    name_lower = order_name.lower()
    if any(w in name_lower for w in ["x-ray", "ct ", "ct angiography", "cta", "mri", "ultrasound", "echo", "chest x-ray", "kub"]):
        return "IMAGING"
    if any(w in name_lower for w in ["panel", "culture", "cbc", "bmp", "cmp", "lumbar", "wound culture", "blood culture"]):
        return "LAB"
    return "MED"


def build_order_params(order_name: str) -> str:
    """Generate realistic parameters for an order."""
    name_lower = order_name.lower()
    if "bolus" in name_lower or "saline" in name_lower or "ringer" in name_lower:
        return "1L IV over 1 hour"
    if "drip" in name_lower or "infusion" in name_lower:
        return "Per protocol, titrate to goal"
    if "iv" in name_lower:
        return "IV, per protocol"
    if "oral" in name_lower:
        return "PO, per protocol"
    if "panel" in name_lower or "culture" in name_lower:
        return "STAT"
    if "x-ray" in name_lower or "ct " in name_lower or "angiography" in name_lower:
        return "STAT"
    if "consult" in name_lower:
        return "Urgent, please evaluate"
    if "pca" in name_lower:
        return "Per sickle cell pain protocol"
    if "tube" in name_lower or "ngt" in name_lower or "nasogastric" in name_lower:
        return "Standard placement, low intermittent suction"
    return "Per protocol"


def build_order_rationale(order_name: str, task: dict) -> str:
    """Generate a brief rationale for the order."""
    title = task["title"].split(" — ")[0]
    return f"Indicated for {title} management"


def build_actions(task: dict) -> list[dict]:
    """Build the action sequence for a task."""
    patient_id = task["patient_id"]
    actions = []

    # 1. Click patient card from dashboard
    actions.append({"type": "click", "selector": f"[data-testid='patient-card-{patient_id}']"})

    # 2. Navigate to Notes tab
    actions.append({"type": "click", "selector": "[data-testid='activity-notes']"})

    # 3. Fill in the note
    note_text = build_note_text(task)
    actions.append({"type": "fill", "selector": "[aria-label='Note author']", "text": "Patrick Sullivan, MD"})
    actions.append({"type": "fill", "selector": "[aria-label='Note title']", "text": "Progress Note"})
    actions.append({"type": "fill", "selector": "[aria-label='Progress note content']", "text": note_text})
    actions.append({"type": "click", "selector": "[data-testid='save-note-button']"})
    actions.append({"type": "wait", "milliseconds": 600})

    # 4. Navigate to Orders tab
    actions.append({"type": "click", "selector": "[data-testid='activity-orders']"})

    # 5. Place each required order
    for order_name in task["required_orders"]:
        category = build_order_category(order_name)
        params = build_order_params(order_name)
        rationale = build_order_rationale(order_name, task)

        actions.append({"type": "fill", "selector": "[aria-label='Order name']", "text": order_name})

        # Select the correct category
        actions.append({"type": "fill", "selector": "[aria-label='Order category']", "text": category})

        actions.append({"type": "fill", "selector": "[aria-label='Order parameters']", "text": params})
        actions.append({"type": "fill", "selector": "[aria-label='Order rationale']", "text": rationale})

        # The "Sign immediately" checkbox is defaultChecked, no need to click it
        actions.append({"type": "click", "selector": "[data-testid='save-order-button']"})
        actions.append({"type": "wait", "milliseconds": 600})

    # 6. Sign the encounter
    actions.append({"type": "click", "selector": "[data-testid='sign-encounter-button']"})

    return actions


def main():
    task_files = sorted(glob.glob(str(TASKS_DIR / "*.json")))
    generated = 0

    for task_file in task_files:
        with open(task_file) as f:
            task = json.load(f)

        patient_id = task.get("patient_id")
        if not patient_id:
            continue  # skip non-task files like aki-demo-actions.json

        task_id = task["id"]
        actions = build_actions(task)
        note_text = build_note_text(task)

        # Validate that note mentions all required elements
        missing = []
        for element in task["required_note_elements"]:
            if element.lower() not in note_text.lower():
                missing.append(element)
        if missing:
            print(f"  WARNING: {task_id} note is missing elements: {missing}")

        bundle = {
            "task_id": f"{task_id}-rollout",
            "description": f"Synthetic rollout for {task['title']}. Reviews chart, writes progress note, places orders, and signs the encounter.",
            "reset_request": {
                "patient_id": patient_id
            },
            "actions": actions
        }

        output_path = TASKS_DIR / f"{task_id}-actions.json"
        with open(output_path, "w") as f:
            json.dump(bundle, f, indent=2)
            f.write("\n")

        generated += 1
        print(f"  Generated {output_path.name} ({len(actions)} actions)")

    print(f"\nDone: {generated} rollout bundles generated")


if __name__ == "__main__":
    main()
