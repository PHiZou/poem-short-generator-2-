"""Convert news summary into 3-stanza poem using OpenAI."""

import logging
import re
import time
from openai import OpenAI
import settings

logger = logging.getLogger(__name__)


def make_stanzas(summary_text: str, tone: str = "poetic insight", model: str | None = None, max_retries: int = 3, backoff_seconds: float = 1.5) -> list[str]:
    """
    Converts summary → 3 stanzas (2-3 lines each).
    Each stanza focuses on part of the news.
    
    Args:
        summary_text: The news summary text to convert.
        tone: Desired tone/style for the poem.
        model: Optional OpenAI model override.
        max_retries: Number of retry attempts on failure.
        backoff_seconds: Base backoff in seconds between retries.
    
    Returns:
        List of 3 strings, each representing one stanza.
    
    Raises:
        ValueError: If OpenAI API key is not configured or summary is empty.
        Exception: If OpenAI API call fails or cannot parse stanzas.
    """
    if not settings.OPENAI_API_KEY:
        raise ValueError("OPENAI_API_KEY is not configured. Please set it in your environment or .env file.")
    
    if not summary_text or not summary_text.strip():
        raise ValueError("Summary text cannot be empty.")
    
    client = OpenAI(api_key=settings.OPENAI_API_KEY)
    model_name = model or settings.OPENAI_MODEL
    
    prompt = f"""Convert the following world news summary into a 3-stanza poem.
- Each stanza must have 2-3 lines and focus on a different facet of the news.
- Write with {tone} while keeping factual anchoring and insight.
- Provide subtle interpretation: stakes, human impact, and context across regions.
- Use vivid, economical language; avoid clichés; keep it respectful.
- Separate each stanza with a blank line.

News Summary:
{summary_text}

Format the output exactly as:
Stanza 1 line 1
Stanza 1 line 2
[optional line 3]

Stanza 2 line 1
Stanza 2 line 2
[optional line 3]

Stanza 3 line 1
Stanza 3 line 2
[optional line 3]"""

    last_error: Exception | None = None
    for attempt in range(1, max_retries + 1):
        try:
            logger.info(f"Generating poem stanzas from news summary (attempt {attempt}/{max_retries})...")
            response = client.chat.completions.create(
                model=model_name,
                messages=[
                    {"role": "system", "content": "You are a poet who crafts insightful, evocative poetry grounded in real news, balancing empathy, clarity, and global perspective."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.75,
                max_tokens=420
            )
            
            poem_text = response.choices[0].message.content.strip()
            
            # Parse stanzas from the response
            stanzas = _parse_stanzas(poem_text)
            
            # Validate we have exactly 3 stanzas
            if len(stanzas) != 3:
                logger.warning(f"Expected 3 stanzas, got {len(stanzas)}. Attempting to fix...")
                stanzas = _fix_stanza_count(stanzas, poem_text)
            
            # Validate each stanza has 2-3 lines
            for i, stanza in enumerate(stanzas, 1):
                lines = [line.strip() for line in stanza.split('\n') if line.strip()]
                if len(lines) < 2:
                    logger.warning(f"Stanza {i} has only {len(lines)} lines. May need adjustment.")
                elif len(lines) > 3:
                    logger.warning(f"Stanza {i} has {len(lines)} lines. Truncating to 3.")
                    stanzas[i-1] = '\n'.join(lines[:3])
            
            logger.info(f"Successfully generated {len(stanzas)} stanzas")
            return stanzas
            
        except Exception as e:
            last_error = e
            logger.warning(f"Attempt {attempt} failed to generate poem stanzas: {e}")
            if attempt < max_retries:
                time.sleep(backoff_seconds * attempt)
    
    logger.error(f"Failed to generate poem stanzas after {max_retries} attempts: {last_error}")
    raise last_error


def _parse_stanzas(poem_text: str) -> list[str]:
    """
    Parse stanzas from poem text.
    
    Args:
        poem_text: Raw poem text from OpenAI.
    
    Returns:
        List of stanza strings.
    """
    # Split by double newlines (stanza separators)
    parts = re.split(r'\n\s*\n', poem_text)
    
    # Clean up each part
    stanzas = []
    for part in parts:
        part = part.strip()
        if part:
            # Remove stanza numbers if present (e.g., "Stanza 1:")
            part = re.sub(r'^Stanza\s+\d+[:\-]?\s*', '', part, flags=re.IGNORECASE)
            part = part.strip()
            if part:
                stanzas.append(part)
    
    return stanzas


def _fix_stanza_count(stanzas: list[str], original_text: str) -> list[str]:
    """
    Attempt to fix stanza count if we don't have exactly 3.
    
    Args:
        stanzas: Current list of stanzas.
        original_text: Original poem text.
    
    Returns:
        List of exactly 3 stanzas.
    """
    if len(stanzas) == 3:
        return stanzas
    
    # If we have more than 3, take first 3
    if len(stanzas) > 3:
        logger.info(f"Taking first 3 of {len(stanzas)} stanzas")
        return stanzas[:3]
    
    # If we have fewer than 3, try to split longer stanzas
    if len(stanzas) == 2:
        # Split the longer stanza
        if len(stanzas[0]) > len(stanzas[1]):
            # Split first stanza
            lines = [l.strip() for l in stanzas[0].split('\n') if l.strip()]
            mid = len(lines) // 2
            return [
                '\n'.join(lines[:mid]),
                '\n'.join(lines[mid:]),
                stanzas[1]
            ]
        else:
            # Split second stanza
            lines = [l.strip() for l in stanzas[1].split('\n') if l.strip()]
            mid = len(lines) // 2
            return [
                stanzas[0],
                '\n'.join(lines[:mid]),
                '\n'.join(lines[mid:])
            ]
    
    # If we only have 1 stanza, split it into 3
    if len(stanzas) == 1:
        lines = [l.strip() for l in stanzas[0].split('\n') if l.strip()]
        if len(lines) >= 6:
            # Split into roughly equal parts
            chunk_size = len(lines) // 3
            return [
                '\n'.join(lines[0:chunk_size]),
                '\n'.join(lines[chunk_size:chunk_size*2]),
                '\n'.join(lines[chunk_size*2:])
            ]
        else:
            # Pad with empty lines or repeat
            while len(stanzas) < 3:
                stanzas.append(stanzas[0] if stanzas else "")
    
    return stanzas[:3] if len(stanzas) >= 3 else stanzas + [""] * (3 - len(stanzas))

