import os
import sys
import json
import requests
import google.generativeai as genai

# Read environment variables
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
TAVILY_API_KEY = os.environ.get("TAVILY_API_KEY")

TARGET_NAME = os.environ.get("TARGET_NAME", "Target Enterprise")
STAKEHOLDER_TYPE = os.environ.get("STAKEHOLDER_TYPE", "OEM")
SECTOR = os.environ.get("SECTOR", "Manufacturing")
STATE = os.environ.get("STATE", "Pan-India")

def search_tavily(query):
    if not TAVILY_API_KEY:
        return "No Tavily API Key provided."
    url = "https://api.tavily.com/search"
    payload = {
        "api_key": TAVILY_API_KEY,
        "query": query,
        "search_depth": "advanced",
        "max_results": 4
    }
    try:
        res = requests.post(url, json=payload, timeout=25)
        data = res.json()
        snippets = [r.get("content", "") for r in data.get("results", [])]
        return "\n\n".join(snippets)
    except Exception as e:
        return f"Error during web research: {e}"

def generate_intelligence():
    # 1. Targeted live web query
    search_query = f"{TARGET_NAME} {SECTOR} supplier quality vendor manual ESG sustainability {STATE}"
    intel_data = search_tavily(search_query)

    # 2. Configure Gemini
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel("gemini-1.5-flash")

    system_prompt = f"""
You are the Principal Lead for Institutional Strategy at the National Division for Industry Excellence (NDIE), Quality Council of India (QCI).

INPUT PARAMETERS:
- Target Entity: {TARGET_NAME}
- Stakeholder Category: {STAKEHOLDER_TYPE} (Options: OEM, MSME, Trade Body/Association, DIC/DFO, Industrial Cluster)
- Sector: {SECTOR}
- State/Region: {STATE}

LIVE WEB INTEL EXTRACTED:
{intel_data}

Generate an exhaustive, highly structured institutional dossier formatted in clean Markdown.

STRUCTURE YOUR OUTPUT INTO THESE EXACT SECTIONS:

# 1. EXECUTIVE DIAGNOSTIC & STAKEHOLDER MAPPING
- Entity Profile & Industry Footprint
- Core Quality, Supply Chain, or Operational Friction Points (Based on the intel and sector realities)
- Target Leadership Personas to Approach (Titles like Head of Supplier Quality, VP Procurement, President, or DIC GM)

# 2. SCHEME VALUE MAPPING (ZED & LEAN ALIGNMENT)
- Direct mapping to Zero Defect Zero Effect (ZED) parameters (Bronze/Silver/Gold) and Competitive (LEAN) schemes.
- Central Financial Subsidies applicable (80% Micro, 60% Small, 50% Medium, plus 10% special category add-ons; 90% LEAN implementation).
- State Policy Top-up & Incentives specific to {STATE} (if applicable).
- Bank Financial Concessions (Interest subventions of 0.25%-0.50% across SBI, PNB, BoB, etc., plus processing fee waivers).

# 3. 4-TOUCH STAKEHOLDER OUTREACH JOURNEY
Tailor tone strictly to {STAKEHOLDER_TYPE}:
- Touch 1 (Day 1 - Formal Institutional Letter / Email): High-level, official, policy-backed, proposing an executive meeting or joint roadmap.
- Touch 2 (Day 3 - Mobile-Optimized Executive Snippet): 4-sentence WhatsApp/InMail briefing focused on direct financial/supply chain ROI.
- Touch 3 (Day 7 - Value Add Memo): A structured 1-page business case outlining defect reduction and audit fee savings.
- Touch 4 (Day 14 - Formal Consultation Invitation): Official invite to a QCI/NDIE diagnostic consultation or roundtable.

# 4. INTERNAL MEETING CHEAT-SHEET
- Top 3 Probable Objections this stakeholder will raise.
- Institutional Counter-Arguments & Proof Points (QCI handholding, OEM mandate trends, subsidy payback).
- Recommended Co-branded Agenda / Next Step.

Tone: Authoritative, institutional, policy-grounded, non-commercial.
"""
    response = model.generate_content(system_prompt)
    return response.text

if __name__ == "__main__":
    dossier = generate_intelligence()
    
    # Save output to markdown file
    clean_name = TARGET_NAME.lower().replace(" ", "_")
    filename = f"dossier_{clean_name}.md"
    
    with open(filename, "w", encoding="utf-8") as f:
        f.write(dossier)
        
    print(f"Successfully generated {filename}")
