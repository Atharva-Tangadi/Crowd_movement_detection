from fastapi import APIRouter, UploadFile, File, BackgroundTasks, WebSocket, WebSocketDisconnect
from fastapi.responses import StreamingResponse, JSONResponse
from app.services.video_processor import processor
import shutil
import os
import asyncio

router = APIRouter()

# Ensure videos dir exists
os.makedirs("videos", exist_ok=True)

@router.post("/process/start/camera")
async def start_camera():
    success = processor.start_camera()
    if not success:
        return JSONResponse(
            status_code=400, 
            content={"message": "Webcam unavailable. Please check if your camera is connected/enabled or try uploading a video instead."}
        )
    return {"message": "Camera processing started"}

@router.post("/process/start/video")
async def start_video(file: UploadFile = File(...)):
    file_path = f"videos/{file.filename}"
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    success = processor.start_video(file_path)
    if not success:
        return JSONResponse(
            status_code=400,
            content={"message": f"Could not read video file {file.filename}. Check file format."}
        )
    return {"message": f"Processing started for {file.filename}"}

@router.post("/process/stop")
async def stop_processing():
    processor.stop()
    return {"message": "Processing stopped"}

@router.get("/video/stream")
async def video_stream():
    """Streams MJPEG frames."""
    if not processor.is_running:
        return JSONResponse(status_code=400, content={"message": "Processor is not running"})
    return StreamingResponse(processor.generate_frames(), media_type="multipart/x-mixed-replace; boundary=frame")

@router.websocket("/ws/stats")
async def websocket_stats(websocket: WebSocket):
    """Streams real-time stats via WebSocket."""
    await websocket.accept()
    try:
        while True:
            if processor.is_running:
                await websocket.send_json(processor.stats)
            else:
                await websocket.send_json({"status": "Stopped", "fps": 0, "crowd": {"count": 0, "status": "LOW", "peak": 0}, "movement": {"dominant": "Mixed/None", "counts": {}}})
            await asyncio.sleep(1.0) # Send updates every second
    except WebSocketDisconnect:
        print("Client disconnected from stats WebSocket")
