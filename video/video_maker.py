"""Create vertical video from components using moviepy."""

import logging
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from moviepy.editor import (
    ImageClip, CompositeVideoClip, AudioFileClip, concatenate_videoclips
)
import settings

logger = logging.getLogger(__name__)


def build_video(
    backgrounds: list[str],
    stanzas: list[str],
    audio_paths: list[str],
    output_path: str
) -> str:
    """
    Creates vertical video (1080×1920) with synced audio and captions.
    
    Args:
        backgrounds: List of background image file paths (one per stanza)
        stanzas: List of stanza text strings
        audio_paths: List of audio file paths (one per stanza)
        output_path: Path for final output video
    
    Returns:
        Path to generated video file
    
    Raises:
        ValueError: If inputs are invalid or mismatched.
        RuntimeError: If video generation fails.
    """
    # Validate inputs
    if len(stanzas) != len(audio_paths):
        raise ValueError(f"Mismatch: {len(stanzas)} stanzas but {len(audio_paths)} audio files")
    
    if len(backgrounds) < len(stanzas):
        raise ValueError(f"Not enough backgrounds: {len(backgrounds)} backgrounds for {len(stanzas)} stanzas")
    
    # Ensure output directory exists
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    # Validate all files exist
    for i, audio_path in enumerate(audio_paths, 1):
        if not Path(audio_path).exists():
            raise ValueError(f"Audio file not found: {audio_path}")
    
    for i, bg_path in enumerate(backgrounds[:len(stanzas)], 1):
        if not Path(bg_path).exists():
            raise ValueError(f"Background image not found: {bg_path}")
    
    try:
        logger.info(f"Building video with {len(stanzas)} stanzas...")
        
        # Create video clips for each stanza
        video_clips = []
        for i, (stanza, audio_path, bg_path) in enumerate(zip(stanzas, audio_paths, backgrounds), 1):
            logger.info(f"Creating video clip {i}/{len(stanzas)}...")
            clip = _create_stanza_clip(stanza, audio_path, bg_path, i)
            video_clips.append(clip)
        
        # Concatenate all clips
        logger.info("Concatenating video clips...")
        final_video = concatenate_videoclips(video_clips, method="compose")
        
        # Write video file
        logger.info(f"Writing video to {output_path}...")
        final_video.write_videofile(
            str(output_path),
            fps=settings.VIDEO_FPS,
            codec=settings.VIDEO_CODEC,
            audio_codec="aac",
            preset="medium",
            logger=None  # Suppress moviepy's verbose logging
        )
        
        # Clean up
        final_video.close()
        for clip in video_clips:
            clip.close()
        
        logger.info(f"Successfully created video: {output_path}")
        return str(output_path)
        
    except Exception as e:
        logger.error(f"Failed to build video: {e}")
        raise RuntimeError(f"Video generation failed: {e}") from e


def _create_stanza_clip(
    stanza: str,
    audio_path: str,
    background_path: str,
    stanza_number: int
) -> CompositeVideoClip:
    """
    Create a single video clip for one stanza.
    
    Args:
        stanza: Stanza text
        audio_path: Path to audio file
        background_path: Path to background image
        stanza_number: Stanza number (for logging)
    
    Returns:
        CompositeVideoClip with background, text, and audio
    """
    # Load audio to get duration
    audio_clip = AudioFileClip(audio_path)
    duration = audio_clip.duration
    
    # Load and prepare background image
    bg_clip = ImageClip(background_path)
    bg_clip = bg_clip.resize((settings.VIDEO_WIDTH, settings.VIDEO_HEIGHT))
    bg_clip = bg_clip.set_duration(duration)
    bg_clip = bg_clip.set_fps(settings.VIDEO_FPS)
    
    # Create text overlay
    text_clip = _create_text_clip(stanza, duration)
    
    # Composite background and text
    video_clip = CompositeVideoClip([bg_clip, text_clip])
    
    # Add audio
    video_clip = video_clip.set_audio(audio_clip)
    
    return video_clip


