"""Flask web application for the Poem Short Generator."""

import os
import sys
import threading
import json
from datetime import datetime
from pathlib import Path
from flask import Flask, render_template, request, jsonify, send_file, url_for

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

import settings

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY', 'dev-secret-key-change-in-production')

# Track generation status
generation_status = {
    'is_generating': False,
    'progress': '',
    'error': None,
    'last_video': None
}


def get_all_videos():
    """Scan output directory and return all generated videos with metadata."""
    videos = []
    output_dir = settings.OUTPUT_BASE_DIR
    
    if not output_dir.exists():
        return videos
    
    # Get all timestamped directories
    for folder in sorted(output_dir.iterdir(), reverse=True):
        if not folder.is_dir():
            continue
        
        # Skip 'latest' symlink
        if folder.name == 'latest':
            continue
        
        # Find video file in folder
        video_file = None
        for f in folder.iterdir():
            if f.suffix.lower() in ['.mp4', '.mov', '.avi', '.webm']:
                video_file = f
                break
        
        if not video_file:
            continue
        
        # Read metadata
        summary = ''
        stanzas = ''
        summary_path = folder / 'summary.txt'
        stanzas_path = folder / 'stanzas.txt'
        
        if summary_path.exists():
            summary = summary_path.read_text(encoding='utf-8')
        if stanzas_path.exists():
            stanzas = stanzas_path.read_text(encoding='utf-8')
        
        # Parse timestamp from folder name
        try:
            timestamp = datetime.strptime(folder.name.split('_')[0], '%Y%m%d')
            date_str = timestamp.strftime('%B %d, %Y')
        except (ValueError, IndexError):
            date_str = folder.name
        
        # Extract title from video filename
        title = video_file.stem
        # Remove date prefix if present
        if title.startswith('202'):
            parts = title.split('_', 1)
            if len(parts) > 1:
                title = parts[1].replace('-', ' ').title()
            else:
                title = 'Daily Poem'
        
        videos.append({
            'id': folder.name,
            'title': title,
            'date': date_str,
            'timestamp': folder.name,
            'video_path': str(video_file.relative_to(settings.BASE_DIR)),
            'video_filename': video_file.name,
            'summary': summary[:200] + '...' if len(summary) > 200 else summary,
            'full_summary': summary,
            'stanzas': stanzas,
            'folder': str(folder)
        })
    
    return videos


