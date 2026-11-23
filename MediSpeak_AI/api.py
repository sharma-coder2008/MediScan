from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

try:
    from .ai_reader import read_medicines_image
except ImportError:
    from ai_reader import read_medicines_image

BASE_DIR = Path(__file__).resolve().parent
FRONTEND_DIR = BASE_DIR.parent / "frontend"

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ScanRequest(BaseModel):
    image: str
    language: str = "English"


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/api/identify-medicine")
async def identify_medicine_endpoint(req: ScanRequest):
    try:
        return read_medicines_image(req.image, req.language)
    except Exception as exc:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(exc))


# Serve the real dashboard + history pages from the same domain
if FRONTEND_DIR.exists():
    app.mount("/frontend", StaticFiles(directory=str(FRONTEND_DIR), html=True), name="frontend")

    @app.get("/")
    def home():
        return RedirectResponse(url="/frontend/dashboard/dashboard.html")
else:
    @app.get("/")
    def home():
        return {"status": "MediScan API running", "docs": "/docs"}