def _create_text_clip(text: str, duration: float) -> ImageClip:
    """
    Create a text clip using PIL (no ImageMagick required).
    
    Args:
        text: Text to display
        duration: Duration of the clip
    
    Returns:
        ImageClip with formatted text
    """
    # Clean text - preserve line breaks for poetry
    clean_text = text.strip()
    
    # Calculate font size based on text length and video dimensions
    font_size = _calculate_font_size(clean_text)
    
    # Try to load font, fallback to default
    try:
        font = ImageFont.truetype(settings.CAPTION_FONT, font_size)
    except (OSError, IOError):
        try:
            # Try common system fonts
            font_paths = [
                "/System/Library/Fonts/Helvetica.ttc",
                "/System/Library/Fonts/Arial.ttf",
                "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
            ]
            font = None
            for path in font_paths:
                try:
                    font = ImageFont.truetype(path, font_size)
                    break
                except (OSError, IOError):
                    continue
            if font is None:
                font = ImageFont.load_default()
        except Exception:
            font = ImageFont.load_default()
    
    # Create transparent image for text
    img = Image.new('RGBA', (settings.VIDEO_WIDTH, settings.VIDEO_HEIGHT), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Word wrap text
    lines = _wrap_text(clean_text, font, settings.CAPTION_MAX_WIDTH)
    
    # Calculate text dimensions
    line_heights = []
    line_widths = []
    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=font)
        line_widths.append(bbox[2] - bbox[0])
        line_heights.append(bbox[3] - bbox[1])
    
    total_height = sum(line_heights) + (len(lines) - 1) * (font_size // 4)  # Add spacing
    
    # Calculate starting position (centered)
    position = settings.CAPTION_POSITION.lower()
    if position == "center":
        start_y = (settings.VIDEO_HEIGHT - total_height) // 2
    elif position == "bottom":
        start_y = settings.VIDEO_HEIGHT - total_height - 100
    else:  # top
        start_y = 100
    
    # Draw each line of text with stroke (outline)
    current_y = start_y
    for i, line in enumerate(lines):
        if not line.strip():
            current_y += line_heights[i] + (font_size // 4)
            continue
        
        # Calculate x position (centered)
        line_width = line_widths[i]
        x = (settings.VIDEO_WIDTH - line_width) // 2
        
        # Draw stroke (outline) first
        for adj in range(-settings.CAPTION_STROKE_WIDTH, settings.CAPTION_STROKE_WIDTH + 1):
            for adj2 in range(-settings.CAPTION_STROKE_WIDTH, settings.CAPTION_STROKE_WIDTH + 1):
                if adj != 0 or adj2 != 0:
                    draw.text(
                        (x + adj, current_y + adj2),
                        line,
                        font=font,
                        fill=settings.CAPTION_STROKE_COLOR + (255,)
                    )
        
        # Draw main text
        draw.text(
            (x, current_y),
            line,
            font=font,
            fill=settings.CAPTION_COLOR + (255,)
        )
        
        current_y += line_heights[i] + (font_size // 4)
    
    # Convert PIL image to numpy array for MoviePy
    img_array = np.array(img)
    
    # Create ImageClip from the array
    text_clip = ImageClip(img_array)
    text_clip = text_clip.set_duration(duration)
    text_clip = text_clip.set_fps(settings.VIDEO_FPS)
    
    return text_clip


def _wrap_text(text: str, font: ImageFont.ImageFont, max_width: int) -> list[str]:
    """
    Word wrap text to fit within max_width.
    
    Args:
        text: Text to wrap
        font: PIL Font object
        max_width: Maximum width in pixels
    
    Returns:
        List of wrapped lines
    """
    # Split by newlines first (preserve stanza structure)
    paragraphs = text.split('\n')
    wrapped_lines = []
    
    # Create a temporary image for measuring text
    temp_img = Image.new('RGB', (1, 1))
    temp_draw = ImageDraw.Draw(temp_img)
    
    for paragraph in paragraphs:
        if not paragraph.strip():
            wrapped_lines.append("")
            continue
        
        words = paragraph.split()
        current_line = []
        current_width = 0
        
        for word in words:
            # Measure word width
            bbox = temp_draw.textbbox((0, 0), word, font=font)
            word_width = bbox[2] - bbox[0]
            
            # Add space width if not first word
            if current_line:
                space_width = temp_draw.textbbox((0, 0), " ", font=font)[2]
                word_width += space_width
            
            # Check if adding this word would exceed max width
            if current_width + word_width <= max_width:
                current_line.append(word)
                current_width += word_width
            else:
                # Save current line and start new one
                if current_line:
                    wrapped_lines.append(" ".join(current_line))
                current_line = [word]
                current_width = word_width
        
        # Add remaining line
        if current_line:
            wrapped_lines.append(" ".join(current_line))
    
    return wrapped_lines if wrapped_lines else [text]


def _calculate_font_size(text: str) -> int:
    """
    Calculate appropriate font size based on text length.
    
    Args:
        text: Text to measure
    
    Returns:
        Font size in pixels
    """
    # Base font size from settings
    base_size = settings.CAPTION_FONT_SIZE
    
    # Adjust based on text length
    lines = text.split('\n')
    max_line_length = max(len(line) for line in lines) if lines else len(text)
    
    # Reduce font size if text is very long
    if max_line_length > 60:
        # Scale down for long lines
        scale_factor = 60 / max_line_length
        return max(int(base_size * scale_factor), 32)  # Minimum 32px
    
    # Increase slightly for short text
    if max_line_length < 30:
        return min(int(base_size * 1.2), 72)  # Maximum 72px
    
    return base_size



