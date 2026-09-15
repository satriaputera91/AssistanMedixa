from typing import Dict, Any, Optional, Tuple
import logging
from app.modules.medical_agent.context.state import MedicalAgentState
from app.modules.medical_agent.logging_utils import (
    log_node_start, log_node_end, log_edge_transition,
    _debug_node_start, _debug_node_end, _debug_edge
)
from app.core.database import db
from app.core.config import settings
from app.prompts.planner_prompts import (
    PLANNER_SYSTEM_INSTRUCTION,
    CLASSIFY_INTENT_FUNCTION_DECLARATION,
    build_planner_prompt
)

logger = logging.getLogger("medical_agent.skills.planner")

try:
    from google import genai
    from google.genai import types
    HAS_GOOGLE_GENAI_SDK = True
except ImportError:
    HAS_GOOGLE_GENAI_SDK = False


def classify_intent_with_gemini_function_calling(
    query: str,
    patient_id: Optional[str] = None,
    patient_name: Optional[str] = None
) -> Tuple[Optional[str], Optional[Dict[str, Any]]]:
    """Uses Gemini GenAI Function Calling to classify clinical intent from doctor's query."""
    if not settings.GEMINI_API_KEY or not HAS_GOOGLE_GENAI_SDK:
        return None, None

    try:
        client = genai.Client(api_key=settings.GEMINI_API_KEY)
        
        # Build FunctionDeclaration for classify_clinical_intent
        fn_decl = types.FunctionDeclaration(
            name=CLASSIFY_INTENT_FUNCTION_DECLARATION["name"],
            description=CLASSIFY_INTENT_FUNCTION_DECLARATION["description"],
            parameters=CLASSIFY_INTENT_FUNCTION_DECLARATION["parameters"]
        )
        tools = [types.Tool(function_declarations=[fn_decl])]

        prompt = build_planner_prompt(user_query=query, patient_id=patient_id, patient_name=patient_name)

        config = types.GenerateContentConfig(
            system_instruction=PLANNER_SYSTEM_INSTRUCTION,
            tools=tools,
            temperature=0.1,
        )

        response = client.models.generate_content(
            model=settings.GEMINI_MODEL_NAME,
            contents=prompt,
            config=config
        )

        function_calls = getattr(response, "function_calls", None)
        if function_calls:
            fc = function_calls[0]
            func_name = getattr(fc, "name", "")
            func_args = getattr(fc, "args", {})
            if hasattr(func_args, "model_dump"):
                func_args = func_args.model_dump()
            elif not isinstance(func_args, dict):
                func_args = dict(func_args)

            if func_name == "classify_clinical_intent":
                intent_val = func_args.get("intent")
                if intent_val == "direct_conversation":
                    intent_val = None
                return intent_val, {
                    "source": "gemini_genai_function_call",
                    "function_name": func_name,
                    "arguments": func_args,
                    "reasoning": func_args.get("reasoning", ""),
                    "confidence": func_args.get("confidence", 0.95)
                }
    except Exception as e:
        logger.warning("Gemini GenAI intent classification failed: %s. Falling back to rule-based planner.", e)

    return None, None


