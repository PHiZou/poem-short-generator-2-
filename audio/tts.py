"""Generate audio files using Piper TTS."""

import logging
import subprocess
import os
from pathlib import Path
import settings

logger = logging.getLogger(__name__)


def generate_audio_files(stanzas: list[str], output_dir: str) -> list[str]:
    """
    Uses Piper TTS to generate 3 WAV files (one per stanza).
    
    Args:
        stanzas: List of stanza text strings
        output_dir: Directory to save audio files
    
    Returns:
        List of file paths to generated WAV files
    
    Raises:
        ValueError: If stanzas list is empty or invalid.
        RuntimeError: If Piper TTS fails to generate audio.
    """
    if not stanzas:
        raise ValueError("Stanzas list cannot be empty.")
    
    if len(stanzas) != 3:
        logger.warning(f"Expected 3 stanzas, got {len(stanzas)}")
    
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    audio_paths = []
    
    for i, stanza in enumerate(stanzas, 1):
        # Clean stanza text for TTS (remove extra whitespace, newlines)
        clean_text = ' '.join(stanza.split())
        
        audio_filename = f"stanza_{i}.{settings.OUTPUT_AUDIO_FORMAT}"
        audio_path = output_path / audio_filename
        
        try:
            logger.info(f"Generating audio for stanza {i}...")
            _generate_audio_with_piper(clean_text, str(audio_path))
            
            # Validate audio file was created
            if not audio_path.exists():
                raise RuntimeError(f"Audio file was not created: {audio_path}")
            
            # Check file size (should be > 0)
            if audio_path.stat().st_size == 0:
                raise RuntimeError(f"Audio file is empty: {audio_path}")
            
            audio_paths.append(str(audio_path))
            logger.info(f"Successfully generated audio: {audio_path}")
            
        except Exception as e:
            logger.error(f"Failed to generate audio for stanza {i}: {e}")
            raise RuntimeError(f"TTS generation failed for stanza {i}: {e}") from e
    
    return audio_paths


def _generate_audio_with_piper(text: str, output_path: str) -> None:
    """
    Generate audio using Piper TTS.
    
    Supports multiple Piper installation methods:
    1. piper-tts Python package (if available)
    2. piper command-line tool via subprocess
    3. piper Python bindings
    
    Args:
        text: Text to convert to speech
        output_path: Path to save the WAV file
    
    Raises:
        RuntimeError: If Piper TTS is not available or fails.
    """
    # Try method 1: piper-tts Python package (imports as 'piper')
    try:
        import piper
        # Check if it's the piper-tts package (has PiperVoice)
        if hasattr(piper, 'PiperVoice'):
            logger.debug("Using piper-tts Python package")
            _generate_with_piper_package(text, output_path)
            return
    except ImportError:
        pass
    
    # Try method 2: piper command-line tool
    try:
        logger.debug("Using piper command-line tool")
        _generate_with_piper_cli(text, output_path)
        return
    except (FileNotFoundError, subprocess.CalledProcessError):
        pass
    
    # Method 3 is now handled by method 1 (piper-tts package)
    
    # If all methods fail, raise error with helpful message
    raise RuntimeError(
        "Piper TTS is not available. Please install it using one of:\n"
        "1. pip install piper-tts\n"
        "2. Install piper command-line tool and ensure it's in PATH\n"
        "3. Install piper Python bindings\n"
        "See https://github.com/rhasspy/piper for installation instructions."
    )


def _generate_with_piper_package(text: str, output_path: str) -> None:
    """Generate audio using piper-tts Python package."""
    import piper
    import wave
    
    # Get voice model path
    voice_model = settings.PIPER_VOICE_MODEL
    if settings.PIPER_VOICE_PATH:
        voice_model = settings.PIPER_VOICE_PATH
    
    # PiperVoice.load expects a path to .onnx model file
    # Try multiple locations: explicit path, current dir, or download if needed
    model_path = None
    
    # If it's already a full path with .onnx extension, use it
    if voice_model.endswith('.onnx') and Path(voice_model).exists():
        model_path = voice_model
    # If it's a path without extension, try adding .onnx
    elif Path(voice_model).exists():
        model_path = voice_model
    # Try current directory with .onnx extension
    elif Path(f"{voice_model}.onnx").exists():
        model_path = f"{voice_model}.onnx"
    # Try in project root
    elif (Path(settings.BASE_DIR) / f"{voice_model}.onnx").exists():
        model_path = str(Path(settings.BASE_DIR) / f"{voice_model}.onnx")
    else:
        # Try downloading the voice model
        logger.info(f"Voice model not found locally. Attempting to download '{voice_model}'...")
        try:
            import subprocess
            result = subprocess.run(
                ["python", "-m", "piper.download_voices", voice_model],
                capture_output=True,
                text=True,
                timeout=120,
                cwd=str(settings.BASE_DIR)
            )
            if result.returncode == 0:
                # Model downloaded, try loading from current directory
                if Path(f"{voice_model}.onnx").exists():
                    model_path = f"{voice_model}.onnx"
                elif (Path(settings.BASE_DIR) / f"{voice_model}.onnx").exists():
                    model_path = str(Path(settings.BASE_DIR) / f"{voice_model}.onnx")
                else:
                    raise RuntimeError(f"Voice model downloaded but not found: {voice_model}")
            else:
                raise RuntimeError(f"Could not download voice model: {result.stderr}")
        except Exception as e:
            raise RuntimeError(
                f"Could not load voice model '{voice_model}'. "
                f"Please ensure the .onnx model file exists or set PIPER_VOICE_PATH to the full path. Error: {e}"
            )
    
    # Load the voice model
    try:
        voice = piper.PiperVoice.load(model_path)
    except Exception as e:
        raise RuntimeError(f"Failed to load voice model from '{model_path}': {e}")
    
    # Synthesize text to WAV file
    with wave.open(output_path, "wb") as wav_file:
        voice.synthesize_wav(text, wav_file)


def _generate_with_piper_cli(text: str, output_path: str) -> None:
    """Generate audio using piper command-line tool."""
    voice_model = settings.PIPER_VOICE_MODEL
    if settings.PIPER_VOICE_PATH:
        voice_model = settings.PIPER_VOICE_PATH
    
    # Prepare piper command
    # Format: echo "text" | piper --model <model> --output_file <output>
    cmd = [
        "piper",
        "--model", voice_model,
        "--output_file", output_path
    ]
    
    # Run piper with text input
    process = subprocess.Popen(
        cmd,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    stdout, stderr = process.communicate(input=text)
    
    if process.returncode != 0:
        raise subprocess.CalledProcessError(
            process.returncode,
            cmd,
            stdout,
            stderr
        )



