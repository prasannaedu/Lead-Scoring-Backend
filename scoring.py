from pydantic import BaseModel
from typing import List, Dict, Any
import os, re

from openai import OpenAI

class OfferModel(BaseModel):
    name: str
    value_props: List[str]
    ideal_use_cases: List[str]

class ScoringEngine:
    def __init__(self, offer: Dict[str, Any]):
        # Offer can be dict or OfferModel
        if isinstance(offer, OfferModel):
            self.offer = offer.dict()
        else:
            self.offer = offer

        # Example ICP: take first ideal_use_case as exact ICP
        self.icp = (self.offer.get("ideal_use_cases") or [None])[0]

        # Setup OpenAI client if key exists
        api_key = os.getenv("OPENAI_API_KEY")
        self.client = OpenAI(api_key=api_key) if api_key else None

    # ---------------- Rule Layer ---------------- #
    def _role_score(self, role: str) -> int:
        if not role:
            return 0
        role_lower = role.lower()
        decision_keywords = [
            "head","director","vp","vice","chief","cfo","cto",
            "ceo","founder","owner","co-founder","president","lead"
        ]
        influencer_keywords = [
            "manager","senior","principal","specialist",
            "analyst","consultant","engineer","developer"
        ]
        if any(k in role_lower for k in decision_keywords):
            return 20
        if any(k in role_lower for k in influencer_keywords):
            return 10
        return 0

    def _industry_score(self, industry: str) -> int:
        if not industry or not self.icp:
            return 0
        ind = industry.lower().strip()
        icp = self.icp.lower().strip()
        if ind == icp:
            return 20
        if icp in ind or ind in icp:
            return 10
        return 0

    def _completeness_score(self, lead: Dict[str, str]) -> int:
        required = ["name","role","company","industry","location","linkedin_bio"]
        for k in required:
            if not lead.get(k):
                return 0
        return 10

    def _rule_score(self, lead: Dict[str, str]) -> int:
        return (
            self._role_score(lead.get("role"))
            + self._industry_score(lead.get("industry"))
            + self._completeness_score(lead)
        )

    # ---------------- AI Layer ---------------- #
    def _build_prompt(self, lead: Dict[str,str]) -> str:
        return f"""
You are a sales-assistant classifier.

Product/Offer: {self.offer.get('name')}
Value props: {', '.join(self.offer.get('value_props') or [])}
Ideal use cases: {', '.join(self.offer.get('ideal_use_cases') or [])}

Prospect:
  Name: {lead.get('name')}
  Role: {lead.get('role')}
  Company: {lead.get('company')}
  Industry: {lead.get('industry')}
  Location: {lead.get('location')}
  LinkedIn bio: {lead.get('linkedin_bio')}

Task: Classify the prospect intent as High, Medium, or Low. 
Respond in this format:
Intent: <High/Medium/Low>
Reason: <1–2 sentence explanation>
"""

    def _call_ai(self, lead: Dict[str, str]) -> Dict[str, str]:
        if self.client:
            try:
                resp = self.client.chat.completions.create(
                    model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
                    messages=[{"role": "user", "content": self._build_prompt(lead)}],
                    temperature=0
                )
                text = resp.choices[0].message.content.strip()

                intent = "Medium"
                reasoning = text
                m = re.search(r"Intent\s*[:\-]\s*(High|Medium|Low)", text, re.IGNORECASE)
                if m:
                    intent = m.group(1).title()
                return {"intent": intent, "reasoning": reasoning}

            except Exception as e:
                print("OpenAI call failed, using heuristic:", e)

        # -------- Heuristic fallback -------- #
        bio = (lead.get("linkedin_bio") or "").lower()
        role = (lead.get("role") or "").lower()
        high_keywords = ["looking for","interested in","evaluate","purchase","buy",
                         "decision","budget","ready to buy"]
        med_keywords = ["curious","exploring","considering","research","trial",
                        "pilot","planning"]

        if any(k in bio for k in high_keywords) or any(k in role for k in ["head","director","vp","cto","ceo","founder"]):
            return {"intent": "High", "reasoning": "Heuristic: decision maker or strong buying signals."}
        elif any(k in bio for k in med_keywords):
            return {"intent": "Medium", "reasoning": "Heuristic: exploratory language found."}
        else:
            return {"intent": "Low", "reasoning": "Heuristic: no strong buying signals."}

    # ---------------- Public Method ---------------- #
    def score_lead(self, lead: Dict[str,str]) -> Dict[str,Any]:
        rule = self._rule_score(lead)
        ai_resp = self._call_ai(lead)
        mapping = {"High": 50, "Medium": 30, "Low": 10}
        ai_points = mapping.get(ai_resp.get("intent","Medium"), 30)
        final_score = rule + ai_points
        return {
            "name": lead.get("name"),
            "role": lead.get("role"),
            "company": lead.get("company"),
            "industry": lead.get("industry"),
            "intent": ai_resp.get("intent"),
            "score": final_score,
            "reasoning": ai_resp.get("reasoning"),
            "rule_score": rule,
            "ai_points": ai_points
        }
