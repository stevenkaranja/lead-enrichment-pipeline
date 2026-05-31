"""
Company enrichment via Clearbit + fallback web scraping.
"""
import os
import requests


def enrich_company(domain: str) -> dict:
    """
    Enrich a company by domain.
    Returns: name, industry, employee_count, description, country, linkedin_url
    """
    result = {
        "domain": domain,
        "company_name": "",
        "industry": "",
        "employee_count": "",
        "description": "",
        "country": "",
        "linkedin_url": "",
        "enrichment_source": "",
    }

    # Try Clearbit first
    api_key = os.getenv("CLEARBIT_API_KEY", "")
    if api_key:
        try:
            resp = requests.get(
                f"https://company.clearbit.com/v2/companies/find?domain={domain}",
                auth=(api_key, ""),
                timeout=10,
            )
            if resp.status_code == 200:
                data = resp.json()
                result.update({
                    "company_name": data.get("name", ""),
                    "industry": data.get("category", {}).get("industry", ""),
                    "employee_count": data.get("metrics", {}).get("employeesRange", ""),
                    "description": (data.get("description", "") or "")[:200],
                    "country": data.get("geo", {}).get("country", ""),
                    "linkedin_url": data.get("linkedin", {}).get("handle", ""),
                    "enrichment_source": "clearbit",
                })
                return result
        except Exception:
            pass

    # Fallback: derive company name from domain
    name = domain.split(".")[0].replace("-", " ").title()
    result.update({
        "company_name": name,
        "enrichment_source": "domain_parse",
    })
    return result
