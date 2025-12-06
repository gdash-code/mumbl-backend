# Testing with Insomnia

Insomnia is a great alternative to Postman! You can use the same `mumbl-postman-collection.json` file.

## Installation

1. **Download Insomnia** (if you haven't already)
   - https://insomnia.rest/download

2. **Open Insomnia**

## Importing the Collection

### Method 1: Import File (Easiest)

1. Click the **Insomnia icon** (top left corner)
2. Select **Import/Export**
3. Click **Import Data**
4. Choose **From File**
5. Select: `mumbl-postman-collection.json`
6. Click **Scan**
7. Your collection will be imported automatically

### Method 2: Drag & Drop

1. Simply drag `mumbl-postman-collection.json` into Insomnia
2. It should automatically import

## Using the Collection in Insomnia

Once imported, you'll see your requests in the left sidebar:

```
📁 Mumbl Transcription API
  ├── Health Check
  ├── Transcribe Audio (M4A)
  └── Transcribe Audio (MP3)
```

### 1. Test Health Endpoint

1. Click **Health Check**
2. Click the **Send** button (or `Cmd+Enter`)
3. You should see:
   ```json
   {
     "ok": true
   }
   ```

### 2. Test Transcription

1. Click **Transcribe Audio (M4A)**
2. In the **Body** tab, you'll see a form with `file` field
3. Click the **file** field value area
4. Select **File** from the dropdown
5. Click **Choose File** and select your audio file
6. Click **Send** button
7. Wait 20-60 seconds for transcription

**Expected Response:**
```json
{
  "transcript": "your transcribed text here"
}
```

## Key Differences from Postman

| Feature | Insomnia | Postman |
|---------|----------|---------|
| Import Postman collections | ✅ Yes | ✅ Yes |
| Lightweight | ✅ Yes (smaller) | ❌ No (heavier) |
| Keyboard shortcuts | ✅ Better | ❌ Okay |
| Free tier | ✅ Full features | ⚠️ Limited |
| File upload in form data | ✅ Yes | ✅ Yes |

## Troubleshooting in Insomnia

### Request shows as "pending" forever
- **Solution**: Backend might be running slow for first transcription
- Check the backend is still running: `lsof -i :8000`

### "Connection refused"
- **Solution**: Start the backend
- Run: `nohup ./venv/bin/python -m uvicorn main:app --host 0.0.0.0 --port 8000 > server.log 2>&1 &`

### File field shows empty after selecting file
- **Solution**: This is normal in Insomnia - the file path is stored even if not visible
- Just click Send and it will work

### "422 Unprocessable Content"
- **Solution**: The `file` field name might be wrong
- Make sure the form field is named exactly `file` (not `audio` or other names)

## Pro Tips for Insomnia

1. **View Response as Pretty JSON**
   - Right-click response → **Format as JSON** (or auto-formats)

2. **View Timeline**
   - Bottom of response panel shows network timing
   - Useful to see how long transcription takes

3. **Save Responses**
   - Click the **disk icon** to save response for later

4. **Environment Variables**
   - Create environment with: `base_url` = `http://192.168.1.168:8000`
   - Then use `{{ base_url }}/health` in requests

5. **Request History**
   - Insomnia saves all your requests
   - Click **Timeline** in left sidebar to view history

## Next Steps

Once you confirm everything works in Insomnia:

1. ✅ Backend is working
2. ✅ API is responding correctly  
3. ⚠️ iOS app audio recording needs fixing
4. 📱 Then test iOS app end-to-end

For iOS audio recording issues, see the main `SETUP.md` file.
