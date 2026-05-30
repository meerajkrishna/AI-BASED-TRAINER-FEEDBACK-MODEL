"""
Learning Services — YouTube Data API v3 + Wikipedia REST API
─────────────────────────────────────────────────────────────
These are used exclusively by the seed_topics management command.
API views serve from the cached DB data and never call these.

Resilience strategy:
  • YouTube: retry once on network error, return partial results on rate limit
  • Wikipedia: fall back to a simple definition if no article found
  • Both: never raise — always return safe defaults so seeding continues
"""

import logging
import time

import requests
from django.conf import settings

logger = logging.getLogger(__name__)

YOUTUBE_API_BASE = "https://www.googleapis.com/youtube/v3"
WIKIPEDIA_API_BASE = "https://en.wikipedia.org/api/rest_v1/page/summary"


# ═══════════════════════════════════════════════════════════════════════
# YouTube Data API v3
# ═══════════════════════════════════════════════════════════════════════

def fetch_youtube_videos(query: str, max_results: int = 10) -> list[dict]:
    """
    Search YouTube for educational videos on the given aptitude topic.

    Args:
        query:       Search term (e.g. "Percentage aptitude tutorial")
        max_results: Number of videos to fetch (max 10 to stay within quota)

    Returns:
        list of dicts: [{youtube_id, title, thumbnail_url, channel_name}, ...]
        Always returns a list (empty on failure).

    Quota cost: 100 units per search.list call.
    """
    api_key = getattr(settings, 'YOUTUBE_API_KEY', '')
    if not api_key:
        logger.warning("YOUTUBE_API_KEY not set — skipping YouTube fetch for '%s'", query)
        return []

    params = {
        'part': 'snippet',
        'q': f"{query} aptitude tutorial for placement",
        'type': 'video',
        'videoCategoryId': '27',  # Education
        'relevanceLanguage': 'en',
        'maxResults': max_results,
        'order': 'relevance',
        'key': api_key,
        'safeSearch': 'strict',
        'videoEmbeddable': 'true',
    }

    for attempt in range(2):  # Retry once on failure
        try:
            resp = requests.get(
                f"{YOUTUBE_API_BASE}/search",
                params=params,
                timeout=15,
            )

            if resp.status_code == 403:
                logger.error("YouTube API quota exceeded or forbidden. Status: %s", resp.status_code)
                return []

            if resp.status_code != 200:
                logger.warning("YouTube API returned %s for '%s' (attempt %d)", resp.status_code, query, attempt + 1)
                if attempt == 0:
                    time.sleep(2)
                    continue
                return []

            data = resp.json()
            items = data.get('items', [])
            videos = []

            for idx, item in enumerate(items):
                snippet = item.get('snippet', {})
                video_id = item.get('id', {}).get('videoId', '')
                if not video_id:
                    continue

                thumbnails = snippet.get('thumbnails', {})
                thumb = (
                    thumbnails.get('high', {}).get('url', '') or
                    thumbnails.get('medium', {}).get('url', '') or
                    thumbnails.get('default', {}).get('url', '')
                )

                videos.append({
                    'youtube_id': video_id,
                    'title': snippet.get('title', 'Untitled Video'),
                    'thumbnail_url': thumb,
                    'channel_name': snippet.get('channelTitle', ''),
                    'order': idx,
                })

            logger.info("Fetched %d YouTube videos for '%s'", len(videos), query)
            return videos

        except requests.exceptions.Timeout:
            logger.warning("YouTube API timeout for '%s' (attempt %d)", query, attempt + 1)
            if attempt == 0:
                time.sleep(2)
                continue
            return []
        except requests.exceptions.RequestException as e:
            logger.error("YouTube API network error for '%s': %s", query, e)
            if attempt == 0:
                time.sleep(2)
                continue
            return []
        except Exception as e:
            logger.error("Unexpected error fetching YouTube for '%s': %s", query, e)
            return []

    return []


# ═══════════════════════════════════════════════════════════════════════
# Wikipedia REST API
# ═══════════════════════════════════════════════════════════════════════

