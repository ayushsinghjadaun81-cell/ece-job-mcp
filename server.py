from mcp.server.fastmcp import FastMCP

mcp = FastMCP(
    "ECE Job Tools",
    stateless_http=True,
    json_response=True,
)

# Version 1 deliberately uses a tiny in-memory dataset.
# We will replace this with real job-source retrieval after
# Claude successfully connects to the MCP server.
JOBS = [
    {
        "title": "Embedded Systems Intern",
        "company": "Example Robotics",
        "location": "Remote, India",
        "salary": "₹8,000/month",
        "url": "https://example.com/jobs/embedded-intern",
        "skills": ["Arduino", "Embedded Systems", "C", "Sensors"],
    },
    {
        "title": "IoT Intern",
        "company": "Example IoT Labs",
        "location": "Remote, India",
        "salary": "₹12,000/month",
        "url": "https://example.com/jobs/iot-intern",
        "skills": ["IoT", "Arduino", "Sensors", "Microcontrollers"],
    },
]


@mcp.tool()
def search_jobs(
    keywords: list[str],
    location: str = "India",
) -> list[dict]:
    """Search the demo job dataset by keywords and location."""
    wanted = {k.strip().lower() for k in keywords if k.strip()}
    loc = location.lower()

    results = []
    for job in JOBS:
        searchable = " ".join([
            job["title"],
            job["company"],
            job["location"],
            *job["skills"],
        ]).lower()

        keyword_match = not wanted or any(k in searchable for k in wanted)
        location_match = not loc or loc in job["location"].lower()

        if keyword_match and location_match:
            results.append(job)

    return results


@mcp.tool()
def server_status() -> dict:
    """Return basic information about this MCP server."""
    return {
        "name": "ECE Job Tools",
        "version": "0.1.0",
        "status": "online",
        "tools": ["search_jobs", "server_status"],
    }
app = mcp.streamable_http_app()

    
