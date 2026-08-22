import re
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

from app.modules.guardrails.service import GuardrailsService
from app.core.database import db

logger = logging.getLogger("AIMedical.LLMOutputValidator")

# Allergy drug family cross-reference mapping for contraindication screening
ALLERGY_CROSS_MAP: Dict[str, List[str]] = {
    "penisilin": ["penicillin", "amoxicillin", "amoksisilin", "ampicillin", "ampisilin", "augmentin", "amoxiclav"],
    "penicillin": ["penicillin", "amoxicillin", "amoksisilin", "ampicillin", "ampisilin", "augmentin", "amoxiclav"],
    "sefalosporin": ["cefadroxil", "sefadrosil", "cefixime", "sefisim", "ceftriaxone", "seftriakson", "cefuroxime", "cephalexin"],
    "cephalosporin": ["cefadroxil", "sefadrosil", "cefixime", "sefisim", "ceftriaxone", "seftriakson", "cefuroxime", "cephalexin"],
    "nsaid": ["ibuprofen", "asam mefenamat", "mefenamic acid", "ketorolac", "diklofenak", "diclofenac", "meloxicam", "piroxicam", "aspirin", "asetosal"],
    "aspirin": ["aspirin", "asetosal", "acetylsalicylic acid"],
    "sulfa": ["cotrimoxazole", "kotrimoksazol", "sulfamethoxazole", "sulfasalazine", "glimepiride"],
    "sulfonamid": ["cotrimoxazole", "kotrimoksazol", "sulfamethoxazole", "sulfasalazine", "glimepiride"],
    "parasetamol": ["paracetamol", "parasetamol", "acetaminophen", "panadol", "sanmol"],
    "paracetamol": ["paracetamol", "parasetamol", "acetaminophen", "panadol", "sanmol"],
    "fluoroquinolone": ["ciprofloxacin", "ciprofloksasin", "levofloxacin", "levofloksasin", "moxifloxacin"],
}

MANDATORY_DISCLAIMER = (
    "\n\n---\n*(⚠️ **Clinical Disclaimer**: Sistem pendukung keputusan klinis AI ditujukan untuk "
    "dokter berwenang. Keputusan klinis sepenuhnya berada di bawah pertimbangan dokter penanggung jawab.)*"
)


