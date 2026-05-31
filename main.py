"""
Lead Enrichment Pipeline
========================
Company name/domain in → enriched + scored leads out.

Usage:
    python main.py --input data/sample_input.csv --output data/output.csv
    python main.py --domain stripe.com
"""
import argparse
import csv
import os
import sys
from datetime import datetime
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv
from rich.console import Console
from rich.progress import track
from rich.table import Table

from enricher import enrich_company, find_contacts, score_lead

load_dotenv()
console = Console()


def process_domain(domain: str) -> dict:
    """Run the full enrichment pipeline for a single domain."""
    domain = domain.lower().strip().replace("https://", "").replace("http://", "").replace("www.", "").split("/")[0]

    company = enrich_company(domain)
    contacts = find_contacts(domain)
    score = score_lead(company, contacts)

    # Pick best contact
    best_contact = contacts[0] if contacts else {}

    return {
        "domain": domain,
        "company_name": company.get("company_name", ""),
        "industry": company.get("industry", ""),
        "employee_count": company.get("employee_count", ""),
        "country": company.get("country", ""),
        "description": company.get("description", ""),
        "linkedin_url": company.get("linkedin_url", ""),
        "contact_name": f"{best_contact.get('first_name', '')} {best_contact.get('last_name', '')}".strip(),
        "contact_email": best_contact.get("email", ""),
        "contact_position": best_contact.get("position", ""),
        "email_confidence": best_contact.get("confidence", ""),
        "total_contacts_found": len(contacts),
        "icp_score": score.get("score", 0),
        "icp_tier": score.get("tier", ""),
        "score_reasons": score.get("reasons", ""),
        "enrichment_source": company.get("enrichment_source", ""),
        "enriched_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
    }


def run_from_csv(input_path: str, output_path: str):
    """Process a CSV file of domains/company names."""
    df = pd.read_csv(input_path)

    # Accept 'domain', 'company', or 'website' as column name
    col = next((c for c in df.columns if c.lower() in ["domain", "company", "website", "url"]), df.columns[0])
    domains = df[col].dropna().tolist()

    console.print(f"\n[bold yellow]Lead Enrichment Pipeline[/bold yellow]")
    console.print(f"Processing [cyan]{len(domains)}[/cyan] companies...\n")

    results = []
    for domain in track(domains, description="Enriching leads..."):
        try:
            results.append(process_domain(str(domain)))
        except Exception as e:
            console.print(f"[red]Error processing {domain}: {e}[/red]")

    out_df = pd.DataFrame(results)
    out_df = out_df.sort_values("icp_score", ascending=False)
    out_df.to_csv(output_path, index=False)

    # Print summary table
    table = Table(title=f"\nEnrichment Results — Top Leads")
    table.add_column("Company", style="cyan")
    table.add_column("Contact", style="white")
    table.add_column("Email", style="white")
    table.add_column("Score", style="yellow")
    table.add_column("Tier", style="bold")

    for _, row in out_df.head(10).iterrows():
        table.add_row(
            row["company_name"] or row["domain"],
            row["contact_name"] or "—",
            row["contact_email"] or "—",
            str(row["icp_score"]),
            row["icp_tier"],
        )

    console.print(table)
    console.print(f"\n[green]✓[/green] Output saved to [cyan]{output_path}[/cyan]")
    console.print(f"[green]✓[/green] {len([r for r in results if r['icp_score'] >= 70])} Hot leads found\n")


def run_single(domain: str):
    """Enrich a single domain and print results."""
    console.print(f"\n[bold yellow]Enriching:[/bold yellow] {domain}\n")
    result = process_domain(domain)

    table = Table(show_header=False, box=None, padding=(0, 2))
    table.add_column("Field", style="dim")
    table.add_column("Value", style="cyan")

    for key, value in result.items():
        if value and key not in ["enriched_at", "enrichment_source"]:
            table.add_row(key.replace("_", " ").title(), str(value))

    console.print(table)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Lead Enrichment Pipeline")
    parser.add_argument("--input", help="Input CSV file path")
    parser.add_argument("--output", help="Output CSV file path", default="data/output.csv")
    parser.add_argument("--domain", help="Single domain to enrich")
    args = parser.parse_args()

    if args.domain:
        run_single(args.domain)
    elif args.input:
        run_from_csv(args.input, args.output)
    else:
        console.print("[red]Error:[/red] Provide --input <csv> or --domain <domain>")
        console.print("Example: python main.py --domain stripe.com")
        console.print("Example: python main.py --input data/sample_input.csv")
        sys.exit(1)