def classify_intent_rule_based(
    query_lower: str,
    is_general_knowledge_mode: bool
) -> Optional[str]:
    """Rule-based intent classification fallback."""
    if is_general_knowledge_mode:
        if any(k in query_lower for k in ["pedoman", "guideline", "kriteria diagnosis", "staging", "kriteria diagnostik", "konsensus"]):
            return "1. Pedoman Klinis & Kriteria Diagnosis (Knowledge Management)"
        elif any(k in query_lower for k in ["panduan terapi", "lini pertama", "rejimen", "terapi obat", "pemilihan obat", "first-line"]):
            return "2. Panduan Terapi & Rejimen Lini Pertama (Knowledge Management)"
        elif any(k in query_lower for k in ["panduan tindakan", "prosedur medis", "protokol tindakan", "indikasi tindakan"]):
            return "3. Panduan Tindakan & Prosedur Medis (Clinical Guidelines)"
        elif any(k in query_lower for k in ["penyesuaian dosis", "renal dosing", "hepatic", "gangguan ginjal", "penurunan egfr", "fungsi hati"]):
            return "4. Penyesuaian Dosis Ginjal & Hepar (Knowledge Management)"
        elif any(k in query_lower for k in ["skrining interaksi", "interaksi obat", "ddi", "kombinasi berisiko", "kontraindikasi"]):
            return "5. Skrining Interaksi Obat & Kontraindikasi (Knowledge Management)"
        elif any(k in query_lower for k in ["tanda bahaya", "red flag", "ambang kritis", "kegawatdaruratan", "kriteria rujukan"]):
            return "6. Deteksi Tanda Bahaya & Kedaruratan (Knowledge Management)"
        elif any(k in query_lower for k in ["biomarker", "hasil lab", "interpretasi lab", "nilai normal", "nilai rujukan"]):
            return "7. Interpretasi Biomarker & Hasil Lab (Knowledge Management)"
        elif any(k in query_lower for k in ["patofisiologi", "mekanisme penyakit", "etiologi"]):
            return "8. Penjelasan Patofisiologi & Mekanisme Penyakit (Knowledge Management)"
        return None

    # Patient-Specific
    if any(k in query_lower for k in ["buat cppt", "kirim cppt", "kirim soap", "buat soap", "sinkronisasi cppt", "simpan cppt", "kirim/sinkronisasikan", "update simrs", "sync simrs", "commit emr", "kirim ke simrs", "kirim/sinkronisasi"]):
        return "10. Buat Draft CPPT S/O/A/P"
    elif any(k in query_lower for k in [
        "ambil informasi pasien", "informasi pasien", "ambil data pasien", "data pasien",
        "ambil informasi demografi", "ambil informasi riwayat", "ambil data profil",
        "profil demografi", "demografi pasien", "demografi", "profil pasien",
        "identitas pasien", "data demografi"
    ]):
        return "1. Ambil Informasi Demografi Pasien (SIMRS / Satu Sehat)"
    elif any(k in query_lower for k in ["anamnesis", "keluhan", "rps", "rpd", "rpk", "tinjauan sistem"]):
        return "2. Ambil Anamnesis Sebelumnya"
    elif any(k in query_lower for k in ["lab", "laboratorium", "ttv", "tanda vital", "egfr", "uacr", "hba1c", "elektrolit", "tensi"]):
        return "3. Evaluasi Hasil Lab & Pemeriksaan SIMRS (MCP)"
    elif any(k in query_lower for k in ["diagnosis", "icd", "banding", "differential"]):
        return "4. Rekomendasi Diagnosis & ICD-10"
    elif any(k in query_lower for k in ["rekomendasi obat", "terapi obat", "dosis", "regimen", "peresepan"]):
        return "5. Rekomendasi Terapi Obat Berbasis Bukti (Knowledge Management)"
    elif any(k in query_lower for k in ["rekomendasi tindakan", "prosedur medis", "rencana tindakan", "tindakan medis", "intervensi klinis", "tindakan", "prosedur"]):
        return "6. Rekomendasi Tindakan & Prosedur Medis (Clinical Procedures & Interventions)"
    elif any(k in query_lower for k in ["patofisiologi", "penjelasan penyakit", "kriteria diagnostik", "staging"]):
        return "7. Penjelasan Penyakit & Patofisiologi (Knowledge Management)"
    elif any(k in query_lower for k in ["tanda bahaya", "red flag", "bahaya", "urgensi", "kegawatdaruratan"]):
        return "8. Deteksi Tanda Bahaya & Red Flags (Knowledge Management)"
    elif any(k in query_lower for k in ["skrining", "interaksi obat", "keamanan obat", "ddi", "efek samping"]):
        return "9. Skrining Interaksi & Keamanan Obat Pasien"
    elif any(k in query_lower for k in ["evaluasi klinis", "evaluasi lengkap", "laporan lengkap", "semua data", "evaluasi terpadu", "ringkasan lengkap", "konsultasi lengkap", "seluruh pemeriksaan"]):
        return "Evaluasi Klinis Terpadu SIMRS & Knowledge Management"

    return None


