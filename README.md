# Lead Scoring Backend Service 🚀
This backend service scores leads based on product/offers and prospect data. It combines rule-based logic with AI reasoning (OpenAI) to assign an intent and score to each lead.

✅ Runs locally or on the cloud (Render).  
✅ Accepts CSV uploads.  
✅ Exports scored results automatically.

---

##  Live Demo

The service is deployed on Render:  
 [https://lead-scoring-backend-wyrt.onrender.com/docs](https://lead-scoring-backend-wyrt.onrender.com/docs)

You can test all endpoints using the interactive Swagger UI.

---

##  Features

- Accept product/offer information via API
- Upload prospect leads CSV
- Rule-based + AI scoring pipeline
- Retrieve scored leads as JSON
- Export results as CSV
- Fully automated workflow via `run_lead_scoring.sh`

---

##  Tech Stack

- **Python 3.13**
- **FastAPI** for APIs
- **Uvicorn** as ASGI server
- **OpenAI API** for AI scoring
- **python-multipart** for file uploads
- **jq** for JSON parsing in shell script
- **Docker** for containerized deployment

---

##  Setup (Local Development)

### 1. Clone the repository

```bash
git clone https://github.com/prasannaedu/Lead-Scoring-Backend.git
cd Lead-Scoring-Backend
```

### 2. Create and activate virtual environment

```bash
python -m venv venv
# Windows
.\venv\Scripts\activate
# macOS/Linux
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Set OpenAI API key

```bash
# Windows
setx OPENAI_API_KEY "your_openai_api_key_here"
# macOS/Linux
export OPENAI_API_KEY="your_openai_api_key_here"
```

### 5. Run the server locally

```bash
uvicorn main:app --host 127.0.0.1 --port 8000 --reload
```

API will be available at:  
 [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

---

## 🌍 Deployment (Render)

This service is containerized and deployable with Render.

- **Dockerfile** is included (Render auto-detects it).
- Exposes port `8000`.
- Environment variable required:
  - `OPENAI_API_KEY = your_openai_api_key_here`

Deployed version:  
 [https://lead-scoring-backend-wyrt.onrender.com/docs](https://lead-scoring-backend-wyrt.onrender.com/docs)

---

##  API Endpoints

### 1. `POST /offer`

**Description**: Submit product/offer details.

**Request Body (JSON)**:

```json
{
  "name": "Special Discount",
  "value_props": ["10% off on all premium products"],
  "ideal_use_cases": ["Best for returning customers during holiday season"]
}
```

**Response**:

```json
{
  "status": "ok",
  "offer": {
    "name": "Special Discount",
    "value_props": ["10% off on all premium products"],
    "ideal_use_cases": ["Best for returning customers during holiday season"]
  }
}
```

### 2. `POST /leads/upload`

**Description**: Upload a leads CSV file.

**Form Data**:

- `file`: CSV with columns: `name`, `role`, `company`, `industry`, `location`, `linkedin_bio`

**Response**:

```json
{
  "status": "ok",
  "count": 5
}
```

### 3. `POST /score`

**Description**: Run scoring on uploaded leads.

**Response**:

```json
{
  "status": "ok",
  "count": 5
}
```

### 4. `GET /results`

**Description**: Retrieve scored leads as JSON.

**Example Response**:

```json
[
  {
    "name": "Alice Johnson",
    "role": "Marketing Manager",
    "company": "TechSolutions",
    "industry": "Software",
    "intent": "Low",
    "score": 20,
    "reasoning": "Heuristic: no strong buying signals."
  },
  {
    "name": "Bob Smith",
    "role": "CTO",
    "company": "InnoTech",
    "industry": "Technology",
    "intent": "High",
    "score": 70,
    "reasoning": "Heuristic: decision maker or strong buying signals."
  }
]
```

### 5. `GET /export_csv`

**Description**: Download scored leads as CSV.

**Local**:

```bash
curl -X GET "http://127.0.0.1:8000/export_csv" \
-H "accept: text/csv" -o scored_leads.csv
```

**On Render**:

```bash
curl -X GET "https://lead-scoring-backend-wyrt.onrender.com/export_csv" \
-H "accept: text/csv" -o scored_leads.csv
```

---

##  Scoring Logic

### Rule-Based Layer (0–50 points)

- **Role relevance**: decision maker (+20), influencer (+10), others (0)
- **Industry match**: exact ICP (+20), adjacent (+10), else (0)
- **Data completeness**: all fields present (+10)

### AI Layer (0–50 points)

- Sends prospect + offer info to OpenAI
- AI classifies intent: High (50), Medium (30), Low (10)
- Provides reasoning for transparency

**Final Score** = `rule_score + ai_points` (0–100)

---

##  Automation Script

`run_lead_scoring.sh` automates the full workflow:

```bash
./run_lead_scoring.sh
```

**Steps**:
- Upload leads CSV
- Post product/offer
- Score leads
- Export scored leads as CSV

---

##  Example Workflow (cURL)

### Create Offer

```bash
curl -X POST https://lead-scoring-backend-wyrt.onrender.com/offer \
-H "Content-Type: application/json" \
-d '{"name": "Special Discount", "value_props": ["10% off on all premium products"], "ideal_use_cases": ["Best for returning customers during holiday season"]}'
```

### Upload Leads

```bash
curl -X POST https://lead-scoring-backend-wyrt.onrender.com/leads/upload \
-H "accept: application/json" \
-H "Content-Type: multipart/form-data" \
-F "file=@leads.csv;type=text/csv"
```

### Score Leads

```bash
curl -X POST https://lead-scoring-backend-wyrt.onrender.com/score \
-H "accept: application/json"
```

### Get Results (JSON)

```bash
curl -X GET https://lead-scoring-backend-wyrt.onrender.com/results \
-H "accept: application/json"
```

### Export CSV

```bash
curl -X GET https://lead-scoring-backend-wyrt.onrender.com/export_csv \
-H "accept: text/csv" -o scored_leads.csv
```