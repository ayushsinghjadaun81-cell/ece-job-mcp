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
