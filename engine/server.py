"""Engine HTTP server. The old JobManager server was broken (see docs/AUDIT.md); the app now lives in relicon.api."""
from relicon.api import app  # noqa: F401

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("server:app", host="0.0.0.0", port=8000)
