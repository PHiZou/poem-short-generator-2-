"""Generate world news summary using OpenAI."""

import logging
import time
from openai import OpenAI
import settings

logger = logging.getLogger(__name__)


def get_world_news_summary(model: str | None = None, max_retries: int = 3, backoff_seconds: float = 1.5) -> str:
    """
    Uses OpenAI to generate a 6-8 sentence global news digest.
    
    Returns:
        Summary text as string.
    
    Raises:
        ValueError: If OpenAI API key is not configured.
        Exception: If OpenAI API call fails.
    """
    if not settings.OPENAI_API_KEY:
        raise ValueError("OPENAI_API_KEY is not configured. Please set it in your environment or .env file.")
    
    client = OpenAI(api_key=settings.OPENAI_API_KEY)
    model_name = model or settings.OPENAI_MODEL
    
    prompt = """Generate a concise 6-8 sentence summary of today's most important world news.
- Cover geopolitics, economy/markets, major conflicts, climate/disasters, tech/policy shifts.
- Highlight why each item matters (implications, stakes, affected regions).
- Avoid timestamps; write in clear, neutral journalistic prose.
- Keep it factual, globally balanced, and non-speculative."""

    last_error: Exception | None = None
    for attempt in range(1, max_retries + 1):
        try:
            logger.info(f"Generating world news summary using OpenAI (attempt {attempt}/{max_retries})...")
            response = client.chat.completions.create(
                model=model_name,
                messages=[
                    {"role": "system", "content": "You are a world news summarizer. Provide concise, factual, globally balanced summaries with clear implications."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.6,
                max_tokens=600
            )
            
            summary = response.choices[0].message.content.strip()
            
            # Validate summary length (rough check for 6-10 sentences)
            sentences = summary.split('.')
            sentence_count = len([s for s in sentences if s.strip()])
            
            if sentence_count < 4:
                logger.warning(f"Generated summary has only {sentence_count} sentences. May need adjustment.")
            elif sentence_count > 10:
                logger.warning(f"Generated summary has {sentence_count} sentences. May be too long.")
            
            logger.info(f"Successfully generated news summary ({sentence_count} sentences)")
            return summary
            
        except Exception as e:
            last_error = e
            logger.warning(f"Attempt {attempt} failed to generate news summary: {e}")
            if attempt < max_retries:
                time.sleep(backoff_seconds * attempt)
    
    logger.error(f"Failed to generate news summary after {max_retries} attempts: {last_error}")
    raise last_error

