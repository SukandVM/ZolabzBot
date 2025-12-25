import asyncio
import io
from typing import List, Tuple
from contextlib import asynccontextmanager
import cv2
import numpy as np
import whisper
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import soundfile as sf

# Initialize models globally
cascade_classifier = cv2.CascadeClassifier()
whisper_model = None

class Faces(BaseModel):
    """Pydantic model for face detection results"""
    faces: List[Tuple[int, int, int, int]]

class Transcription(BaseModel):
    """Pydantic model for speech transcription results"""
    text: str
    language: str

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Modern FastAPI lifespan event handler"""
    global whisper_model
    
    # Startup: Load models
    print("Loading models...")
    
    # Load face detection classifier
    cascade_path = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
    success = cascade_classifier.load(cascade_path)
    if not success:
        raise RuntimeError(f"Failed to load cascade classifier from {cascade_path}")
    print("✓ Face detection model loaded")
    
    # Load Whisper model
    print("Loading Whisper model (this may take a moment)...")
    whisper_model = whisper.load_model("base")  # Change to 'tiny', 'small', 'medium', or 'large'
    print("✓ Whisper model loaded")
    
    yield
    
    # Shutdown
    print("Shutting down...")

app = FastAPI(lifespan=lifespan)

# Serve static files
app.mount("/static", StaticFiles(directory="."), name="static")

async def receive_video(websocket: WebSocket, queue: asyncio.Queue):
    """Receive image bytes from WebSocket and add to queue"""
    bytes_data = await websocket.receive_bytes()
    try:
        queue.put_nowait(bytes_data)
    except asyncio.QueueFull:
        try:
            queue.get_nowait()
            queue.put_nowait(bytes_data)
        except:
            pass

async def detect_faces(websocket: WebSocket, queue: asyncio.Queue):
    """Process images from queue and detect faces"""
    while True:
        try:
            bytes_data = await queue.get()
            
            # Decode image
            data = np.frombuffer(bytes_data, dtype=np.uint8)
            img = cv2.imdecode(data, cv2.IMREAD_COLOR)
            
            if img is None:
                continue
            
            # Convert to grayscale for face detection
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            
            # Detect faces
            faces = cascade_classifier.detectMultiScale(
                gray,
                scaleFactor=1.1,
                minNeighbors=5,
                minSize=(30, 30)
            )
            
            # Prepare response
            if len(faces) > 0:
                faces_output = Faces(faces=faces.tolist())
            else:
                faces_output = Faces(faces=[])
            
            # Send results back to client
            await websocket.send_json(faces_output.model_dump())
            
        except asyncio.CancelledError:
            break
        except Exception as e:
            print(f"Error in detect_faces: {e}")
            break

@app.websocket("/face-detection")
async def face_detection(websocket: WebSocket):
    """WebSocket endpoint for face detection"""
    await websocket.accept()
    print("Face detection WebSocket connected")
    
    queue: asyncio.Queue = asyncio.Queue(maxsize=10)
    detect_task = asyncio.create_task(detect_faces(websocket, queue))
    
    try:
        while True:
            await receive_video(websocket, queue)
    except WebSocketDisconnect:
        print("Face detection WebSocket disconnected")
        detect_task.cancel()
        try:
            await detect_task
        except asyncio.CancelledError:
            pass
    except Exception as e:
        print(f"Error in face_detection: {e}")
        detect_task.cancel()
    finally:
        try:
            await websocket.close()
        except:
            pass

@app.websocket("/speech-recognition")
async def speech_recognition(websocket: WebSocket):
    """WebSocket endpoint for speech recognition using Whisper"""
    await websocket.accept()
    print("Speech recognition WebSocket connected")
    
    try:
        while True:
            # Receive audio data
            audio_bytes = await websocket.receive_bytes()
            
            try:
                # Convert bytes to audio array
                audio_io = io.BytesIO(audio_bytes)
                audio_data, sample_rate = sf.read(audio_io)
                
                # Convert to float32 and ensure mono
                if len(audio_data.shape) > 1:
                    audio_data = audio_data.mean(axis=1)
                audio_data = audio_data.astype(np.float32)
                
                # Transcribe with Whisper
                result = whisper_model.transcribe(audio_data, fp16=False)
                
                # Send transcription back
                transcription = Transcription(
                    text=result["text"].strip(),
                    language=result.get("language", "unknown")
                )
                
                await websocket.send_json(transcription.model_dump())
                print(f"Transcribed: {transcription.text}")
                
            except Exception as e:
                print(f"Error processing audio: {e}")
                await websocket.send_json({
                    "text": "",
                    "language": "error",
                    "error": str(e)
                })
    
    except WebSocketDisconnect:
        print("Speech recognition WebSocket disconnected")
    except Exception as e:
        print(f"Error in speech_recognition: {e}")
    finally:
        try:
            await websocket.close()
        except:
            pass

@app.get("/")
async def root():
    """Serve the main HTML page"""
    return FileResponse("index.html")

if __name__ == "__main__":
    import uvicorn
    print("Starting Face Detection + Speech Recognition server")
    print("Server will be available at: http://localhost:8000")
    uvicorn.run(app, host="0.0.0.0", port=8000)