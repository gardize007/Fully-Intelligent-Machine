from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from services.qa_engine import QAEngine
from services.health_service import HealthService
from services.places_service import PlacesService

app = FastAPI()
templates = Jinja2Templates(directory="templates")

# Initialize services
qa = QAEngine(memory_path="memory.json")
health = HealthService()
places = PlacesService()
def classify_intent(query: str) -> str:
    query_lower = query.lower()
    if any(word in query_lower for word in ["sore", "pain", "fever", "throat", "headache", "leg"]):
        return "health"
    elif any(word in query_lower for word in ["find", "park", "restaurant", "location", "city", "places"]):
        return "places"
    else:
        return "general"


@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "answer": ""})

@app.post("/ask", response_class=HTMLResponse)
async def ask(request: Request, query: str = Form(...)):
    # Decide intent
    intent = classify_intent(query)
    answer = ""
    if intent == "health":
        result = health.handle(query)
        answer = result["message"]
    elif intent == "places":
        result = places.search_from_text(query)
        if result["results"]:
            answer = "\n".join([f"{r['name']} - {r.get('address','No address')}" for r in result["results"]])
        else:
            answer = "No places found."
    else:
        answer = qa.answer(query)

    return templates.TemplateResponse("index.html", {"request": request, "answer": answer})