def run_generation(tone, stanzas_count, model):
    """Run the poem generation pipeline in background."""
    global generation_status
    
    try:
        generation_status['progress'] = 'Starting generation...'
        
        # Import here to avoid circular imports
        from poem.summarizer import get_world_news_summary, generate_short_title
        from poem.poem_writer import make_stanzas
        from audio.tts import generate_audio_files
        from video.video_maker import build_video
        import random
        import re
        
        # Create output directory
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_dir = settings.OUTPUT_BASE_DIR / timestamp
        output_dir.mkdir(parents=True, exist_ok=True)
        audio_dir = output_dir / "audio"
        audio_dir.mkdir(exist_ok=True)
        
        # Step 1: Get news summary
        generation_status['progress'] = 'Step 1/4: Fetching world news...'
        summary = get_world_news_summary(model=model)
        (output_dir / "summary.txt").write_text(summary, encoding='utf-8')
        
        # Step 2: Generate poem
        generation_status['progress'] = 'Step 2/4: Writing poem stanzas...'
        stanzas = make_stanzas(summary, tone=tone, model=model, stanza_count=stanzas_count)
        stanzas_text = "\n\n".join(f"Stanza {i}:\n{stanza}" for i, stanza in enumerate(stanzas, 1))
        (output_dir / "stanzas.txt").write_text(stanzas_text, encoding='utf-8')
        
        # Generate title
        title = generate_short_title(summary, model=model)
        safe_title = re.sub(r"[^a-z0-9]+", "-", title.lower().strip()).strip("-") or "video"
        
        # Step 3: Generate audio
        generation_status['progress'] = 'Step 3/4: Generating audio narration...'
        audio_paths = generate_audio_files(stanzas, str(audio_dir))
        
        # Step 4: Build video
        generation_status['progress'] = 'Step 4/4: Building video...'
        
        # Select backgrounds
        bg_dir = settings.ASSETS_BACKGROUNDS_DIR
        image_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.gif'}
        image_files = [
            str(f) for f in bg_dir.iterdir()
            if f.is_file() and f.suffix.lower() in image_extensions
        ]
        
        if len(image_files) < stanzas_count:
            selected = image_files * ((stanzas_count // len(image_files)) + 1)
            background_paths = selected[:stanzas_count]
        else:
            background_paths = random.sample(image_files, stanzas_count)
        
        # Build video
        date_prefix = timestamp.split("_")[0]
        video_filename = f"{date_prefix}_{safe_title}.{settings.OUTPUT_VIDEO_FORMAT}"
        video_path = output_dir / video_filename
        
        build_video(
            backgrounds=background_paths,
            stanzas=stanzas,
            audio_paths=audio_paths,
            output_path=str(video_path)
        )
        
        generation_status['progress'] = 'Complete!'
        generation_status['last_video'] = timestamp
        
    except Exception as e:
        generation_status['error'] = str(e)
        generation_status['progress'] = f'Error: {e}'
    finally:
        generation_status['is_generating'] = False


@app.route('/')
def index():
    """Homepage - display video gallery."""
    videos = get_all_videos()
    return render_template('index.html', videos=videos)


@app.route('/video/<video_id>')
def video_detail(video_id):
    """Display a single video with full details."""
    videos = get_all_videos()
    video = next((v for v in videos if v['id'] == video_id), None)
    if not video:
        return "Video not found", 404
    return render_template('video_detail.html', video=video)


@app.route('/generate', methods=['GET'])
def generate_page():
    """Display the generation form."""
    return render_template('generate.html', 
                         status=generation_status,
                         default_model=settings.OPENAI_MODEL)


@app.route('/api/generate', methods=['POST'])
def api_generate():
    """Start video generation (async)."""
    global generation_status
    
    if generation_status['is_generating']:
        return jsonify({'error': 'Generation already in progress'}), 400
    
    # Get parameters from request
    data = request.get_json() or {}
    tone = data.get('tone', 'poetic insight')
    stanzas_count = int(data.get('stanzas', 7))
    model = data.get('model', settings.OPENAI_MODEL)
    
    # Reset status
    generation_status = {
        'is_generating': True,
        'progress': 'Initializing...',
        'error': None,
        'last_video': None
    }
    
    # Run generation in background thread
    thread = threading.Thread(target=run_generation, args=(tone, stanzas_count, model))
    thread.daemon = True
    thread.start()
    
    return jsonify({'status': 'started'})


@app.route('/api/status')
def api_status():
    """Get current generation status."""
    return jsonify(generation_status)


@app.route('/download/<video_id>')
def download_video(video_id):
    """Download a video file."""
    videos = get_all_videos()
    video = next((v for v in videos if v['id'] == video_id), None)
    
    if not video:
        return "Video not found", 404
    
    video_path = settings.BASE_DIR / video['video_path']
    if not video_path.exists():
        return "Video file not found", 404
    
    return send_file(
        video_path,
        as_attachment=True,
        download_name=video['video_filename']
    )


@app.route('/serve/<video_id>')
def serve_video(video_id):
    """Serve video file for playback."""
    videos = get_all_videos()
    video = next((v for v in videos if v['id'] == video_id), None)
    
    if not video:
        return "Video not found", 404
    
    video_path = settings.BASE_DIR / video['video_path']
    if not video_path.exists():
        return "Video file not found", 404
    
    return send_file(video_path, mimetype='video/mp4')


@app.route('/api/videos')
def api_videos():
    """API endpoint to get all videos as JSON."""
    videos = get_all_videos()
    return jsonify(videos)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
