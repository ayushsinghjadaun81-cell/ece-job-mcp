from mcp.server.fastmcp import FastMCP
from mcp.server.transport_security import TransportSecuritySettings
from job_sources import search_jooble
security = TransportSecuritySettings(
    enable_dns_rebinding_protection=True,
    allowed_hosts=[
        "ece-job-mcp.onrender.com",
        "ece-job-mcp.onrender.com:*",
    ],
    allowed_origins=[
        "https://claude.ai",
    ],
)

mcp = FastMCP(
    "ECE Job Tools",
    stateless_http=True,
    json_response=True,
    transport_security=security,
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
async def search_jobs(
    keywords: list[str],
    location: str = "India",
) -> list[dict]:
    """Search real jobs using Jooble."""

    query = " ".join(keywords)

    return await search_jooble(
        keywords=query,
        location=location,
    ) 


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

    
