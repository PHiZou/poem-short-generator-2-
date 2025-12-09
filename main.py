"""Main entry point for the poem short generator pipeline."""

import logging
import sys
from datetime import datetime
from pathlib import Path
import random

from poem.summarizer import get_world_news_summary
from poem.poem_writer import make_stanzas
from audio.tts import generate_audio_files
from video.video_maker import build_video
import settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('poem_generator.log')
    ]
)

logger = logging.getLogger(__name__)


def main() -> None:
    """Main entry point orchestrating the pipeline."""
    try:
        logger.info("=" * 60)
        logger.info("Starting Poem Short Generator Pipeline")
        logger.info("=" * 60)
        
        # Create timestamped output directory
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_dir = settings.OUTPUT_BASE_DIR / timestamp
        output_dir.mkdir(parents=True, exist_ok=True)
        
        audio_dir = output_dir / "audio"
        audio_dir.mkdir(exist_ok=True)
        
        logger.info(f"Output directory: {output_dir}")
        
        # Step 1: Generate world news summary
        logger.info("\n[Step 1/4] Generating world news summary...")
        summary = get_world_news_summary()
        
        # Save summary
        summary_path = output_dir / "summary.txt"
        summary_path.write_text(summary, encoding='utf-8')
        logger.info(f"Summary saved to: {summary_path}")
        
        # Step 2: Convert summary to poem stanzas
        logger.info("\n[Step 2/4] Converting summary to poem stanzas...")
        stanzas = make_stanzas(summary)
        
        # Save stanzas
        stanzas_path = output_dir / "stanzas.txt"
        stanzas_text = "\n\n".join(f"Stanza {i}:\n{stanza}" for i, stanza in enumerate(stanzas, 1))
        stanzas_path.write_text(stanzas_text, encoding='utf-8')
        logger.info(f"Stanzas saved to: {stanzas_path}")
        
        # Step 3: Generate audio files
        logger.info("\n[Step 3/4] Generating audio files...")
        audio_paths = generate_audio_files(stanzas, str(audio_dir))
        logger.info(f"Generated {len(audio_paths)} audio files")
        
        # Step 4: Build video
        logger.info("\n[Step 4/4] Building video...")
        
        # Select background images
        background_paths = _select_backgrounds(len(stanzas))
        if not background_paths:
            raise RuntimeError(
                f"No background images found in {settings.ASSETS_BACKGROUNDS_DIR}. "
                "Please add at least 3 background images."
            )
        
        # Build video
        video_path = output_dir / f"video.{settings.OUTPUT_VIDEO_FORMAT}"
        final_video_path = build_video(
            backgrounds=background_paths,
            stanzas=stanzas,
            audio_paths=audio_paths,
            output_path=str(video_path)
        )
        
        logger.info("\n" + "=" * 60)
        logger.info("Pipeline completed successfully!")
        logger.info("=" * 60)
        logger.info(f"Final video: {final_video_path}")
        logger.info(f"All outputs saved to: {output_dir}")
        
    except KeyboardInterrupt:
        logger.warning("\nPipeline interrupted by user.")
        sys.exit(1)
    except Exception as e:
        logger.error(f"\nPipeline failed with error: {e}", exc_info=True)
        sys.exit(1)


def _select_backgrounds(count: int) -> list[str]:
    """
    Select background images for the video.
    
    Args:
        count: Number of backgrounds needed
    
    Returns:
        List of background image file paths
    """
    bg_dir = settings.ASSETS_BACKGROUNDS_DIR
    
    if not bg_dir.exists():
        logger.warning(f"Background directory does not exist: {bg_dir}")
        return []
    
    # Find all image files
    image_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.gif'}
    image_files = [
        str(f) for f in bg_dir.iterdir()
        if f.is_file() and f.suffix.lower() in image_extensions
    ]
    
    if not image_files:
        logger.warning(f"No image files found in {bg_dir}")
        return []
    
    if len(image_files) < count:
        logger.warning(
            f"Only {len(image_files)} background images available, "
            f"but {count} are needed. Some backgrounds will be reused."
        )
        # Repeat images if needed
        selected = image_files * ((count // len(image_files)) + 1)
        return selected[:count]
    
    # Randomly select backgrounds
    selected = random.sample(image_files, count)
    logger.info(f"Selected {len(selected)} background images")
    
    return selected


if __name__ == "__main__":
    main()

