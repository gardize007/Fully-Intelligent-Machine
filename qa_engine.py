from builtins import Exception, FileNotFoundError, float, open, str
import json
from difflib import SequenceMatcher
from typing import List, Dict, Any

# Optional heavy deps handled gracefully:
try:
    import wikipedia
except Exception:
    wikipedia = None

try:
    from sentence_transformers import SentenceTransformer, util
    _SEM_MODEL = SentenceTransformer('all-MiniLM-L6-v2')
except Exception:
    _SEM_MODEL = None
    util = None

def _str_sim(a: str, b: str) -> float:
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()

def _sem_sim(a: str, b: str) -> float:
    if not _SEM_MODEL or not a or not b:
        return 0.0
    e1 = _SEM_MODEL.encode(a, convert_to_tensor=True)
    e2 = _SEM_MODEL.encode(b, convert_to_tensor=True)
    return float(util.pytorch_cos_sim(e1, e2).item())

class QAEngine:
    def __init__(self, memory_path: str = "memory.json"):
        self.memory_path = memory_path
        self.memory: Dict[str, List[Dict[str, Any]]] = self._load()

    def _load(self) -> Dict[str, Any]:
        try:
            with open(self.memory_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError:
            return {}
        except Exception:
            return {}

    def _save(self):
        with open(self.memory_path, "w", encoding="utf-8") as f:
            json.dump(self.memory, f, ensure_ascii=False, indent=2)

    def _wiki_summary(self, question: str) -> str | None:
        if not wikipedia:
            return None
        try:
            return wikipedia.summary(question, sentences=1)
        except Exception:
            return None

    def _combined_score(self, answer_text: str, online_text: str | None, user_score: int) -> float:
        s = float(user_score)
        if online_text:
            s += _str_sim(answer_text, online_text)
            s += _sem_sim(answer_text, online_text)
        return s

    def _get_best_answer_from_memory(self, question: str, online_text: str | None) -> str | None:
        answers = self.memory.get(question, [])
        if not answers:
            return None
        # compute combined scores
        for a in answers:
            a["combined_score"] = self._combined_score(a["answer"], online_text, a.get("score", 0))
        answers.sort(key=lambda x: x.get("combined_score", 0), reverse=True)
        return answers[0]["answer"]

    def _autonomous_learn(self, question: str) -> str | None:
        # Phase 5: fetch online summary and store as a candidate
        online = self._wiki_summary(question)
        if online:
            self.memory.setdefault(question, []).append({"answer": online, "score": 1})
            self._save()
        return online

    def answer(self, question: str) -> str:
        question = question.strip()
        online_guess = self._wiki_summary(question)  # attempt Phase 3/5 generation

        best = self._get_best_answer_from_memory(question, online_guess)
        if best:
            # light autonomous reinforcement (reward similar answers)
            for a in self.memory.get(question, []):
                if _str_sim(a["answer"], online_guess or "") > 0.7 or _sem_sim(a["answer"], online_guess or "") > 0.7:
                    a["score"] = a.get("score", 0) + 1
            self._save()
            return best

        # If new question, autonomously learn
        learnt = self._autonomous_learn(question)
        if learnt:
            return learnt

        # Last resort: ask user (but since this is a non-interactive method, we return a prompt)
        return "I don't know yet. Please provide a correct answer, and I will learn it."
