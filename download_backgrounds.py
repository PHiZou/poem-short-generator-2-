"""Download vertical background images from Unsplash."""

import os
import requests
from pathlib import Path

# Keywords for different image types
KEYWORDS = [
    "landscape vertical",
    "abstract texture",
    "sky clouds vertical",
    "nature vertical",
    "minimalist vertical",
    "gradient vertical"
]

# Image dimensions (vertical format)
WIDTH = 1080
HEIGHT = 1920


def download_backgrounds():
    """Download 6 vertical background images from Unsplash."""
    # Create backgrounds directory if it doesn't exist
    bg_dir = Path("assets/backgrounds")
    bg_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"Downloading {len(KEYWORDS)} background images to {bg_dir}...")
    
    for i, keyword in enumerate(KEYWORDS, 1):
        filename = bg_dir / f"bg_{i:02d}.jpg"
        
        # Try Unsplash Source API (modern approach)
        url = f"https://source.unsplash.com/{WIDTH}x{HEIGHT}/?{keyword.replace(' ', ',')}"
        
        print(f"Downloading image {i}/{len(KEYWORDS)}: {keyword}...")
        
        try:
            # Download image with headers to avoid blocking
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
            }
            response = requests.get(url, timeout=30, allow_redirects=True, headers=headers)
            response.raise_for_status()
            
            # Check if we got an actual image
            content_type = response.headers.get('content-type', '')
            if 'image' not in content_type:
                # If redirected, follow to final URL
                final_url = response.url
                response = requests.get(final_url, timeout=30, headers=headers)
                response.raise_for_status()
            
            # Save image
            with open(filename, 'wb') as f:
                f.write(response.content)
            
            # Verify file was created and has content
            if filename.exists() and filename.stat().st_size > 1000:  # At least 1KB
                print(f"  ✓ Saved: {filename} ({filename.stat().st_size // 1024}KB)")
            else:
                print(f"  ✗ Failed: File is too small or empty")
                filename.unlink(missing_ok=True)
                
        except requests.exceptions.RequestException as e:
            print(f"  ✗ Failed to download: {e}")
            # Try fallback: use Picsum Photos (reliable alternative)
            try:
                fallback_url = f"https://picsum.photos/{WIDTH}/{HEIGHT}?random={i}"
                response = requests.get(fallback_url, timeout=30, headers=headers)
                response.raise_for_status()
                
                with open(filename, 'wb') as f:
                    f.write(response.content)
                
                if filename.exists() and filename.stat().st_size > 1000:
                    print(f"  ✓ Saved (fallback): {filename} ({filename.stat().st_size // 1024}KB)")
                else:
                    print(f"  ✗ Fallback also failed")
            except Exception as e2:
                print(f"  ✗ Fallback failed: {e2}")
    
    # Count successfully downloaded images
    downloaded = list(bg_dir.glob("bg_*.jpg"))
    print(f"\n✓ Download complete! {len(downloaded)} images saved to {bg_dir}")
    
    if len(downloaded) < 3:
        print(f"\n⚠ Warning: Only {len(downloaded)} images downloaded. You need at least 3 for the video generator.")


if __name__ == "__main__":
    download_backgrounds()

