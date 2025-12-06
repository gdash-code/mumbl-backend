#!/usr/bin/env python3
"""
Simple test script to verify the transcription API works
without needing the iOS simulator.
"""

import requests
import sys
import time
from pathlib import Path

# Configuration
BACKEND_URL = "http://192.168.1.168:8000"
UPLOADS_DIR = Path("uploads")

def test_health():
    """Test the /health endpoint"""
    print("=" * 60)
    print("Testing /health endpoint...")
    print("=" * 60)
    try:
        response = requests.get(f"{BACKEND_URL}/health", timeout=5)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_transcribe(audio_file: Path):
    """Test the /transcribe endpoint with an audio file"""
    print("\n" + "=" * 60)
    print(f"Testing /transcribe endpoint with: {audio_file.name}")
    print("=" * 60)
    
    if not audio_file.exists():
        print(f"❌ File not found: {audio_file}")
        return False
    
    file_size = audio_file.stat().st_size
    print(f"📁 File size: {file_size / 1024:.1f} KB")
    
    try:
        print("⏳ Uploading and transcribing (this may take 20-60 seconds)...")
        start_time = time.time()
        
        with open(audio_file, "rb") as f:
            files = {"file": (audio_file.name, f, "audio/mp4")}
            response = requests.post(
                f"{BACKEND_URL}/transcribe",
                files=files,
                timeout=120  # 2 minute timeout for transcription
            )
        
        elapsed = time.time() - start_time
        print(f"⏱️  Time taken: {elapsed:.1f} seconds")
        print(f"✅ Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"📝 Transcript: {result.get('transcript', 'N/A')}")
            return True
        else:
            print(f"❌ Error: {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        print("❌ Request timeout - transcription took too long")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    """Run all tests"""
    print("\n🎙️  MUMBL Transcription API Test Suite\n")
    
    # Test health
    if not test_health():
        print("\n❌ Backend is not responding. Make sure it's running:")
        print("   nohup ./venv/bin/python -m uvicorn main:app --host 0.0.0.0 --port 8000 > server.log 2>&1 &")
        sys.exit(1)
    
    print("\n✅ Backend is healthy!\n")
    
    # Find audio files
    if not UPLOADS_DIR.exists():
        print(f"❌ Uploads directory not found: {UPLOADS_DIR}")
        sys.exit(1)
    
    audio_files = list(UPLOADS_DIR.glob("*.m4a"))
    if not audio_files:
        print(f"❌ No .m4a files found in {UPLOADS_DIR}")
        sys.exit(1)
    
    print(f"Found {len(audio_files)} audio files\n")
    
    # Test with first audio file
    success = test_transcribe(audio_files[0])
    
    # Summary
    print("\n" + "=" * 60)
    if success:
        print("✅ All tests passed!")
    else:
        print("❌ Some tests failed. Check the output above.")
    print("=" * 60 + "\n")
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
