# Poem Short Generator 2

A Python pipeline that automatically generates daily news summaries, converts them into poetic stanzas, creates text-to-speech audio, and produces vertical videos (1080×1920) perfect for social media.

## Features

- 📰 **News Summarization**: Uses OpenAI GPT-4 to generate concise world news summaries
- ✍️ **Poetry Generation**: Converts news summaries into 3-stanza poems
- 🔊 **Text-to-Speech**: Generates audio narration using Piper TTS
- 🎬 **Video Creation**: Creates vertical videos with synced audio and captions
- 🎨 **Custom Backgrounds**: Supports multiple background images
- 📱 **Social Media Ready**: Outputs vertical 1080×1920 videos

## Project Structure

```
poem-short-generator-2/
├── main.py                 # Main pipeline orchestration
├── settings.py             # Configuration settings
├── requirements.txt       # Python dependencies
├── download_backgrounds.py # Script to download background images
├── poem/
│   ├── summarizer.py      # News summary generation
│   └── poem_writer.py     # Poem stanza generation
├── audio/
│   └── tts.py             # Piper TTS audio generation
├── video/
│   └── video_maker.py     # Video composition and assembly
├── assets/
│   └── backgrounds/       # Background images (add your own)
└── output/                 # Generated outputs (timestamped)
```

## Prerequisites

- Python 3.8 or higher
- OpenAI API key ([Get one here](https://platform.openai.com/api-keys))
- ffmpeg (required by MoviePy)

## Installation

1. **Clone the repository** (or download the project):
   ```bash
   git clone <your-repo-url>
   cd poem-short-generator-2
   ```

2. **Install Python dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Install Piper TTS**:
   ```bash
   pip install piper-tts
   ```
   
   The voice model will be automatically downloaded on first run.

4. **Install ffmpeg** (if not already installed):
   - **macOS**: `brew install ffmpeg`
   - **Linux**: `sudo apt-get install ffmpeg`
   - **Windows**: Download from [ffmpeg.org](https://ffmpeg.org/download.html)

5. **Set up your OpenAI API key**:
   - Copy `.env.example` to `.env`
   - Edit `.env` and add your API key:
     ```
     OPENAI_API_KEY=sk-your-actual-key-here
     ```

6. **Download background images** (optional):
   ```bash
   python download_backgrounds.py
   ```
   
   Or add your own images to `assets/backgrounds/` (JPG, PNG formats supported)

## Usage

Run the complete pipeline:

```bash
python main.py
# optional flags:
# --model gpt-4o-mini --tone "poetic insight" --backgrounds assets/backgrounds --output-dir output
```

The script will:
1. Generate a world news summary using OpenAI
2. Convert it to 3 poem stanzas
3. Generate audio files for each stanza
4. Create a vertical video with backgrounds and captions
5. Save everything to `output/YYYYMMDD_HHMMSS/`

### Output Structure

Each run creates a timestamped folder containing:
```
output/YYYYMMDD_HHMMSS/
├── summary.txt           # Generated news summary
├── stanzas.txt           # Generated poem stanzas
├── audio/
│   ├── stanza_1.wav
│   ├── stanza_2.wav
│   └── stanza_3.wav
└── video.mp4             # Final video output
```

## Configuration

Edit `settings.py` to customize:

- **OpenAI Model**: Change `OPENAI_MODEL` (default: "gpt-4")
- **Video Resolution**: Modify `VIDEO_WIDTH` and `VIDEO_HEIGHT` (default: 1080×1920)
- **Caption Styling**: Adjust font, size, color, position
- **Piper Voice**: Set `PIPER_VOICE_MODEL` or `PIPER_VOICE_PATH`

Or set environment variables in `.env`:
```
OPENAI_API_KEY=your-key
OPENAI_MODEL=gpt-4
PIPER_VOICE_MODEL=en_US-lessac-medium
```

## Requirements

See `requirements.txt` for full list. Key dependencies:
- `openai` - OpenAI API client
- `moviepy==1.0.3` - Video editing
- `Pillow>=9.0.0,<10.0.0` - Image processing
- `piper-tts` - Text-to-speech
- `python-dotenv` - Environment variable management
- `requests` - HTTP requests (for downloading backgrounds)

## Troubleshooting

### MoviePy Import Error
If you get `ModuleNotFoundError: No module named 'moviepy.editor'`:
```bash
pip install moviepy==1.0.3
```

### Pillow ANTIALIAS Error
If you get `AttributeError: module 'PIL.Image' has no attribute 'ANTIALIAS'`:
```bash
pip install "Pillow<10.0.0"
```

### Piper TTS Not Found
Ensure `piper-tts` is installed:
```bash
pip install piper-tts
```

The voice model will be downloaded automatically on first run.

### No Background Images
Add at least 3 images to `assets/backgrounds/` or run:
```bash
python download_backgrounds.py
```

## Future Enhancements

Potential improvements for website/app deployment:
- Web API using Flask/FastAPI
- Scheduled daily runs (cron/scheduler)
- Database storage for generated content
- User authentication and customization
- Mobile app integration
- Cloud storage for outputs

## License

[Add your license here]

## Contributing

[Add contribution guidelines if open-sourcing]

## Support

For issues or questions, please open an issue on GitHub.

