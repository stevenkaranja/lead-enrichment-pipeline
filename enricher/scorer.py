"""
ICP lead scoring — outputs 0–100 score + tier (Hot / Warm / Cold).
"""
import os


ICP_INDUSTRIES = [i.strip() for i in os.getenv("ICP_INDUSTRIES", "SaaS,Technology,Fintech").split(",")]
ICP_MIN_EMP = int(os.getenv("ICP_MIN_EMPLOYEES", "10"))
ICP_MAX_EMP = int(os.getenv("ICP_MAX_EMPLOYEES", "500"))

EMPLOYEE_RANGE_MAP = {
    "1-10": 5, "11-50": 30, "51-200": 100, "201-500": 350,
    "501-1000": 750, "1001-5000": 3000, "5001-10000": 7500, "10001+": 15000,
}


def score_lead(company: dict, contacts: list) -> dict:
    """
    Score a lead 0–100 based on ICP fit.
    Breakdown:
        - Industry match:    30 pts
        - Company size:      30 pts
        - Contact quality:   25 pts
        - Data completeness: 15 pts
    """
    score = 0
    reasons = []

    # Industry match (30 pts)
    industry = company.get("industry", "")
    if any(icp.lower() in industry.lower() for icp in ICP_INDUSTRIES):
        score += 30
        reasons.append(f"Industry match ({industry})")

    # Company size (30 pts)
    emp_range = company.get("employee_count", "")
    emp_count = EMPLOYEE_RANGE_MAP.get(emp_range, 0)
    if ICP_MIN_EMP <= emp_count <= ICP_MAX_EMP:
        score += 30
        reasons.append(f"Size match ({emp_range} employees)")
    elif emp_count > 0:
        score += 10
        reasons.append(f"Size outside ICP ({emp_range} employees)")

    # Contact quality (25 pts)
    if contacts:
        best_confidence = max((c.get("confidence", 0) for c in contacts), default=0)
        contact_score = int((best_confidence / 100) * 25)
        score += contact_score
        reasons.append(f"Best contact confidence: {best_confidence}%")
    else:
        reasons.append("No contacts found")

    # Data completeness (15 pts)
    filled = sum(1 for k in ["company_name", "industry", "country", "description"] if company.get(k))
    completeness_score = int((filled / 4) * 15)
    score += completeness_score

    # Determine tier
    if score >= 70:
        tier = "🔥 Hot"
    elif score >= 40:
        tier = "🟡 Warm"
    else:
        tier = "❄️ Cold"

    return {"score": score, "tier": tier, "reasons": "; ".join(reasons)}
