# Hindi AI Video Generator

AI-powered Hindi video generator built with Streamlit.

## Pipeline

Topic
↓
Hindi Script
↓
Scene Planning
↓
Veo AI Video Generation
↓
Hindi TTS
↓
Captions
↓
Background Music
↓
FFmpeg
↓
MP4

## Features

- Hindi script generation
- AI scene planning
- AI-generated video clips
- Hindi narration
- Automatic captions
- Background music
- FFmpeg rendering
- 9:16 vertical videos
- 16:9 landscape videos
- 720p / 1080p output

## Required secrets

Add these in Streamlit Secrets:

OPENAI_API_KEY="your-openai-key"
GEMINI_API_KEY="your-gemini-key"

Optional:

TEXT_MODEL="gpt-5.6-luna"
TTS_MODEL="gpt-4o-mini-tts"
VEO_MODEL="veo-3.1-generate-preview"
