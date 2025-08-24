from builtins import any, str
from typing import Dict, List

# Very simple rules to start; later we’ll plug in MedlinePlus/NHS/WHO lookups.
RED_FLAGS = [
    "severe chest pain", "difficulty breathing", "blue lips", "fainting",
    "confusion", "seizure", "pregnant bleeding", "stroke", "numbness one side"
]

BASIC_ADVICE = [
    "Stay hydrated and rest.",
    "Consider over-the-counter pain relievers per label instructions.",
    "Monitor symptoms and avoid known triggers."
]

def detect_red_flags(text: str) -> List[str]:
    t = text.lower()
    return [rf for rf in RED_FLAGS if rf in t]

def guess_common_causes(text: str) -> List[Dict[str, str]]:
    t = text.lower()
    causes = []
    if any(k in t for k in ["sore throat", "leg", "fever", "cough"]):
        causes.append({"name": "Viral upper respiratory infection (cold/flu)", "likelihood": "high"})
        causes.append({"name": "Strep throat", "likelihood": "medium"})
        causes.append({"name": "Allergy-related irritation", "likelihood": "low"})
    if "headache" in t or "migraine" in t:
        causes.append({"name": "Tension headache", "likelihood": "high"})
        causes.append({"name": "Migraine", "likelihood": "medium"})
        causes.append({"name": "Dehydration", "likelihood": "low"})
    if "chest pain" in t:
        causes.append({"name": "Musculoskeletal strain", "likelihood": "medium"})
        causes.append({"name": "Cardiac cause", "likelihood": "unknown"})
    return causes or [{"name": "General, non-specific symptoms", "likelihood": "unknown"}]

class HealthService:
    def handle(self, symptoms_text: str) -> Dict:
        flags = detect_red_flags(symptoms_text)
        causes = guess_common_causes(symptoms_text)

        message_lines = []
        if flags:
            message_lines.append("🚨 Red flags detected: " + "; ".join(flags))
            message_lines.append("If you are experiencing any of the above, seek emergency care immediately.")

        message_lines.append("Possible causes (not a diagnosis):")
        for c in causes[:5]:
            message_lines.append(f" - {c['name']} (likelihood: {c['likelihood']})")

        message_lines.append("\nSelf-care suggestions:")
        for a in BASIC_ADVICE:
            message_lines.append(f" - {a}")

        response = {
            "message": "\n".join(message_lines),
            "sources": [
                {"name": "Isala hospital (General Health Info)", "url": "https://www.isala.com]/"},
                {"name": "NHS Conditions", "url": "https://www.nhs.uk/conditions/"},
                {"name": "WHO Health Topics", "url": "https://www.who.int/health-topics"}
            ],
            "disclaimer": "\n⚠️ Educational information only. Not a medical diagnosis. Consult a healthcare professional."
        }
        return response
