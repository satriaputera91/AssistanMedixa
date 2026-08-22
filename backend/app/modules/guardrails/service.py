import re
from typing import Dict, List, Tuple
from app.modules.guardrails.schemas import TestGuardrailResponse

class GuardrailsService:
    # Common PII Regex Patterns
    PII_PATTERNS = {
        "NIK (16-digit ID)": r"\b[1-9]\d{15}\b",
        "Credit Card": r"\b(?:\d{4}[-\s]?){3}\d{4}\b",
        "Phone Number": r"\b(?:\+?62|08)\d{8,12}\b",
        "Email Address": r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",
        "Secret Key / Password": r"(?i)(password|secret_key|api_key|pin)\s*[:=]\s*['\"]?\w+['\"]?"
    }

    # Non-medical prompt injection / jailbreak patterns
    INJECTION_PATTERNS = [
        r"(?i)\b(ignore previous instructions|bypass safety|system prompt|jailbreak|pretend you are)\b",
        r"(?i)\b(buatkan resep palsu|surat izin palsu|narkotika ilegal|senjata|bom)\b",
    ]

    @classmethod
    def evaluate(cls, text: str, config: dict, target_type: str = "input") -> TestGuardrailResponse:
        if not config.get("enabled", True):
            return TestGuardrailResponse(
                passed=True,
                verdict="ALLOWED (Guardrails Disabled)",
                risk_score=0.0,
                risk_level="Low",
                violations=[],
                redacted_text=text,
                applied_rules=["System Bypass (Guardrails Inactive)"]
            )

        violations: List[str] = []
        applied_rules: List[str] = []
        redacted_text = text
        risk_score = 0.0

        # 1. Max length check
        max_len = config.get("max_query_length", 1500)
        applied_rules.append(f"Max Length Constraint ({max_len} chars)")
        if len(text) > max_len:
            violations.append(f"Teks melebihi batas {max_len} karakter (terdeteksi: {len(text)} karakter).")
            risk_score += 0.3

        # 2. PII Redaction & Detection
        if config.get("pii_redaction_enabled", True):
            applied_rules.append("PII Redaction & Privacy Filter")
            for pii_name, pattern in cls.PII_PATTERNS.items():
                matches = list(re.finditer(pattern, text))
                if matches:
                    violations.append(f"Terdeteksi data sensitif PII: {pii_name}")
                    risk_score += 0.25
                    redacted_text = re.sub(pattern, f"[REDACTED_{pii_name.upper().split()[0]}]", redacted_text)

        # 3. Banned Keywords Filter
        banned_keywords = config.get("banned_keywords", [])
        if banned_keywords:
            applied_rules.append(f"Banned Keywords Filter ({len(banned_keywords)} kata kunci)")
            for kw in banned_keywords:
                if kw.lower() in text.lower():
                    violations.append(f"Mengandung kata kunci terlarang: '{kw}'")
                    risk_score += 0.5

        # 4. Prompt Injection & Jailbreak Filter
        if config.get("toxic_content_filter", True):
            applied_rules.append("Toxic & Prompt Injection Shield")
            for inj_pat in cls.INJECTION_PATTERNS:
                if re.search(inj_pat, text):
                    violations.append("Terdeteksi upaya manipulasi instruksi / konten tidak aman.")
                    risk_score += 0.6
                    break

        # 5. Strictly Medical Scope Check
        if config.get("strictly_medical_scope", True) and target_type == "input":
            applied_rules.append("Medical Scope Verification")
            # If query asks for non-medical activities with explicit triggers
            non_medical_match = re.search(r"(?i)\b(resep kue|kue bolu|lirik lagu|coding game|ramalan zodiak|judi|saham)\b", text)
            if non_medical_match:
                violations.append(f"Pertanyaan di luar cakupan klinis medis ('{non_medical_match.group(0)}')")
                risk_score += 0.4

        # Calculate final verdict and risk level
        risk_score = min(round(risk_score, 2), 1.0)
        
        if risk_score >= 0.7:
            risk_level = "Critical" if risk_score >= 0.9 else "High"
            passed = False
            verdict = "REJECTED (Critical Safety Violation)"
        elif risk_score >= 0.4:
            risk_level = "Medium"
            # If safety level is strict, medium risk is rejected; otherwise flagged
            passed = config.get("safety_level", "Strict") != "Strict"
            verdict = "FLAGGED (Medium Risk)" if passed else "REJECTED (Strict Policy)"
        else:
            risk_level = "Low"
            passed = True
            verdict = "PASSED (Safe)"

        return TestGuardrailResponse(
            passed=passed,
            verdict=verdict,
            risk_score=risk_score,
            risk_level=risk_level,
            violations=violations,
            redacted_text=redacted_text,
            applied_rules=applied_rules
        )
