import os
import re
import httpx
import hashlib


JOOBLE_API_KEY = os.getenv("JOOBLE_API_KEY")


# Strong signals for the kinds of ECE jobs we want.
POSITIVE_KEYWORDS = {
    "firmware": 5,
    "microcontroller": 5,
    "embedded systems": 5,
    "embedded software": 5,
    "embedded c": 5,
    "embedded c++": 5,
    "stm32": 4,
    "arm": 3,
    "rtos": 4,
    "freertos": 4,
    "arduino": 3,
    "esp32": 3,
    "iot": 3,
    "pcb": 4,
    "pcb design": 5,
    "altium": 4,
    "kicad": 4,
    "easyeda": 4,
    "hardware": 2,
    "electronics": 2,
    "fpga": 4,
    "verilog": 4,
    "vhdl": 4,
    "vlsi": 3,
    "digital design": 3,
    "analog design": 3,
    "circuit design": 4,
    "bare metal": 4,
    "device driver": 4,
    "low level": 3,
}


# Strong signals that usually indicate irrelevant software/business roles.
NEGATIVE_KEYWORDS = {
    "salesforce": 6,
    "servicenow": 6,
    "sap": 5,
    "frontend": 5,
    "backend": 5,
    "full stack": 5,
    "react": 5,
    "angular": 5,
    "node.js": 5,
    "java backend": 5,
    "web developer": 5,
    "wordpress": 5,
    "php developer": 5,
    "devops": 4,
    "cloud engineer": 4,
    "data engineer": 4,
    "data scientist": 4,
    "business analyst": 4,
    "technical support": 3,
}
def contains_keyword(text: str, keyword: str) -> bool:
    """Check for a whole word or phrase, avoiding accidental substring matches."""

    pattern = rf"\b{re.escape(keyword)}\b"

    return re.search(pattern, text) is not None
def has_strong_ece_signal(job: dict) -> bool:
    """Check whether a job contains a genuine ECE/embedded technical signal."""

    text = " ".join(
        str(job.get(field, ""))
        for field in [
            "title",
            "snippet",
        ]
    ).lower()

    strong_signals = [
        "firmware",
        "microcontroller",
        "embedded software",
        "embedded systems",
        "pcb design",
        "circuit design",
        "stm32",
        "esp32",
        "rtos",
        "freertos",
        "fpga",
        "verilog",
        "vhdl",
        "arduino",
        "iot",
        "electronics engineer",
    ]

    return any(
        contains_keyword(text, signal)
        for signal in strong_signals
    )
def score_job(job: dict) -> int:
    """
    Score a job based on its title, company and description.

    Higher score = stronger ECE/embedded relevance.
    """

    text = " ".join(
        str(job.get(field, ""))
        for field in [
            "title",
            "company",
            "snippet",
        ]
    ).lower()

    score = 0

    for keyword, points in POSITIVE_KEYWORDS.items():
        if contains_keyword(text, keyword):
            score += points

    for keyword, points in NEGATIVE_KEYWORDS.items():
        if contains_keyword(text, keyword):
            score -= points

    # The job title deserves extra importance.
    title = str(job.get("title", "")).lower()

    if "embedded" in title:
        score += 5

    if "firmware" in title:
        score += 5

    if "hardware" in title:
        score += 3

    if "pcb" in title:
        score += 5

    if "electronics" in title:
        score += 3

    if "microcontroller" in title:
        score += 5

    return score
def score_eligibility(job: dict) -> int:
    """
    Estimate whether the job is suitable for a diploma/fresher candidate.
    """

    text = " ".join(
        str(job.get(field, ""))
        for field in [
            "title",
            "company",
            "snippet",
        ]
    ).lower()

    score = 0

    positive_signals = {
        "fresher": 5,
        "freshers": 5,
        "entry level": 5,
        "entry-level": 5,
        "junior": 4,
        "trainee": 5,
        "graduate trainee": 6,
        "graduate engineer trainee": 6,
        "intern": 4,
        "internship": 4,
        "0-1 years": 5,
        "0-2 years": 5,
        "diploma": 5,
    }

    negative_signals = {
        "senior": 6,
        "staff": 8,
        "principal": 8,
        "lead": 6,
        "manager": 7,
        "director": 8,
        "5+ years": 7,
        "7+ years": 8,
        "10+ years": 8,
    }

    for keyword, points in positive_signals.items():
        if contains_keyword(text, keyword):
            score += points

    for keyword, points in negative_signals.items():
        if contains_keyword(text, keyword):
            score -= points

    return score

async def search_jooble(
    keywords: str,
    location: str = "India",
) -> list[dict]:
    """Search Jooble for real job listings."""

    if not JOOBLE_API_KEY:
        raise RuntimeError("JOOBLE_API_KEY is not configured")

    url = f"https://jooble.org/api/{JOOBLE_API_KEY}"

    payload = {
        "keywords": keywords,
        "location": location,
        "page": "1",
        "ResultOnPage": "30",
        "companysearch": "false",
    }

    async with httpx.AsyncClient(timeout=20) as client:
        response = await client.post(url, json=payload)

    response.raise_for_status()

    data = response.json()
    return data.get("jobs", [])


async def search_multiple_jooble(
    keywords: list[str],
    location: str = "India",
) -> list[dict]:
    """
    Search Jooble using multiple focused queries,
    remove duplicates, score relevance, and filter noise.
    """

    all_jobs = []

    for keyword in keywords:
        keyword = keyword.strip()

        if not keyword:
            continue

        jobs = await search_jooble(
            keywords=keyword,
            location=location,
        )

        for job in jobs:
            raw_text = " | ".join([
                str(job.get("title", "")),
                str(job.get("company", "")),
                str(job.get("location", "")),
                str(job.get("snippet", "")),
            ])

            job["_debug_search_keyword"] = keyword
            job["_debug_signature"] = hashlib.sha256(
                raw_text.encode("utf-8")
            ).hexdigest()

        all_jobs.extend(jobs)

    # Remove duplicate jobs.
    unique_jobs = []
    seen = set()

    for job in all_jobs:
        job_id = (
            job.get("id")
            or job.get("link")
            or (
                job.get("title", ""),
                job.get("company", ""),
                job.get("location", ""),
            )
        )

        if job_id in seen:
            continue

        seen.add(job_id)
        unique_jobs.append(job)

    # Score every unique job.
    scored_jobs = []

    for job in unique_jobs:
        relevance_score = score_job(job)
        eligibility_score = score_eligibility(job)

        job["relevance_score"] = relevance_score
        job["eligibility_score"] = eligibility_score
        job["total_score"] = (
            relevance_score + eligibility_score
        )

        scored_jobs.append(job)

    # Diagnostic: inspect every scored job before filtering.
    for job in scored_jobs:
        ece_signal = has_strong_ece_signal(job)
        relevance_ok = job["relevance_score"] >= 5
        eligibility_ok = job["eligibility_score"] >= 0

        job["_debug_ece_signal"] = ece_signal
        job["_debug_relevance_ok"] = relevance_ok
        job["_debug_eligibility_ok"] = eligibility_ok
        job["_debug_passes_filter"] = (
            ece_signal
            and relevance_ok
            and eligibility_ok
        )

    # Highest total score first.
    scored_jobs.sort(
        key=lambda job: job["total_score"],
        reverse=True,
    )

    return scored_jobs


     
