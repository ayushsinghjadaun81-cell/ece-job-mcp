import os
import httpx


JOOBLE_API_KEY = os.getenv("JOOBLE_API_KEY")


# Strong signals for the kinds of ECE jobs we want.
POSITIVE_KEYWORDS = {
    "embedded": 5,
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
        if keyword in text:
            score += points

    for keyword, points in NEGATIVE_KEYWORDS.items():
        if keyword in text:
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
        score = score_job(job)

        job["relevance_score"] = score

        scored_jobs.append(job)

    # Keep only jobs with meaningful ECE relevance.
    relevant_jobs = [
        job
        for job in scored_jobs
        if job["relevance_score"] >= 5
    ]

    # Highest relevance first.
    relevant_jobs.sort(
        key=lambda job: job["relevance_score"],
        reverse=True,
    )

    return relevant_jobs