def fetch_wikipedia_summary(topic_name: str) -> dict:
    """
    Fetch a summary from Wikipedia for the given topic.

    Args:
        topic_name: Topic name (e.g. "Percentage", "Profit and Loss")

    Returns:
        dict: {definition, description, wikipedia_url}
        Always returns a dict with safe defaults on failure.
    """
    # Normalize for Wikipedia URL (spaces → underscores)
    wiki_title = topic_name.replace(' ', '_').replace('&', 'and')

    # Try multiple search variants for better hit rate
    search_variants = [
        f"{wiki_title}_(mathematics)",
        wiki_title,
        f"{wiki_title}_(aptitude)",
    ]

    for variant in search_variants:
        try:
            resp = requests.get(
                f"{WIKIPEDIA_API_BASE}/{variant}",
                headers={'User-Agent': 'AITrainerApp/1.0 (educational project)'},
                timeout=10,
            )

            if resp.status_code == 404:
                continue  # Try next variant

            if resp.status_code != 200:
                logger.warning("Wikipedia API returned %s for '%s'", resp.status_code, variant)
                continue

            data = resp.json()
            extract = data.get('extract', '')
            page_url = data.get('content_urls', {}).get('desktop', {}).get('page', '')

            if not extract or len(extract) < 50:
                continue  # Too short, try next variant

            # Build a richer description from the Wikipedia extract
            definition = extract.split('.')[0] + '.' if '.' in extract else extract[:200]

            logger.info("Wikipedia summary found for '%s' via variant '%s'", topic_name, variant)
            return {
                'definition': definition.strip(),
                'description': extract.strip(),
                'wikipedia_url': page_url,
            }

        except requests.exceptions.Timeout:
            logger.warning("Wikipedia timeout for '%s'", variant)
            continue
        except requests.exceptions.RequestException as e:
            logger.warning("Wikipedia network error for '%s': %s", variant, e)
            continue
        except Exception as e:
            logger.error("Unexpected error fetching Wikipedia for '%s': %s", variant, e)
            continue

    # Fallback: return a generic definition
    logger.info("No Wikipedia article found for '%s' — using fallback", topic_name)
    return {
        'definition': f"{topic_name} is an important topic in quantitative aptitude.",
        'description': (
            f"{topic_name} is a fundamental concept frequently tested in aptitude exams, "
            f"competitive tests, and campus placement interviews. Understanding {topic_name.lower()} "
            f"helps build strong problem-solving and numerical reasoning skills."
        ),
        'wikipedia_url': '',
    }

MEDIAWIKI_API = "https://en.wikipedia.org/w/api.php"


def _clean_wikipedia_html(raw_html: str) -> str:
    """
    Clean Wikipedia's rendered HTML to remove navigation, edit links,
    references, etc. while preserving formulas, tables, headings, and content.
    """
    import re

    html = raw_html

    # ── Remove unwanted elements by regex ──

    # Remove table of contents
    html = re.sub(r'<div id="toc"[^>]*>.*?</div>\s*', '', html, flags=re.DOTALL)
    html = re.sub(r'<div[^>]*class="[^"]*toc[^"]*"[^>]*>.*?</div>\s*', '', html, flags=re.DOTALL)

    # Remove edit section links [edit]
    html = re.sub(r'<span class="mw-editsection">.*?</span>', '', html, flags=re.DOTALL)

    # Remove hatnotes (disambiguation notices)
    html = re.sub(r'<div[^>]*class="[^"]*hatnote[^"]*"[^>]*>.*?</div>', '', html, flags=re.DOTALL)

    # Remove navigation boxes at the bottom
    html = re.sub(r'<div[^>]*class="[^"]*navbox[^"]*"[^>]*>.*?</div>\s*', '', html, flags=re.DOTALL)
    html = re.sub(r'<table[^>]*class="[^"]*navbox[^"]*"[^>]*>.*?</table>', '', html, flags=re.DOTALL)

    # Remove "stub" notices
    html = re.sub(r'<div[^>]*class="[^"]*stub[^"]*"[^>]*>.*?</div>', '', html, flags=re.DOTALL)

    # Remove reference/citation markers like [1] [2] etc.
    html = re.sub(r'<sup[^>]*class="[^"]*reference[^"]*"[^>]*>.*?</sup>', '', html, flags=re.DOTALL)

    # Remove the entire references/notes section
    html = re.sub(r'<div[^>]*class="[^"]*reflist[^"]*"[^>]*>.*?</div>', '', html, flags=re.DOTALL)
    html = re.sub(r'<ol[^>]*class="references"[^>]*>.*?</ol>', '', html, flags=re.DOTALL)

    # Remove "See also", "References", "External links", "Notes", "Further reading" sections
    for section_name in ['See_also', 'References', 'External_links', 'Notes', 'Further_reading', 'Bibliography']:
        pattern = rf'<h2[^>]*>\s*<span[^>]*id="{section_name}"[^>]*>.*?</span>\s*</h2>.*'
        html = re.sub(pattern, '', html, flags=re.DOTALL)

    # Also match the plain-text version of section headings
    for section_name in ['See also', 'References', 'External links', 'Notes', 'Further reading', 'Bibliography']:
        pattern = rf'<h2>.*?{re.escape(section_name)}.*?</h2>.*'
        html = re.sub(pattern, '', html, flags=re.DOTALL)

    # Remove image thumbnails (keep math images)
    html = re.sub(r'<div[^>]*class="[^"]*thumb[^"]*"[^>]*>.*?</div>\s*</div>', '', html, flags=re.DOTALL)
    html = re.sub(r'<figure[^>]*>.*?</figure>', '', html, flags=re.DOTALL)

    # Remove <img> tags that are NOT math (keep math formula images)
    html = re.sub(r'<img(?![^>]*class="[^"]*mwe-math[^"]*")[^>]*/?>', '', html, flags=re.DOTALL)

    # Convert internal wiki links to plain text
    # <a href="/wiki/..." title="...">text</a> → text
    html = re.sub(r'<a[^>]*href="/wiki/[^"]*"[^>]*>(.*?)</a>', r'\1', html, flags=re.DOTALL)

    # Remove empty paragraphs and excess whitespace
    html = re.sub(r'<p>\s*</p>', '', html)
    html = re.sub(r'\n{3,}', '\n\n', html)

    # Remove any remaining Wikipedia-specific classes we don't need
    html = re.sub(r'<div[^>]*class="[^"]*metadata[^"]*"[^>]*>.*?</div>', '', html, flags=re.DOTALL)
    html = re.sub(r'<div[^>]*class="[^"]*sidebar[^"]*"[^>]*>.*?</div>\s*</div>', '', html, flags=re.DOTALL)

    return html.strip()


