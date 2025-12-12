# Poem Short Generator 2

A Python pipeline that automatically generates daily news summaries, converts them into poetic stanzas, creates text-to-speech audio, and produces vertical videos (1080×1920) perfect for social media.

**Now with a web interface!** 🌐

## Features

- 📰 **News Summarization**: Uses OpenAI GPT-4 to generate concise world news summaries
- ✍️ **Poetry Generation**: Converts news summaries into 3-stanza poems
- 🔊 **Text-to-Speech**: Generates audio narration using Piper TTS
- 🎬 **Video Creation**: Creates vertical videos with synced audio and captions
- 🎨 **Custom Backgrounds**: Supports multiple background images
- 📱 **Social Media Ready**: Outputs vertical 1080×1920 videos
- 🌐 **Web Interface**: Browse videos, generate on-demand, customize settings, and download

## Project Structure

```
poem-short-generator-2/
├── main.py                 # Main pipeline orchestration (CLI)
├── run_web.py              # Web application entry point
├── settings.py             # Configuration settings
├── requirements.txt        # Python dependencies
├── download_backgrounds.py # Script to download background images
├── poem/
│   ├── summarizer.py       # News summary generation
│   └── poem_writer.py      # Poem stanza generation
├── audio/
│   └── tts.py              # Piper TTS audio generation
├── video/
│   └── video_maker.py      # Video composition and assembly
├── webapp/
│   ├── app.py              # Flask web application
│   ├── templates/          # HTML templates
│   └── static/             # CSS and JavaScript
├── assets/
│   └── backgrounds/        # Background images (add your own)
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

### Web App (Recommended)

Start the web server:

```bash
python run_web.py
```

Then open http://localhost:5000 in your browser.

**Web App Features:**
- 📺 **Video Gallery**: Browse all generated poems with video playback
- ⚡ **On-Demand Generation**: Generate new poems with custom settings
- ⚙️ **Settings**: Choose tone (poetic, somber, upbeat, etc.), stanza count, and AI model
- 📥 **Download**: Download any video directly from the gallery

**Environment Variables (optional):**
```bash
FLASK_HOST=0.0.0.0    # Host to bind to (default: 0.0.0.0)
FLASK_PORT=5000       # Port to run on (default: 5000)
FLASK_DEBUG=true      # Debug mode (default: true)
```

### Command Line (CLI)

Run the complete pipeline from command line:

```bash
python main.py
# optional flags:
# --model gpt-4o-mini --tone "poetic insight" --backgrounds assets/backgrounds --output-dir output
```

### Daily automation (cron, 8:00 AM ET)

1) Use the provided runner script:
```
run_daily.sh
```
It runs the pipeline, logs to `cron.log`, and updates `output/latest` to point to the newest run.

2) Add a cron entry (macOS/Linux):
```
crontab -e
```
Add this line:
```
0 8 * * * TZ=America/New_York /Users/peterhagen/Desktop/poem-short-generator-2/run_daily.sh
```

3) Optional: adjust Python binary or venv in `run_daily.sh`:
- Edit `PYTHON_BIN` (or uncomment the venv `source` line).
- Change tone/stanzas flags as desired.

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
- `flask` - Web framework
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

## Deployment

### Local Development
```bash
python run_web.py
```

### Production (Gunicorn)
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 webapp.app:app
```

### AWS Deployment
The app is ready for deployment on AWS:
- **EC2**: Run with Gunicorn behind Nginx
- **Elastic Beanstalk**: Use the included `requirements.txt`
- **Lambda + API Gateway**: For serverless (requires adaptation)

### Docker (optional)
```dockerfile
FROM python:3.11-slim
WORKDIR /app
RUN apt-get update && apt-get install -y ffmpeg && rm -rf /var/lib/apt/lists/*
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt piper-tts
COPY . .
EXPOSE 5000
CMD ["gunicorn", "-w", "2", "-b", "0.0.0.0:5000", "webapp.app:app"]
```

## Future Enhancements

Potential improvements:
- Database storage for generated content
- User authentication and customization
- Mobile app integration
- Cloud storage for outputs (S3)
- WebSocket for real-time generation progress

## License

[Add your license here]

## Contributing

[Add contribution guidelines if open-sourcing]

## Support

For issues or questions, please open an issue on GitHub.