def node_planner(state: MedicalAgentState) -> MedicalAgentState:
    """Classifies clinical queries, determines intents, and plans workflow execution paths using Gemini GenAI function calling with rule fallback."""
    log_node_start("planner", state, icon="🧠")
    query = state.get("user_query", "")
    query_lower = query.lower()
    patient_id = state.get("patient_id")
    steps = list(state.get("steps_executed", []))
    
    is_general_knowledge_mode = not patient_id or not patient_id.strip()

    patient_name = None
    if patient_id:
        try:
            p_rec = db.patient_records.get(patient_id)
            if p_rec:
                patient_name = p_rec.get("name")
        except Exception:
            pass

    # 1. Primary: Gemini GenAI Function Calling Intent Classification
    detected_intent, fc_meta = classify_intent_with_gemini_function_calling(
        query=query,
        patient_id=patient_id,
        patient_name=patient_name
    )

    logger.info(f"Detected intent: {detected_intent}")

    # 2. Secondary: Fallback to deterministic rule-based classifier if GenAI FC is unconfigured or returns None
    if detected_intent is None:
        detected_intent = classify_intent_rule_based(
            query_lower=query_lower,
            is_general_knowledge_mode=is_general_knowledge_mode
        )
        planner_mode = "rule_based_fallback"
    else:
        planner_mode = "genai_function_call"

    # Format result and audit step
    if is_general_knowledge_mode:
        if detected_intent:
            steps.append({
                "step_name": "Agent Intelligence & Knowledge Planner",
                "description": f"Knowledge Intent: '{detected_intent}' (Konsultasi Medis Umum via {planner_mode})",
                "status": "completed",
                "result": {"detected_intent": detected_intent, "mode": "general_consultation", "classifier": planner_mode, "meta": fc_meta}
            })
            log_node_end("planner", f"Intent: '{detected_intent}' | Mode: General Consultation ({planner_mode})")
        else:
            steps.append({
                "step_name": "Agent Intelligence & Conversation Handler",
                "description": f"Merespons kueri konsultasi umum melalui basis pengetahuan medis (Knowledge Management via {planner_mode}).",
                "status": "completed",
                "result": {"detected_intent": None, "mode": "general_consultation", "classifier": planner_mode}
            })
            log_node_end("planner", f"Intent: None (General consultation / direct response via {planner_mode})")

        return {
            **state,
            "detected_intent": detected_intent,
            "steps_executed": steps
        }

    # Patient Mode
    simrs_mrn = f"MRN-SIMRS-{patient_id.replace('P-', '')}"
    pat_str = f"{patient_id} ({patient_name})" if patient_name else patient_id
    
    if detected_intent:
        steps.append({
            "step_name": "Agent Intelligence & Clinical Planner",
            "description": f"Clinical Intent Detected: '{detected_intent}' (Target Patient: {pat_str}, MRN: {simrs_mrn}, via {planner_mode})",
            "status": "completed",
            "result": {"detected_intent": detected_intent, "simrs_mrn": simrs_mrn, "patient_name": patient_name, "classifier": planner_mode, "meta": fc_meta}
        })
        log_node_end("planner", f"Intent: '{detected_intent}' | Patient: {pat_str} | MRN: {simrs_mrn} ({planner_mode})")
    else:
        steps.append({
            "step_name": "Agent Intelligence & Conversation Handler",
            "description": f"Tidak ada intent klinis khusus yang terdeteksi ({pat_str}). Merespons kueri secara percakapan langsung ({planner_mode}).",
            "status": "completed",
            "result": {"detected_intent": None, "patient_name": patient_name, "classifier": planner_mode}
        })
        log_node_end("planner", f"Intent: None (Direct conversation via {planner_mode}) | Patient: {pat_str}")

    return {
        **state,
        "detected_intent": detected_intent,
        "steps_executed": steps
    }
