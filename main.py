from builtins import EOFError, KeyboardInterrupt, input, print
import os
from dotenv import load_dotenv
from utils.router import classify_intent
from services.qa_engine import QAEngine
from services.health_service import HealthService
from services.places_service import PlacesService
def banner():
    print("\\Welcome to S.A Intelligent Machine)")
    print("Type your request (e.g., 'I have a sore throat', 'Find parks in Berlin', 'Why is the sky blue?').")
    print("Type 'exit' to quit.\n")
def main():
    load_dotenv()  # loads .env if present
    qa = QAEngine(memory_path="memory.json")
    health = HealthService()
    places = PlacesService()
    banner()
    while True:
        try:
            text = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye!")
            break
        if not text:
            continue
        if text.lower() in {"exit", "quit"}:
            print("Goodbye!")
            break
        intent = classify_intent(text)
        if intent == "health":
            result = health.handle(text)
            print("\n--- Health Helper (educational, not a diagnosis) ---")
            print(result["message"])
            if result.get("sources"):
                print("\nSources:")
                for s in result["sources"]:
                    print(f"- {s['name']}: {s['url']}")
            print(result["disclaimer"])
            print("-----------------------------------------------------\n")
        elif intent == "places":
            result = places.search_from_text(text)
            print("\n--- Places & Addresses ---")
            if "error" in result:
                print("Error:", result["error"])
            elif not result["results"]:
                print("No places found.")
            else:
                for i, r in enumerate(result["results"], 1):
                    line = f"{i}. {r['name']} — {r.get('address','(no address)')}"
                    if r.get("rating") is not None:
                        line += f" | rating: {r['rating']}"
                    if r.get("open_now") is not None:
                        line += f" | open_now: {r['open_now']}"
                    print(line)
            if result.get("attribution"):
                print("\nAttribution:", ", ".join(result["attribution"]))
            print("--------------------------\n")
        else:  # general Q&A
            answer = qa.answer(text)
            print("\n--- Answer ---")
            print(answer)
            print("--------------\n")
if __name__ == "__main__":
    main()
