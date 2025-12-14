# Mumbl Backend Setup Guide

## Overview
This is a FastAPI backend for the Mumbl iOS app that provides audio transcription using OpenAI's Whisper model (via faster-whisper).

## Prerequisites

- Python 3.13+
- FFmpeg (for audio processing)
- Virtual environment (venv)

### Install FFmpeg (macOS)
```bash
brew install ffmpeg
```

## Installation

### 1. Clone the Repository
```bash
git clone https://github.com/gdash-code/mumbl-backend.git
cd mumbl-backend
```

### 2. Create Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Install Additional Dependencies (Python 3.13 Compatibility)
```bash
pip install audioread
```

## Running the Server

### Quick Start
```bash
./venv/bin/python -m uvicorn main:app --host 0.0.0.0 --port 8000
```

### Production (Background Process)
```bash
cd "/path/to/mumbl-backend"
nohup ./venv/bin/python -m uvicorn main:app --host 0.0.0.0 --port 8000 > server.log 2>&1 &
```

### Development (With Auto-Reload)
```bash
./venv/bin/python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## Environment Variables

Optional configuration via environment variables:

```bash
# Whisper Model Size (default: "base")
# Options: tiny, base, small, medium, large-v3
export WHISPER_MODEL=base

# Device (default: "cpu")
# Options: cpu, cuda
export WHISPER_DEVICE=cpu

# Compute Type (default: "int8")
# Options: int8 (CPU), float16 (CUDA)
export WHISPER_COMPUTE=int8
```

Example with environment variables:
```bash
WHISPER_MODEL=base WHISPER_DEVICE=cpu ./venv/bin/python -m uvicorn main:app --host 0.0.0.0 --port 8000
```

## API Endpoints

### Health Check
**Endpoint:** `GET /health`

**Response:**
```json
{"ok": true}
```

**Example:**
```bash
curl http://127.0.0.1:8000/health
```

### Transcribe Audio
**Endpoint:** `POST /transcribe`

**Request:**
- Content-Type: `multipart/form-data`
- Form field: `file` (audio file in M4A, MP3, WAV format)

**Response:**
```json
{"transcript": "transcribed text here"}
```

**Example with curl:**
```bash
curl -X POST -F "file=@audio.m4a" http://127.0.0.1:8000/audio
```

## Testing Endpoints

### Using curl
```bash
# Health check
curl http://127.0.0.1:8000/health

# Transcribe (replace audio.m4a with your file)
curl -X POST -F "file=@audio.m4a" http://127.0.0.1:8000/transcribe
```

### Using Python
```python
import requests

# Health check
response = requests.get("http://127.0.0.1:8000/health")
print(response.json())

# Transcribe
with open("audio.m4a", "rb") as f:
    files = {"file": f}
    response = requests.post("http://127.0.0.1:8000/transcribe", files=files)
    print(response.json())
```

## Accessing from iOS Simulator/Device

### On Same Network (Real Device)
1. Find your Mac's local IP:
   ```bash
   ifconfig | grep "inet " | grep -v 127.0.0.1
   ```
2. Update your iOS app's APIClient to use: `http://<YOUR_IP>:8000`

### Simulator on Same Mac
Use: `http://127.0.0.1:8000`

### Simulator from Another Mac
1. Ensure backend is running with `--host 0.0.0.0`
2. Use your Mac's network IP in the iOS app

## Troubleshooting

### Backend Won't Start
```bash
# Check if port 8000 is already in use
lsof -i :8000

# Kill the existing process (replace PID)
kill -9 <PID>
```

### ModuleNotFoundError: No module named 'pyaudioop'
This is a Python 3.13 compatibility issue. Solution:
```bash
pip install audioread
```

### FFmpeg Not Found
```bash
# Ensure FFmpeg is installed
brew install ffmpeg

# Verify installation
which ffmpeg
```

### Slow Transcription
- Use a smaller model: `WHISPER_MODEL=tiny`
- Use GPU if available: `WHISPER_DEVICE=cuda`
- Increase compute precision: `WHISPER_COMPUTE=float16`

### Connection Refused from iOS
- Verify backend is running: `curl http://<YOUR_IP>:8000/health`
- Check firewall settings
- Ensure iOS device is on the same network as Mac
- Verify correct IP in APIClient.swift

## Project Structure

```
mumbl-backend/
├── main.py                  # FastAPI app & endpoints
├── whisper_transcriber.py   # Whisper transcription logic
├── requirements.txt         # Python dependencies
├── SETUP.md                 # This file
├── BACKEND_INTEGRATION.md   # iOS integration guide
└── uploads/                 # Temporary audio files
```

## Requirements

All dependencies are listed in `requirements.txt`:
- fastapi - Web framework
- uvicorn - ASGI server
- python-multipart - File upload support
- pydub - Audio processing
- ffmpeg-python - FFmpeg integration
- faster-whisper - Speech-to-text model
- audioread - Audio reading (Python 3.13 support)

## CORS Configuration

The backend has CORS enabled to allow requests from any origin:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

For production, restrict this to specific origins:
```python
allow_origins=["https://yourdomain.com"]
```

## Performance Tips

1. **First Run**: The Whisper model is downloaded on first use (~140MB for "base")
2. **Model Selection**: 
   - `tiny` - Fast but less accurate
   - `base` - Good balance (recommended)
   - `small` - Better accuracy, slower
   - `large-v3` - Best accuracy, slow
3. **GPU**: Use CUDA if available: `WHISPER_DEVICE=cuda`

## Monitoring

### View Server Logs
```bash
# Real-time logs
tail -f "/path/to/mumbl-backend/server.log"

# Last 50 lines
tail -50 "/path/to/mumbl-backend/server.log"
```

### Check Running Processes
```bash
ps aux | grep uvicorn
```

### Stop Server
```bash
# If running in background, find and kill
lsof -i :8000
kill -9 <PID>

# Or if you have the process ID from background job
kill %1
```

## Documentation

- [FastAPI Docs](https://fastapi.tiangolo.com)
- [Faster Whisper](https://github.com/SYSTRAN/faster-whisper)
- [OpenAI Whisper](https://github.com/openai/whisper)
- [iOS Integration Guide](./BACKEND_INTEGRATION.md)

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Review the logs: `tail -f server.log`
3. Test endpoints with curl
4. Check GitHub issues: https://github.com/gdash-code/mumbl-backend/issues

---

**Last Updated:** December 6, 2025
