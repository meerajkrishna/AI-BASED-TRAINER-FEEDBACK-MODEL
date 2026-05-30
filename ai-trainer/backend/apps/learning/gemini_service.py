import google.generativeai as genai
from django.conf import settings
import logging
import time
import re

logger = logging.getLogger(__name__)

class ContentGenerationError(Exception):
    """Raised when we completely fail to generate content (e.g. all keys exhausted)."""
    pass

class GeminiLearningService:
    def __init__(self):
        # GEMINI_API_KEYS should be a list of keys, fallback to empty list
        self.api_keys = getattr(settings, 'GEMINI_API_KEYS', [])
        if not self.api_keys or not any(self.api_keys):
            raise ValueError("GEMINI_API_KEYS not configured in settings")
            
        self.current_key_idx = 0
        self._configure_active_key()
        
    def _configure_active_key(self):
        active_key = self.api_keys[self.current_key_idx].strip()
        genai.configure(api_key=active_key)
        # Using flash model for faster, cheaper generation that is sufficient for text tutorials
        self.model = genai.GenerativeModel('gemini-2.5-flash')
        logger.info(f"Configured Gemini with API key index {self.current_key_idx} (partial: {active_key[:4]}...)")

    def _rotate_key(self) -> bool:
        if self.current_key_idx < len(self.api_keys) - 1:
            self.current_key_idx += 1
            self._configure_active_key()
            return True
        return False

    def generate_topic_tutorial(self, topic_name: str) -> dict:
        prompt = f"""You are an expert aptitude trainer creating a comprehensive tutorial for a learning platform.
Write a highly-structured, easy-to-understand tutorial on the topic: "{topic_name}".

The tutorial MUST be formatted as valid HTML fragments that will be rendered inside an existing React web application.
Do NOT use markdown blocks like ```html. Just output raw HTML directly.
IMPORTANT: DO NOT generate `<!DOCTYPE html>`, `<html>`, `<head>`, `<style>`, or `<body>` tags. Only generate the structural fragments (`<h2>`, `<p>`, `<div>`, etc.) for the content itself!

Include the following sections clearly formatted using standard HTML tags:

1. Concept & Definition (Explain it simply like you are teaching a beginner).
2. Important Formulas & Shortcuts (Use clean <ul> lists or simple HTML tables). Highlight key parts.
3. 2-3 Solved Examples (Make sure they are classic exam-style questions. Show step-by-step solutions).
4. Pro-Tips / Mental Math Tricks / Pitfalls to avoid.

Formatting rules:
- Use <h2> for main section headers.
- Use <h3> for sub-headings like "Example 1".
- Wrap formulas in <div class="formula-box"></div>.
- Wrap solved examples in <div class="example-box"></div>.
- Emphasize important terms using <strong>.
- Make the content engaging and strictly focused on aptitude test preparation.

Generate the HTML tutorial now:"""

        max_attempts = len(self.api_keys) * 2  # Try each key up to 2 times
        attempt = 0
        
        while attempt < max_attempts:
            try:
                response = self.model.generate_content(prompt)
                
                # Check if generated content was blocked by safety settings
                if hasattr(response, 'prompt_feedback') and response.prompt_feedback.block_reason:
                    raise Exception(f"Prompt blocked: {response.prompt_feedback.block_reason}")
                
                html_content = response.text.strip()
                
                # Cleanup if AI still added markdown blocks
                if html_content.startswith('```html'):
                    html_content = html_content[7:]
                if html_content.startswith('```'):
                    html_content = html_content[3:]
                if html_content.endswith('```'):
                    html_content = html_content[:-3]
                    
                html_content = html_content.strip()
                
                # Extract definition (just the first reasonable sentence from the html)
                first_p_match = re.search(r'<p>(.*?)</p>', html_content, flags=re.DOTALL | re.IGNORECASE)
                definition_text = ""
                if first_p_match:
                    raw_text = re.sub(r'<[^>]+>', '', first_p_match.group(1)).replace('\n', ' ').strip()
                    definition_text = raw_text.split('.')[0] + '.' if '.' in raw_text else raw_text
                
                return {
                    'description': html_content,
                    'definition': definition_text[:500] if definition_text else f"{topic_name} is an important aptitude concept."
                }

            except Exception as e:
                err_msg = str(e).lower()
                logger.warning(f"Error generating content on key {self.current_key_idx}: {e}")
                
                # Catch typical quota/rate-limit indicators
                if "429" in err_msg or "quota" in err_msg or "exhausted" in err_msg or "too many requests" in err_msg:
                    logger.info("Rate limit hit. Attempting to rotate API key...")
                    if self._rotate_key():
                        # Rotated successfully, retry immediately
                        continue
                    else:
                        logger.error("All API keys exhausted their quota.")
                        raise ContentGenerationError("All API keys exhausted.") from e
                else:
                    # Other transient errors (503, bad gateway, timeout)
                    time.sleep(2)
                    attempt += 1

        raise ContentGenerationError("Exceeded max retries for generating tutorial.")