def fetch_wikipedia_full_content(topic_name: str) -> dict:
    """
    Fetch the FULL Wikipedia article as rendered HTML.

    Uses MediaWiki action=parse&prop=text to get the complete rendered
    article with proper math formulas, tables, headings, and lists.
    The HTML is cleaned to remove navigation, edit links, and references.

    Args:
        topic_name: Topic name (e.g. "Percentage", "Quadratic Equations")

    Returns:
        dict: {definition, description, wikipedia_url}
        Always returns a dict with safe defaults on failure.
    """
    wiki_title = topic_name.replace(' ', '_').replace('&', 'and')

    search_variants = [
        f"{wiki_title}_(mathematics)",
        wiki_title,
        f"{wiki_title}_(aptitude)",
        f"{wiki_title}_(arithmetic)",
    ]

    for variant in search_variants:
        try:
            # ── Step 1: Check if article exists ──
            check_resp = requests.get(
                MEDIAWIKI_API,
                params={
                    'action': 'query',
                    'titles': variant.replace('_', ' '),
                    'prop': 'info',
                    'inprop': 'url',
                    'format': 'json',
                },
                headers={'User-Agent': 'AITrainerApp/1.0 (educational project)'},
                timeout=10,
            )

            if check_resp.status_code != 200:
                continue

            check_data = check_resp.json()
            pages = check_data.get('query', {}).get('pages', {})
            page_id = list(pages.keys())[0]
            if page_id == '-1':
                continue  # Article doesn't exist

            page_url = pages[page_id].get('fullurl', '')

            # ── Step 2: Get rendered HTML ──
            resp = requests.get(
                MEDIAWIKI_API,
                params={
                    'action': 'parse',
                    'page': variant.replace('_', ' '),
                    'prop': 'text',
                    'format': 'json',
                    'disabletoc': 'true',
                },
                headers={'User-Agent': 'AITrainerApp/1.0 (educational project)'},
                timeout=20,
            )

            if resp.status_code != 200:
                logger.warning("MediaWiki parse API returned %s for '%s'", resp.status_code, variant)
                continue

            data = resp.json()
            raw_html = data.get('parse', {}).get('text', {}).get('*', '')

            if not raw_html or len(raw_html) < 200:
                continue

            # ── Step 3: Clean the HTML ──
            cleaned_html = _clean_wikipedia_html(raw_html)

            if len(cleaned_html) < 200:
                continue

            # ── Step 4: Extract plain-text definition ──
            import re
            first_p = re.search(r'<p>(.*?)</p>', cleaned_html, re.DOTALL)
            definition = ''
            if first_p:
                definition = re.sub(r'<[^>]+>', '', first_p.group(1)).strip()
                if '.' in definition:
                    definition = definition.split('.')[0] + '.'
                definition = definition[:500]

            logger.info(
                "Full Wikipedia HTML fetched for '%s' via '%s' — %d chars",
                topic_name, variant, len(cleaned_html)
            )

            return {
                'definition': definition,
                'description': cleaned_html,
                'wikipedia_url': page_url,
            }

        except requests.exceptions.Timeout:
            logger.warning("MediaWiki timeout for '%s'", variant)
            continue
        except requests.exceptions.RequestException as e:
            logger.warning("MediaWiki network error for '%s': %s", variant, e)
            continue
        except Exception as e:
            logger.error("Unexpected error fetching full Wikipedia for '%s': %s", variant, e)
            continue

    # Fallback: try the summary endpoint
    logger.info("Full article not found for '%s' — falling back to summary", topic_name)
    summary = fetch_wikipedia_summary(topic_name)
    return summary