class LLMOutputValidator:
    """
    Deterministic & heuristic validation engine for evaluating LLM-generated clinical outputs.
    Ensures safety, factual grounding against SIMRS EMR, allergy safety, red flag alerting,
    PII sanitization, and structured format compliance.
    """

    @classmethod
    def validate_grounding(
        cls,
        output_text: str,
        simrs_profile: Optional[Dict[str, Any]] = None,
        simrs_anamnesis: Optional[Dict[str, Any]] = None,
        simrs_labs: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Verify that mentioned patient parameters in LLM output do not contradict ground truth SIMRS data.
        """
        anomalies: List[str] = []
        checks_performed: List[str] = ["Demographics Grounding", "Lab Values Grounding", "Vital Signs Grounding"]

        if not simrs_profile and not simrs_anamnesis and not simrs_labs:
            return {
                "grounding_score": 1.0,
                "anomalies": [],
                "status": "SKIPPED_NO_PATIENT_CONTEXT",
                "checks_performed": checks_performed
            }

        text_lower = output_text.lower()

        # 1. Verify Patient Name & MRN if explicitly mentioned
        if simrs_profile:
            mrn = simrs_profile.get("mrn", "")
            full_name = simrs_profile.get("full_name", "")
            
            # Check if an incorrect MRN pattern is mentioned
            mentioned_mrns = re.findall(r"MRN-SIMRS-\d+", output_text, re.IGNORECASE)
            for m in mentioned_mrns:
                if mrn and m.upper() != mrn.upper():
                    anomalies.append(f"Nomor Rekam Medis tidak sesuai ground-truth: tertera '{m}', seharusnya '{mrn}'.")

            # Check if mismatched gender pronouns or terms occur
            patient_gender = (simrs_profile.get("gender") or "").lower()
            if patient_gender == "male" and any(w in text_lower for w in ["ny.", "ibu ", "wanita berusia", "perempuan"]):
                anomalies.append("Inkonsistensi gender: pasien berjenis kelamin Laki-laki tetapi teks menyebutkan perempuan.")
            elif patient_gender == "female" and any(w in text_lower for w in ["tn.", "bapak ", "pria berusia", "laki-laki"]):
                anomalies.append("Inkonsistensi gender: pasien berjenis kelamin Perempuan tetapi teks menyebutkan laki-laki.")

        # 2. Verify Vital Signs Consistency
        if simrs_labs and simrs_labs.get("vital_signs"):
            vitals = simrs_labs["vital_signs"]
            true_bp = vitals.get("blood_pressure")
            if true_bp:
                bp_match = re.search(r"(\d{2,3}/\d{2,3})\s*(?:mmhg)?", output_text, re.IGNORECASE)
                if bp_match:
                    found_bp = bp_match.group(1)
                    if found_bp not in true_bp and true_bp not in found_bp:
                        # Allow slight text difference, but flag major divergence
                        anomalies.append(f"Perbedaan tekanan darah: terdeteksi '{found_bp} mmHg' vs SIMRS '{true_bp}'.")

        # Calculate grounding score
        grounding_score = max(0.0, 1.0 - (len(anomalies) * 0.25))
        return {
            "grounding_score": round(grounding_score, 2),
            "anomalies": anomalies,
            "status": "PASSED" if not anomalies else ("WARNING" if grounding_score >= 0.75 else "FAILED"),
            "checks_performed": checks_performed
        }

    @classmethod
    def validate_allergy_contraindications(
        cls,
        output_text: str,
        simrs_anamnesis: Optional[Dict[str, Any]] = None,
        drug_safety_screening: Optional[Dict[str, Any]] = None,
        structured_output: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Check whether recommended medications in the LLM output violate known patient allergies.
        Validates both text content and typed structured_output medication objects.
        """
        contraindication_alerts: List[str] = []
        allergy_str = ""

        if simrs_anamnesis and simrs_anamnesis.get("allergy_history"):
            allergy_str = str(simrs_anamnesis["allergy_history"]).lower()

        if not allergy_str or allergy_str in ["tidak ada", "none", "disangkal", "tidak ada riwayat alergi", "-"]:
            return {
                "allergy_safe": True,
                "contraindication_alerts": [],
                "patient_allergies": "Tidak ada riwayat alergi diketahui"
            }

        text_lower = output_text.lower()

        # Find which allergens apply to the patient
        active_allergens = []
        for allergen_key, drug_list in ALLERGY_CROSS_MAP.items():
            if allergen_key in allergy_str:
                active_allergens.append((allergen_key, drug_list))

        # Check structured output medications if available
        if structured_output:
            plan_meds = structured_output.get("plan", {}).get("medications", []) if isinstance(structured_output.get("plan"), dict) else []
            if not plan_meds and isinstance(structured_output.get("treatment_recommendations"), list):
                plan_meds = structured_output.get("treatment_recommendations", [])

            for m in plan_meds:
                m_name = (m.get("drug_name") if isinstance(m, dict) else str(m)).lower()
                for allergen_key, drug_list in active_allergens:
                    for drug in drug_list:
                        if drug in m_name:
                            contraindication_alerts.append(
                                f"🚨 KONTRAINDIKASI ALERGI (Structured Plan): Obat '{m_name.title()}' dikontraindikasikan dengan riwayat alergi '{allergen_key.title()}' ({allergy_str})."
                            )

        # Check raw text for any mentions
        for allergen_key, drug_list in active_allergens:
            for drug in drug_list:
                if re.search(rf"\b{re.escape(drug)}\b", text_lower):
                    alert_msg = f"🚨 KONTRAINDIKASI ALERGI: Output merekomendasikan '{drug.title()}' padahal pasien memiliki riwayat alergi '{allergen_key.title()}' ({allergy_str})."
                    if alert_msg not in contraindication_alerts:
                        contraindication_alerts.append(alert_msg)

        # Cross-reference with drug safety screening findings
        if drug_safety_screening and drug_safety_screening.get("allergy_contraindications"):
            for alert in drug_safety_screening["allergy_contraindications"]:
                if alert not in contraindication_alerts:
                    contraindication_alerts.append(alert)

        return {
            "allergy_safe": len(contraindication_alerts) == 0,
            "contraindication_alerts": list(set(contraindication_alerts)),
            "patient_allergies": allergy_str
        }


    @classmethod
    def validate_red_flag_coverage(
        cls,
        output_text: str,
        red_flag_detections: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Verify that critical red flag emergency signals are explicitly highlighted in the output.
        """
        missing_red_flags: List[str] = []
        detected_flags = []

        if red_flag_detections:
            detected_flags = red_flag_detections.get("detected_red_flags", [])

        if not detected_flags:
            return {
                "red_flag_covered": True,
                "missing_red_flags": [],
                "total_critical_flags": 0
            }

        text_lower = output_text.lower()
        has_red_flag_section = any(k in text_lower for k in ["tanda bahaya", "red flag", "kegawatdaruratan", "peringatan", "waspada", "🚨", "⚠️"])

        for rf in detected_flags:
            flag_title = rf.get("title", "") if isinstance(rf, dict) else str(rf)
            flag_words = [w for w in re.findall(r"\w+", flag_title.lower()) if len(w) > 4]
            # Check if key concepts of the red flag are mentioned
            matched = any(w in text_lower for w in flag_words) if flag_words else False
            if not matched and not has_red_flag_section:
                missing_red_flags.append(f"Tanda bahaya '{flag_title}' belum terartikulasi secara eksplisit dalam respons.")

        return {
            "red_flag_covered": len(missing_red_flags) == 0,
            "missing_red_flags": missing_red_flags,
            "total_critical_flags": len(detected_flags)
        }

    @classmethod
    def validate_formatting_and_disclaimer(
        cls,
        output_text: str,
        config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Verify structured output formatting (CPPT/SOAP headers, ICD-10 formatting) and disclaimer presence.
        """
        auto_disclaimer = config.get("auto_disclaimer_enforced", True)
        has_disclaimer = any(d in output_text.lower() for d in ["clinical disclaimer", "disclaimer klinis", "pendukung keputusan klinis", "pertimbangan dokter penanggung jawab"])
        
        remediated_text = output_text
        remediation_applied = False

        if auto_disclaimer and not has_disclaimer and len(output_text.strip()) > 100:
            remediated_text = output_text + MANDATORY_DISCLAIMER
            remediation_applied = True

        # Check SOAP / CPPT formatting markers
        has_soap = bool(re.search(r"(?:###|\*\*|##)\s*(?:[👤🔬🎯💊📝]\s*)?[SOAP]\s*[—\-:]", output_text, re.IGNORECASE))
        has_icd10 = bool(re.search(r"\[ICD-10:\s*[A-Z]\d{2}(?:\.\d{1,2})?\]|[A-Z]\d{2}\.\d{1,2}", output_text))

        return {
            "has_disclaimer": has_disclaimer or remediation_applied,
            "has_soap_structure": has_soap,
            "has_icd10_coding": has_icd10,
            "remediation_applied": remediation_applied,
            "remediated_text": remediated_text
        }

    @classmethod
    def evaluate_all(
        cls,
        output_text: str,
        simrs_profile: Optional[Dict[str, Any]] = None,
        simrs_anamnesis: Optional[Dict[str, Any]] = None,
        simrs_labs: Optional[Dict[str, Any]] = None,
        red_flag_detections: Optional[Dict[str, Any]] = None,
        drug_safety_screening: Optional[Dict[str, Any]] = None,
        config: Optional[Dict[str, Any]] = None,
        structured_output: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Comprehensive evaluation pipeline for validating LLM-generated output.
        """
        if config is None:
            config = getattr(db, "guardrail_config", {}) or {
                "enabled": True,
                "pii_redaction_enabled": True,
                "strictly_medical_scope": True,
                "hallucination_prevention": True,
                "toxic_content_filter": True,
                "auto_disclaimer_enforced": True,
                "safety_level": "Strict"
            }

        # 1. Guardrail Safety Check (PII, Banned Words, Toxic Content)
        guardrail_res = GuardrailsService.evaluate(output_text, config=config, target_type="output")
        sanitized_text = guardrail_res.redacted_text or output_text

        # 2. Clinical Grounding & Hallucination Check
        grounding_res = cls.validate_grounding(
            sanitized_text,
            simrs_profile=simrs_profile,
            simrs_anamnesis=simrs_anamnesis,
            simrs_labs=simrs_labs
        )

        # 3. Allergy & Contraindication Check (text + structured_output)
        allergy_res = cls.validate_allergy_contraindications(
            sanitized_text,
            simrs_anamnesis=simrs_anamnesis,
            drug_safety_screening=drug_safety_screening,
            structured_output=structured_output
        )


        # 4. Red Flag Coverage Check
        red_flag_res = cls.validate_red_flag_coverage(
            sanitized_text,
            red_flag_detections=red_flag_detections
        )

        # 5. Formatting & Disclaimer Enforcement
        format_res = cls.validate_formatting_and_disclaimer(sanitized_text, config=config)
        final_text = format_res["remediated_text"]

        # Aggregate Safety & Quality Score
        score = 1.0
        alerts: List[str] = []

        if not guardrail_res.passed:
            score -= 0.4
            alerts.extend(guardrail_res.violations)

        if not allergy_res["allergy_safe"]:
            score -= 0.35
            alerts.extend(allergy_res["contraindication_alerts"])

        if grounding_res["anomalies"]:
            score -= (1.0 - grounding_res["grounding_score"]) * 0.3
            alerts.extend(grounding_res["anomalies"])

        if red_flag_res["missing_red_flags"]:
            score -= 0.15
            alerts.extend(red_flag_res["missing_red_flags"])

        score = max(0.0, min(round(score, 2), 1.0))

        # Determine overall status
        if score >= 0.85 and allergy_res["allergy_safe"] and guardrail_res.passed:
            status = "PASSED"
            verdict = "VALID (Clinically Safe & Grounded)"
        elif not allergy_res["allergy_safe"] or not guardrail_res.passed or score < 0.5:
            status = "REJECTED" if config.get("safety_level") == "Strict" else "WARNING"
            verdict = "REJECTED (Critical Safety / Contraindication Detected)" if status == "REJECTED" else "FLAGGED (Safety Caution)"
        elif format_res["remediation_applied"]:
            status = "REMEDIATED"
            verdict = "REMEDIATED (Auto-corrected & Disclaimer Injected)"
        else:
            status = "WARNING"
            verdict = "WARNING (Minor Grounding / Red Flag Discrepancies)"

        validation_result = {
            "is_valid": status in ["PASSED", "REMEDIATED", "WARNING"],
            "status": status,
            "verdict": verdict,
            "validation_score": score,
            "alerts": alerts,
            "remediated_text": final_text,
            "remediation_applied": format_res["remediation_applied"],
            "details": {
                "grounding": grounding_res,
                "allergy_safety": allergy_res,
                "red_flag_coverage": red_flag_res,
                "formatting": {
                    "has_disclaimer": format_res["has_disclaimer"],
                    "has_soap_structure": format_res["has_soap_structure"],
                    "has_icd10_coding": format_res["has_icd10_coding"],
                },
                "guardrails": {
                    "passed": guardrail_res.passed,
                    "risk_level": guardrail_res.risk_level,
                    "risk_score": guardrail_res.risk_score,
                    "violations": guardrail_res.violations,
                    "applied_rules": guardrail_res.applied_rules
                }
            },
            "timestamp": datetime.now().isoformat()
        }

        return validation_result
