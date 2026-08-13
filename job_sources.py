import os
import httpx


JOOBLE_API_KEY = os.getenv("JOOBLE_API_KEY")


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
    """Search Jooble using multiple focused queries and remove duplicates."""

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
            or job.get("url")
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

    return unique_jobs
