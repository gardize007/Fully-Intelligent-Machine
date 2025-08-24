from builtins import any, str
import re

HEALTH_KEYWORDS = {
    "fever","cough","sore throat","throat","chest pain","shortness of breath","nausea",
    "vomit","diarrhea","rash","headache","migraine","asthma","flu","cold","infection",
    "pain","burn","cut","bleeding","dizzy","fatigue","tired","symptom","medicine","medication"
}
PLACES_KEYWORDS = {
    "near me","nearby","address","restaurant","restaurants","park","parks","nightclub","club","bar",
    "shop","store","mall","supermarket","pharmacy","clinic","hospital","embassy","museum","hotel","cafe",
    "coffee","library","cinema","theater","bus stop","station","airport","bank","atm"
}

def classify_intent(text: str) -> str:
    t = text.lower().strip()
    # quick rule: "find/show/where" + place word => places
    if any(k in t for k in PLACES_KEYWORDS) or re.search(r"\b(find|where|nearest|closest|show)\b", t):
        return "places"
    # symptom-ish text => health
    if any(k in t for k in HEALTH_KEYWORDS):
        return "health"
    # default => general QA
    return "general"
