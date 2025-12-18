from fastapi import APIRouter, HTTPException
import os
from server.services.metrics import BearCartMetrics

router = APIRouter(prefix="/api", tags=["analytics"])

# Initialize metrics service (load data once)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, 'data', 'processed')

try:
    metrics_service = BearCartMetrics(data_dir=DATA_DIR)
except Exception as e:
    print(f"Error loading metrics: {e}")
    metrics_service = None

@router.get("/dashboard")
async def get_dashboard_data():
    if not metrics_service:
        raise HTTPException(status_code=500, detail="Metrics service not initialized. Run pipeline first.")
    
    try:
        data = metrics_service.get_dashboard_data()
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
