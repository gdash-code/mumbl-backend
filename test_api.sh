#!/bin/bash
# Simple bash script to test the Mumbl transcription API
# Usage: ./test_api.sh [path_to_audio_file]

set -e

BACKEND_URL="http://192.168.1.168:8000"
AUDIO_FILE="${1:-/tmp/test_speech.m4a}"

echo "🎙️  Mumbl Transcription API Test"
echo "=================================="
echo ""

# Color codes
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test health endpoint
echo "1️⃣  Testing health endpoint..."
HEALTH_RESPONSE=$(curl -s -w "\n%{http_code}" "$BACKEND_URL/health")
HTTP_CODE=$(echo "$HEALTH_RESPONSE" | tail -n1)
BODY=$(echo "$HEALTH_RESPONSE" | sed '$d')

if [ "$HTTP_CODE" = "200" ]; then
    echo -e "${GREEN}✅ Backend is healthy!${NC}"
    echo "   Response: $BODY"
else
    echo -e "${RED}❌ Backend not responding${NC}"
    echo "   Status: $HTTP_CODE"
    echo "   Make sure backend is running:"
    echo "   nohup ./venv/bin/python -m uvicorn main:app --host 0.0.0.0 --port 8000 > server.log 2>&1 &"
    exit 1
fi

echo ""
echo "2️⃣  Testing transcription endpoint..."

# Check if audio file exists
if [ ! -f "$AUDIO_FILE" ]; then
    echo -e "${RED}❌ Audio file not found: $AUDIO_FILE${NC}"
    echo ""
    echo "Generate a test audio file:"
    echo "  ffmpeg -f lavfi -i sine=f=1000:d=5 -q:a 9 -acodec libmp3lame /tmp/test_audio.mp3 -y"
    echo "  ffmpeg -f lavfi -i sine=f=1000:d=5 -c:a aac -b:a 128k /tmp/test_speech.m4a -y"
    exit 1
fi

FILE_SIZE=$(stat -f%z "$AUDIO_FILE" 2>/dev/null || stat -c%s "$AUDIO_FILE" 2>/dev/null)
FILE_SIZE_KB=$(echo "scale=1; $FILE_SIZE / 1024" | bc)

echo "   File: $(basename $AUDIO_FILE)"
echo "   Size: ${FILE_SIZE_KB} KB"
echo ""
echo -e "${YELLOW}⏳ Transcribing (this may take 20-60 seconds)...${NC}"

# Upload and transcribe
START_TIME=$(date +%s)
TRANSCRIBE_RESPONSE=$(curl -s -w "\n%{http_code}" \
  -F "file=@$AUDIO_FILE" \
  "$BACKEND_URL/transcribe")

END_TIME=$(date +%s)
ELAPSED=$((END_TIME - START_TIME))

HTTP_CODE=$(echo "$TRANSCRIBE_RESPONSE" | tail -n1)
BODY=$(echo "$TRANSCRIBE_RESPONSE" | sed '$d')

echo ""
echo "⏱️  Time elapsed: ${ELAPSED}s"
echo ""

if [ "$HTTP_CODE" = "200" ]; then
    echo -e "${GREEN}✅ Transcription successful!${NC}"
    echo "   Response:"
    echo "   $BODY" | jq . 2>/dev/null || echo "   $BODY"
else
    echo -e "${RED}❌ Transcription failed${NC}"
    echo "   Status: $HTTP_CODE"
    echo "   Error:"
    echo "   $BODY" | jq . 2>/dev/null || echo "   $BODY"
    exit 1
fi

echo ""
echo "=================================="
echo -e "${GREEN}All tests passed! ✅${NC}"
echo "=================================="
echo ""
