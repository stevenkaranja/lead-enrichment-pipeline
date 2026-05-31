# Lead Enrichment Pipeline

> Company domain in → enriched, scored, outbound-ready leads out.

A Python pipeline that takes a list of company domains, enriches them with firmographic data and decision-maker contacts, scores each lead against your ICP, and outputs a clean CSV ready for HubSpot import.

---

## What It Does

```
Input: stripe.com, notion.so, hubspot.com...
         ↓
  [Company Enrichment]   — industry, size, country, description (Clearbit)
         ↓
  [Contact Discovery]    — decision-maker emails + confidence score (Hunter.io)
         ↓
  [ICP Scoring]          — 0–100 score + Hot / Warm / Cold tier
         ↓
Output: enriched_leads.csv (sorted by ICP score, ready for HubSpot)
```

---

## Stack

| Layer | Tool |
|---|---|
| Company enrichment | Clearbit API (free tier) |
| Contact discovery | Hunter.io API (free tier: 25/month) |
| Lead scoring | Custom Python ICP model |
| Data processing | pandas |
| CLI output | rich |

---

## Quickstart

```bash
# 1. Clone
git clone https://github.com/stevenkaranja/lead-enrichment-pipeline
cd lead-enrichment-pipeline

# 2. Install
pip install -r requirements.txt

# 3. Configure
cp .env.example .env
# Add your Hunter.io and Clearbit API keys to .env

# 4. Run on a CSV
python main.py --input data/sample_input.csv --output data/output.csv

# 5. Or enrich a single domain
python main.py --domain stripe.com
```

---

## Input Format

A CSV with a `domain`, `company`, or `website` column:

```csv
domain
stripe.com
notion.so
hubspot.com
```

---

## Output Fields

| Field | Description |
|---|---|
| `company_name` | Company name |
| `industry` | Industry category |
| `employee_count` | Employee range |
| `country` | HQ country |
| `contact_name` | Best decision-maker found |
| `contact_email` | Their email address |
| `contact_position` | Their job title |
| `email_confidence` | Hunter.io confidence % |
| `icp_score` | 0–100 ICP fit score |
| `icp_tier` | 🔥 Hot / 🟡 Warm / ❄️ Cold |

---

## ICP Scoring Logic

| Factor | Weight |
|---|---|
| Industry match | 30 pts |
| Company size (employees) | 30 pts |
| Contact email confidence | 25 pts |
| Data completeness | 15 pts |

Configure your ICP in `.env`:
```
ICP_INDUSTRIES=SaaS,Technology,Fintech
ICP_MIN_EMPLOYEES=10
ICP_MAX_EMPLOYEES=500
```

---

## API Keys (Free Tiers)

- **Hunter.io** — [hunter.io](https://hunter.io) — 25 free searches/month
- **Clearbit** — [clearbit.com/free](https://clearbit.com/free) — free enrichment tier

The pipeline runs without API keys (uses domain-parse fallback) but results will be limited.

---

## Author

**Stephen Karanja** — AI Automation & GTM Systems Engineer  
[stephenkaranja.vercel.app](https://stephenkaranja.vercel.app) · [LinkedIn](https://linkedin.com/in/steven-karanja)
