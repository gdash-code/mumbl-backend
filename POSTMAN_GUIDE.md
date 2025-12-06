# Testing with Postman

This guide shows how to import and use the Mumbl Transcription API collection in Postman.

## Installation

### Option 1: Import from File (Recommended)

1. **Download Postman** (if you haven't already)
   - https://www.postman.com/downloads/

2. **Open Postman** and click **Import**
   - Top left corner → "Import" button

3. **Select the collection file**
   - Choose: `mumbl-postman-collection.json`
   - Click **Import**

4. **Your collection is ready!**
   - You'll see "Mumbl Transcription API" in your Collections panel

### Option 2: Manual Setup

If you prefer to create it manually:

1. Create a new Request (`+ New` → `Request`)
2. Name it "Health Check"
3. Set method to `GET`
4. Enter URL: `http://192.168.1.168:8000/health`
5. Click **Send**

## Using the Collection

### 1. Health Check (Verify Backend is Running)

1. Select **Health Check** from the collection
2. Click **Send**
3. You should see:
   ```json
   {
     "ok": true
   }
   ```

### 2. Transcribe Audio (Upload & Transcribe)

**Before you start:**
- Make sure you have an audio file (MP3, M4A, WAV, etc.)
- Files must be > 1KB in size
- Transcription can take 20-60 seconds

**Steps:**

1. Select **Transcribe Audio (M4A)** or **Transcribe Audio (MP3)**
2. Click the **Body** tab
3. You'll see the **form-data** section with a `file` field
4. Click **Select Files** and choose your audio file
5. Click **Send**

**Example Response:**
```json
{
  "transcript": "hello world this is a test"
}
```

**Common Responses:**

| Status | Meaning |
|--------|---------|
| 200 | Success! Transcription complete |
| 400 | File too small (< 1KB) or corrupted |
| 422 | Missing `file` field in request |
| 500 | Server error (check logs) |

## Testing Tips

### Generate Test Audio Files

If you need test audio files, run these commands:

```bash
# Generate 5-second sine wave (MP3)
ffmpeg -f lavfi -i sine=f=1000:d=5 -q:a 9 -acodec libmp3lame /tmp/test_audio.mp3 -y

# Generate 5-second sine wave (M4A)
ffmpeg -f lavfi -i sine=f=1000:d=5 -c:a aac -b:a 128k /tmp/test_speech.m4a -y

# Record your own audio (macOS)
afrecord -d 10 -c 1 -b 16 -s 44100 -f ALAC /tmp/my_audio.m4a
```

### Test with Speech Recognition

For better testing, record actual speech with:
```bash
afrecord -d 10 -c 1 -b 16 -s 44100 -f ALAC /tmp/my_speech.m4a
```

Then upload in Postman to see the transcript.

## Troubleshooting

### "Connection refused"
- Backend is not running
- Start it: `nohup ./venv/bin/python -m uvicorn main:app --host 0.0.0.0 --port 8000 > server.log 2>&1 &`

### "File too small"
- Your audio file is < 1KB
- Generate a longer test file (5+ seconds recommended)

### "ffmpeg decode failed"
- Your audio file is corrupted
- Try generating a new test file with ffmpeg

### "Timeout after 60 seconds"
- Transcription is taking too long
- Try a shorter audio file first (10-15 seconds)
- Or increase timeout in Postman: **Settings** → increase request timeout

## Environment Variables (Optional)

You can create Postman environment variables for the base URL:

1. Click **Environments** in the left sidebar
2. Create new environment
3. Add variable:
   - Name: `base_url`
   - Value: `http://192.168.1.168:8000`

Then update URLs in requests to use: `{{base_url}}/health`

## Next Steps

Once Postman tests work:
1. ✅ Backend is confirmed working
2. ✅ API format is correct
3. ⚠️ iOS app needs to: fix audio recording to save complete M4A files
4. 📱 Then test end-to-end on simulator/device

See `/mumbl-backend copy/SETUP.md` for more backend information.
