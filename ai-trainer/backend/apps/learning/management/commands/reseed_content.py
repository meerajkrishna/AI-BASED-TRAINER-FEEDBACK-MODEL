"""
reseed_content — update existing topics with full Wikipedia content
════════════════════════════════════════════════════════════════════

Usage:
    python manage.py reseed_content              # Update all topics
    python manage.py reseed_content --limit 5    # Update first 5 only
    python manage.py reseed_content --category arithmetic

This command does NOT touch YouTube videos. It only updates:
  - definition (first sentence of full article)
  - description (full Wikipedia article text)
  - wikipedia_url

Safe to re-run: overwrites existing content with the latest full article.
No API quota concerns — Wikipedia API is free and unlimited (with rate limiting).
"""

import time
import logging

from django.core.management.base import BaseCommand
from apps.learning.models import Topic
from apps.learning.services import fetch_wikipedia_full_content

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Update all topics with full Wikipedia article content."

    def add_arguments(self, parser):
        parser.add_argument(
            '--limit', type=int, default=0,
            help='Limit the number of topics to update (0 = all)',
        )
        parser.add_argument(
            '--category', type=str, default='',
            help='Only update topics in this category',
        )

    def handle(self, *args, **options):
        limit = options['limit']
        category_filter = options['category']

        queryset = Topic.objects.all().order_by('id')

        if category_filter:
            queryset = queryset.filter(category=category_filter)
            self.stdout.write(f"Filtered to category '{category_filter}'")

        if limit > 0:
            queryset = queryset[:limit]
            self.stdout.write(f"Limited to {limit} topics")

        topics = list(queryset)
        total = len(topics)
        updated = 0
        skipped = 0
        errors = 0

        self.stdout.write(self.style.SUCCESS(f"\n{'='*60}"))
        self.stdout.write(self.style.SUCCESS(f"  Updating {total} topics with full Wikipedia content"))
        self.stdout.write(self.style.SUCCESS(f"{'='*60}\n"))

        for idx, topic in enumerate(topics, start=1):
            try:
                self.stdout.write(f"  [{idx}/{total}] Fetching full content: {topic.name}...")

                wiki_data = fetch_wikipedia_full_content(topic.name)
                new_desc = wiki_data.get('description', '')

                if not new_desc or len(new_desc) < 200:
                    self.stdout.write(self.style.WARNING(
                        f"           SKIP — content too short ({len(new_desc)} chars)"
                    ))
                    skipped += 1
                    continue

                old_len = len(topic.description)
                topic.definition = wiki_data['definition']
                topic.description = new_desc
                topic.wikipedia_url = wiki_data.get('wikipedia_url', topic.wikipedia_url)
                topic.save()

                self.stdout.write(self.style.SUCCESS(
                    f"           OK: {old_len} → {len(new_desc)} chars"
                ))
                updated += 1

                # Rate limit: 0.5 seconds between topics
                if idx < total:
                    time.sleep(0.5)

            except Exception as e:
                errors += 1
                self.stdout.write(self.style.ERROR(
                    f"  [{idx}/{total}] ERROR: {topic.name} — {e}"
                ))
                continue

        self.stdout.write(f"\n{'='*60}")
        self.stdout.write(self.style.SUCCESS(f"  RESEED COMPLETE"))
        self.stdout.write(f"  Updated: {updated}")
        self.stdout.write(f"  Skipped: {skipped}")
        self.stdout.write(f"  Errors:  {errors}")
        self.stdout.write(f"{'='*60}\n")
