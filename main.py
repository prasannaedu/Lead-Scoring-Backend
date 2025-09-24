from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from typing import List
import csv, io, os

from scoring import ScoringEngine, OfferModel

app = FastAPI(title="Kuvaka Tech - Lead Scoring Service")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory storage
DB = {"offer": None, "leads": [], "results": []}

@app.post("/offer")
async def post_offer(offer: OfferModel):
    DB["offer"] = offer.dict()
    return {"status": "ok", "offer": DB["offer"]}

@app.post("/leads/upload")
async def upload_leads(file: UploadFile = File(...)):
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV files accepted.")
    content = await file.read()
    reader = csv.DictReader(io.StringIO(content.decode("utf-8")))
    leads = []
    for r in reader:
        leads.append({
            "name": r.get("name","").strip(),
            "role": r.get("role","").strip(),
            "company": r.get("company","").strip(),
            "industry": r.get("industry","").strip(),
            "location": r.get("location","").strip(),
            "linkedin_bio": r.get("linkedin_bio","").strip()
        })
    DB["leads"] = leads
    return {"status": "ok", "count": len(leads)}

@app.post("/score")
async def score_leads():
    if not DB["offer"]:
        raise HTTPException(status_code=400, detail="No offer provided. POST /offer first.")
    if not DB["leads"]:
        raise HTTPException(status_code=400, detail="No leads uploaded. POST /leads/upload first.")
    engine = ScoringEngine(DB["offer"])
    DB["results"] = [engine.score_lead(lead) for lead in DB["leads"]]
    return {"status": "ok", "count": len(DB["results"])}

@app.get("/results")
async def get_results():
    return DB["results"]

@app.get("/export_csv")
async def export_csv():
    if not DB["results"]:
        raise HTTPException(status_code=404, detail="No results available.")
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["name","role","company","industry","intent","score","reasoning"])
    for r in DB["results"]:
        writer.writerow([r.get("name",""),r.get("role",""),r.get("company",""),
                         r.get("industry",""),r.get("intent",""),
                         r.get("score",""), r.get("reasoning","")])
    return Response(
        content=output.getvalue(),
        media_type="text/csv",
        headers={"Content-Disposition":"attachment; filename=results.csv"}
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=int(os.environ.get("PORT", 8000)), reload=True)
