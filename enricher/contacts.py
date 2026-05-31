"""
Contact / email discovery via Hunter.io API.
Free tier: 25 searches/month — sign up at hunter.io
"""
import os
import requests


def find_contacts(domain: str, limit: int = 3) -> list[dict]:
    """
    Find decision-maker contacts at a company domain.
    Returns list of: first_name, last_name, email, position, confidence
    """
    api_key = os.getenv("HUNTER_API_KEY", "")
    if not api_key:
        return [{"email": f"contact@{domain}", "position": "Unknown", "confidence": 0, "source": "placeholder"}]

    try:
        resp = requests.get(
            "https://api.hunter.io/v2/domain-search",
            params={
                "domain": domain,
                "api_key": api_key,
                "limit": limit,
                "type": "personal",
                "seniority": "senior,executive,director",
            },
            timeout=10,
        )
        if resp.status_code == 200:
            emails = resp.json().get("data", {}).get("emails", [])
            return [
                {
                    "first_name": e.get("first_name", ""),
                    "last_name": e.get("last_name", ""),
                    "email": e.get("value", ""),
                    "position": e.get("position", ""),
                    "confidence": e.get("confidence", 0),
                    "source": "hunter",
                }
                for e in emails
            ]
    except Exception:
        pass

    return []
