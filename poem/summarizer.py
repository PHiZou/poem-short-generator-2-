"""Generate world news summary using OpenAI."""

import logging
from openai import OpenAI
import settings

logger = logging.getLogger(__name__)


def get_world_news_summary() -> str:
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
    
    prompt = """Generate a concise 6-8 sentence summary of the most important world news events happening today. 
Focus on major global developments, significant political events, important economic news, and notable international stories.
Write in clear, journalistic prose. Do not include dates or specific times, just describe the events."""

    try:
        logger.info("Generating world news summary using OpenAI...")
        response = client.chat.completions.create(
            model=settings.OPENAI_MODEL,
            messages=[
                {"role": "system", "content": "You are a world news summarizer. Provide concise, factual summaries of global events."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=500
        )
        
        summary = response.choices[0].message.content.strip()
        
        # Validate summary length (rough check for 6-8 sentences)
        sentences = summary.split('.')
        sentence_count = len([s for s in sentences if s.strip()])
        
        if sentence_count < 4:
            logger.warning(f"Generated summary has only {sentence_count} sentences. May need adjustment.")
        elif sentence_count > 10:
            logger.warning(f"Generated summary has {sentence_count} sentences. May be too long.")
        
        logger.info(f"Successfully generated news summary ({sentence_count} sentences)")
        return summary
        
    except Exception as e:
        logger.error(f"Failed to generate news summary: {e}")
        raise

