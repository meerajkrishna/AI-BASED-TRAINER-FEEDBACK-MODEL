"""
seed_topics — populate the learning database with aptitude topics
═══════════════════════════════════════════════════════════════════

Usage:
    python manage.py seed_topics              # Seed all topics
    python manage.py seed_topics --limit 5    # Seed first 5 only (for testing)
    python manage.py seed_topics --skip-youtube   # Seed without YouTube calls
    python manage.py seed_topics --category arithmetic  # Seed one category
    python manage.py seed_topics --archive-update  # Only update archive/quiz flags

For each topic the command:
  1. Creates a Topic row with Wikipedia summary (or fallback)
  2. Fetches 10 YouTube videos and stores them as TopicVideo rows
  3. Skips topics that already exist (safe to re-run)
  4. Topics without quiz data are marked as archived

YouTube API quota: each search = 100 units, daily limit = 10,000.
"""

import time
import logging

from django.core.management.base import BaseCommand
from apps.learning.models import Topic, TopicVideo
from apps.learning.services import fetch_youtube_videos, fetch_wikipedia_summary

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════════
# Topics WITH quiz data (27 topics) — these stay active
# ═══════════════════════════════════════════════════════════════
QUIZ_TOPIC_NAMES = {
    'Percentage',
    'Profit and Loss',
    'Simple Interest',
    'Compound Interest',
    'Averages',
    'Ratio and Proportion',
    'Partnership',
    'Number Series',
    'HCF and LCM',
    'Linear Equations',
    'Quadratic Equations',
    'Logarithms',
    'Time and Work',
    'Bar Graphs',
    'Line Charts',
    'Histogram',
    'Pie Charts',
    'Caselets',
    'Tables and Data Tables',
    'Data Tables',
    'Coding and Decoding',
    'Blood Relations',
    'Seating Arrangement',
    'Syllogisms',
    'Direction Sense',
    'Logical Puzzles',
    'Series Completion',
    'Arithmetic Progression',
    'Geometric Progression',
}


# ═══════════════════════════════════════════════════════════════
# Master topic list — topics across 11+ categories
# has_quiz=True  → quiz data available from Excel datasets
# archived=True  → hidden from UI (no quiz data yet)
# ═══════════════════════════════════════════════════════════════

TOPIC_SEED_DATA = [
    # ── Quantitative / Arithmetic ──
    {'name': 'Percentage', 'category': 'quantitative', 'icon': '📊', 'level': 'Beginner'},
    {'name': 'Profit and Loss', 'category': 'quantitative', 'icon': '💰', 'level': 'Beginner'},
    {'name': 'Simple Interest', 'category': 'quantitative', 'icon': '🏦', 'level': 'Beginner'},
    {'name': 'Compound Interest', 'category': 'quantitative', 'icon': '📈', 'level': 'Intermediate'},
    {'name': 'Averages', 'category': 'quantitative', 'icon': '📉', 'level': 'Beginner'},
    {'name': 'Ratio and Proportion', 'category': 'quantitative', 'icon': '⚖️', 'level': 'Beginner'},
    {'name': 'Partnership', 'category': 'quantitative', 'icon': '🤝', 'level': 'Intermediate'},
    {'name': 'Number Series', 'category': 'quantitative', 'icon': '🔢', 'level': 'Intermediate'},
    {'name': 'HCF and LCM', 'category': 'quantitative', 'icon': '🧮', 'level': 'Beginner'},
    {'name': 'Linear Equations', 'category': 'quantitative', 'icon': '📏', 'level': 'Beginner'},
    {'name': 'Quadratic Equations', 'category': 'quantitative', 'icon': '📐', 'level': 'Intermediate'},
    {'name': 'Logarithms', 'category': 'quantitative', 'icon': '📝', 'level': 'Intermediate'},
    {'name': 'Arithmetic Progression', 'category': 'quantitative', 'icon': '📊', 'level': 'Intermediate'},
    {'name': 'Geometric Progression', 'category': 'quantitative', 'icon': '📈', 'level': 'Intermediate'},
    {'name': 'Time and Work', 'category': 'quantitative', 'icon': '⏱️', 'level': 'Intermediate'},

    # ── Data Interpretation ──
    {'name': 'Bar Graphs', 'category': 'data_interpretation', 'icon': '📊', 'level': 'Beginner'},
    {'name': 'Line Charts', 'category': 'data_interpretation', 'icon': '📈', 'level': 'Beginner'},
    {'name': 'Histogram', 'category': 'data_interpretation', 'icon': '📊', 'level': 'Intermediate'},
    {'name': 'Pie Charts', 'category': 'data_interpretation', 'icon': '🥧', 'level': 'Beginner'},
    {'name': 'Caselets', 'category': 'data_interpretation', 'icon': '📑', 'level': 'Advanced'},
    {'name': 'Data Tables', 'category': 'data_interpretation', 'icon': '📋', 'level': 'Beginner'},

    # ── Logical Reasoning ──
    {'name': 'Coding and Decoding', 'category': 'logical_reasoning', 'icon': '🔐', 'level': 'Beginner'},
    {'name': 'Blood Relations', 'category': 'logical_reasoning', 'icon': '👨‍👩‍👦', 'level': 'Intermediate'},
    {'name': 'Seating Arrangement', 'category': 'logical_reasoning', 'icon': '💺', 'level': 'Intermediate'},
    {'name': 'Syllogisms', 'category': 'logical_reasoning', 'icon': '🧠', 'level': 'Intermediate'},
    {'name': 'Direction Sense', 'category': 'logical_reasoning', 'icon': '🧭', 'level': 'Beginner'},
    {'name': 'Logical Puzzles', 'category': 'logical_reasoning', 'icon': '🧩', 'level': 'Advanced'},
    {'name': 'Series Completion', 'category': 'logical_reasoning', 'icon': '🔢', 'level': 'Beginner'},

    # ═══════════════════════════════════════════════════════════
    # ARCHIVED — No quiz data yet, kept for future use
    # ═══════════════════════════════════════════════════════════

    # ── Archived: Arithmetic ──
    {'name': 'Problems on Ages', 'category': 'arithmetic', 'icon': '🎂', 'level': 'Intermediate'},
    {'name': 'Mixtures and Alligation', 'category': 'arithmetic', 'icon': '🧪', 'level': 'Advanced'},
    {'name': 'Unitary Method', 'category': 'arithmetic', 'icon': '🔢', 'level': 'Beginner'},

    # ── Archived: Number System ──
    {'name': 'Divisibility Rules', 'category': 'number_system', 'icon': '➗', 'level': 'Beginner'},
    {'name': 'Remainders', 'category': 'number_system', 'icon': '🔄', 'level': 'Intermediate'},
    {'name': 'Unit Digit', 'category': 'number_system', 'icon': '1️⃣', 'level': 'Intermediate'},
    {'name': 'Factors and Multiples', 'category': 'number_system', 'icon': '✖️', 'level': 'Beginner'},
    {'name': 'Surds and Indices', 'category': 'number_system', 'icon': '📐', 'level': 'Advanced'},
    {'name': 'Simplification', 'category': 'number_system', 'icon': '✏️', 'level': 'Beginner'},
    {'name': 'Square Roots and Cube Roots', 'category': 'number_system', 'icon': '√', 'level': 'Beginner'},

    # ── Archived: Algebra ──
    {'name': 'Inequalities', 'category': 'algebra', 'icon': '↔️', 'level': 'Intermediate'},
    {'name': 'Harmonic Progression', 'category': 'algebra', 'icon': '🎵', 'level': 'Advanced'},
    {'name': 'Set Theory', 'category': 'algebra', 'icon': '🔵', 'level': 'Beginner'},

    # ── Archived: Geometry & Mensuration ──
    {'name': 'Lines and Angles', 'category': 'geometry', 'icon': '📐', 'level': 'Beginner'},
    {'name': 'Triangles', 'category': 'geometry', 'icon': '🔺', 'level': 'Beginner'},
    {'name': 'Circles', 'category': 'geometry', 'icon': '⭕', 'level': 'Beginner'},
    {'name': 'Polygons', 'category': 'geometry', 'icon': '🔷', 'level': 'Intermediate'},
    {'name': 'Area and Perimeter', 'category': 'geometry', 'icon': '📏', 'level': 'Beginner'},
    {'name': 'Volume and Surface Area', 'category': 'geometry', 'icon': '📦', 'level': 'Intermediate'},
    {'name': 'Coordinate Geometry', 'category': 'geometry', 'icon': '📍', 'level': 'Intermediate'},
    {'name': 'Trigonometry', 'category': 'geometry', 'icon': '📐', 'level': 'Advanced'},

    # ── Archived: Modern Maths ──
    {'name': 'Permutations', 'category': 'modern_maths', 'icon': '🔀', 'level': 'Intermediate'},
    {'name': 'Combinations', 'category': 'modern_maths', 'icon': '🎲', 'level': 'Intermediate'},
    {'name': 'Probability', 'category': 'modern_maths', 'icon': '🎯', 'level': 'Intermediate'},
    {'name': 'Functions and Graphs', 'category': 'modern_maths', 'icon': '📊', 'level': 'Advanced'},
    {'name': 'Binomial Theorem', 'category': 'modern_maths', 'icon': '🔣', 'level': 'Advanced'},
    {'name': 'Matrices and Determinants', 'category': 'modern_maths', 'icon': '🧊', 'level': 'Advanced'},

    # ── Archived: Time Speed Work extras ──
    {'name': 'Pipes and Cisterns', 'category': 'time_speed_work', 'icon': '🚰', 'level': 'Intermediate'},
    {'name': 'Time Speed and Distance', 'category': 'time_speed_work', 'icon': '🚗', 'level': 'Intermediate'},
    {'name': 'Boats and Streams', 'category': 'time_speed_work', 'icon': '⛵', 'level': 'Intermediate'},
    {'name': 'Problems on Trains', 'category': 'time_speed_work', 'icon': '🚂', 'level': 'Intermediate'},
    {'name': 'Races and Games', 'category': 'time_speed_work', 'icon': '🏁', 'level': 'Advanced'},
    {'name': 'Clocks', 'category': 'time_speed_work', 'icon': '🕐', 'level': 'Intermediate'},
    {'name': 'Calendars', 'category': 'time_speed_work', 'icon': '📅', 'level': 'Beginner'},
    {'name': 'Work and Wages', 'category': 'time_speed_work', 'icon': '💵', 'level': 'Intermediate'},

    # ── Archived: Data Interpretation extras ──
    {'name': 'Data Sufficiency', 'category': 'data_interpretation', 'icon': '✅', 'level': 'Advanced'},
    {'name': 'Radar Charts', 'category': 'data_interpretation', 'icon': '🕸️', 'level': 'Intermediate'},

    # ── Archived: Logical Reasoning extras ──
    {'name': 'Analogies', 'category': 'logical_reasoning', 'icon': '🔗', 'level': 'Beginner'},
    {'name': 'Statement and Conclusions', 'category': 'logical_reasoning', 'icon': '💬', 'level': 'Intermediate'},
    {'name': 'Number and Letter Series', 'category': 'logical_reasoning', 'icon': '🔢', 'level': 'Beginner'},
    {'name': 'Input Output', 'category': 'logical_reasoning', 'icon': '⚙️', 'level': 'Intermediate'},
    {'name': 'Order and Ranking', 'category': 'logical_reasoning', 'icon': '🏆', 'level': 'Intermediate'},

    # ── Archived: Verbal Ability ──
    {'name': 'Synonyms', 'category': 'verbal_ability', 'icon': '📖', 'level': 'Beginner'},
    {'name': 'Antonyms', 'category': 'verbal_ability', 'icon': '🔄', 'level': 'Beginner'},
    {'name': 'Reading Comprehension', 'category': 'verbal_ability', 'icon': '📚', 'level': 'Intermediate'},
    {'name': 'Sentence Correction', 'category': 'verbal_ability', 'icon': '✏️', 'level': 'Intermediate'},
    {'name': 'Para Jumbles', 'category': 'verbal_ability', 'icon': '🔀', 'level': 'Intermediate'},
    {'name': 'Fill in the Blanks', 'category': 'verbal_ability', 'icon': '📝', 'level': 'Beginner'},
    {'name': 'Vocabulary', 'category': 'verbal_ability', 'icon': '🔤', 'level': 'Beginner'},
    {'name': 'Idioms and Phrases', 'category': 'verbal_ability', 'icon': '💬', 'level': 'Intermediate'},
    {'name': 'One Word Substitution', 'category': 'verbal_ability', 'icon': '🔡', 'level': 'Beginner'},
    {'name': 'Spotting Errors', 'category': 'verbal_ability', 'icon': '🔍', 'level': 'Intermediate'},

    # ── Archived: Computer Aptitude ──
    {'name': 'Number Systems Binary and Hexadecimal', 'category': 'computer_aptitude', 'icon': '💻', 'level': 'Beginner'},
    {'name': 'Boolean Algebra', 'category': 'computer_aptitude', 'icon': '🔲', 'level': 'Intermediate'},
    {'name': 'Basic Networking Concepts', 'category': 'computer_aptitude', 'icon': '🌐', 'level': 'Beginner'},
    {'name': 'Operating System Concepts', 'category': 'computer_aptitude', 'icon': '🖥️', 'level': 'Intermediate'},
    {'name': 'DBMS Basics', 'category': 'computer_aptitude', 'icon': '🗄️', 'level': 'Intermediate'},
    {'name': 'Programming Logic', 'category': 'computer_aptitude', 'icon': '⌨️', 'level': 'Beginner'},
    {'name': 'Data Structures Basics', 'category': 'computer_aptitude', 'icon': '🌳', 'level': 'Intermediate'},
    {'name': 'Algorithms Basics', 'category': 'computer_aptitude', 'icon': '📋', 'level': 'Intermediate'},

    # ── Archived: General Aptitude ──
    {'name': 'Approximation', 'category': 'general_aptitude', 'icon': '🎯', 'level': 'Beginner'},
    {'name': 'Vedic Mathematics', 'category': 'general_aptitude', 'icon': '🕉️', 'level': 'Intermediate'},
    {'name': 'BODMAS Rule', 'category': 'general_aptitude', 'icon': '🔢', 'level': 'Beginner'},
    {'name': 'Mean Median Mode', 'category': 'general_aptitude', 'icon': '📊', 'level': 'Beginner'},
    {'name': 'Decimal Fractions', 'category': 'general_aptitude', 'icon': '🔟', 'level': 'Beginner'},
    {'name': 'Chain Rule', 'category': 'general_aptitude', 'icon': '🔗', 'level': 'Intermediate'},
    {'name': 'Stocks and Shares', 'category': 'general_aptitude', 'icon': '📈', 'level': 'Advanced'},
    {'name': 'True Discount and Bankers Discount', 'category': 'general_aptitude', 'icon': '🏷️', 'level': 'Advanced'},
]


class Command(BaseCommand):
    help = "Seed the learning database with aptitude topics, YouTube videos, and Wikipedia summaries."

    def add_arguments(self, parser):
        parser.add_argument(
            '--limit', type=int, default=0,
            help='Limit the number of topics to seed (0 = all)',
        )
        parser.add_argument(
            '--skip-youtube', action='store_true',
            help='Skip YouTube API calls (e.g. to save quota during testing)',
        )
        parser.add_argument(
            '--category', type=str, default='',
            help='Only seed topics in this category (e.g. "arithmetic")',
        )
        parser.add_argument(
            '--archive-update', action='store_true',
            help='Only update has_quiz and is_archived flags on existing topics (no external calls)',
        )

    def handle(self, *args, **options):
        limit = options['limit']
        skip_youtube = options['skip_youtube']
        category_filter = options['category']
        archive_update = options['archive_update']

        # ── Archive-only update mode ──
        if archive_update:
            self._update_archive_flags()
            return

        topics_to_seed = TOPIC_SEED_DATA

        if category_filter:
            topics_to_seed = [t for t in topics_to_seed if t['category'] == category_filter]
            self.stdout.write(f"Filtered to category '{category_filter}': {len(topics_to_seed)} topics")

        if limit > 0:
            topics_to_seed = topics_to_seed[:limit]
            self.stdout.write(f"Limited to {limit} topics")

        total = len(topics_to_seed)
        created_count = 0
        skipped_count = 0
        error_count = 0

        self.stdout.write(self.style.SUCCESS(f"\n{'='*60}"))
        self.stdout.write(self.style.SUCCESS(f"  Seeding {total} aptitude topics"))
        self.stdout.write(self.style.SUCCESS(f"  YouTube: {'SKIPPED' if skip_youtube else 'ENABLED'}"))
        self.stdout.write(self.style.SUCCESS(f"{'='*60}\n"))

        for idx, topic_data in enumerate(topics_to_seed, start=1):
            name = topic_data['name']
            has_quiz = name in QUIZ_TOPIC_NAMES
            is_archived = not has_quiz

            # Skip if already exists — but update flags
            if Topic.objects.filter(name=name).exists():
                topic = Topic.objects.get(name=name)
                changed = False
                if topic.has_quiz != has_quiz:
                    topic.has_quiz = has_quiz
                    changed = True
                if topic.is_archived != is_archived:
                    topic.is_archived = is_archived
                    changed = True
                if topic.category != topic_data['category']:
                    topic.category = topic_data['category']
                    changed = True
                if changed:
                    topic.save()
                    self.stdout.write(f"  [{idx}/{total}] UPDATED flags: {name} (quiz={has_quiz}, archived={is_archived})")
                else:
                    self.stdout.write(f"  [{idx}/{total}] SKIP (exists): {name}")
                skipped_count += 1
                continue

            try:
                # ── Step 1: Fetch Wikipedia summary ──
                self.stdout.write(f"  [{idx}/{total}] Fetching Wikipedia: {name}...")
                wiki_data = fetch_wikipedia_summary(name)

                # ── Step 2: Create Topic ──
                topic = Topic.objects.create(
                    name=name,
                    category=topic_data['category'],
                    icon=topic_data['icon'],
                    level=topic_data['level'],
                    definition=wiki_data['definition'][:500],
                    description=wiki_data['description'],
                    wikipedia_url=wiki_data['wikipedia_url'],
                    order=idx,
                    has_quiz=has_quiz,
                    is_archived=is_archived,
                )

                # ── Step 3: Fetch YouTube videos ──
                if not skip_youtube:
                    self.stdout.write(f"           Fetching YouTube videos...")
                    videos = fetch_youtube_videos(name, max_results=10)

                    for video in videos:
                        TopicVideo.objects.create(
                            topic=topic,
                            youtube_id=video['youtube_id'],
                            title=video['title'],
                            thumbnail_url=video['thumbnail_url'],
                            channel_name=video['channel_name'],
                            order=video['order'],
                        )

                    self.stdout.write(self.style.SUCCESS(
                        f"           OK: {len(videos)} videos saved"
                    ))
                else:
                    self.stdout.write(self.style.WARNING(
                        f"           YouTube skipped"
                    ))

                created_count += 1
                status_icon = "✅" if has_quiz else "📦"
                self.stdout.write(self.style.SUCCESS(
                    f"           {status_icon} quiz={'YES' if has_quiz else 'NO'}, archived={'YES' if is_archived else 'NO'}"
                ))

                # Rate limit: 1 second between topics to respect APIs
                if idx < total:
                    time.sleep(1)

            except Exception as e:
                error_count += 1
                self.stdout.write(self.style.ERROR(
                    f"  [{idx}/{total}] ERROR: {name} — {e}"
                ))
                # Continue with next topic — no single point of failure
                continue

        # ── Summary ──
        active_count = Topic.objects.filter(is_archived=False).count()
        archived_count = Topic.objects.filter(is_archived=True).count()
        quiz_count = Topic.objects.filter(has_quiz=True).count()

        self.stdout.write(f"\n{'='*60}")
        self.stdout.write(self.style.SUCCESS(f"  SEED COMPLETE"))
        self.stdout.write(f"  Created: {created_count}")
        self.stdout.write(f"  Skipped: {skipped_count}")
        self.stdout.write(f"  Errors:  {error_count}")
        self.stdout.write(f"  ──────────────────────")
        self.stdout.write(f"  Active topics:   {active_count}")
        self.stdout.write(f"  Archived topics: {archived_count}")
        self.stdout.write(f"  With quiz data:  {quiz_count}")
        self.stdout.write(f"  Total in DB: {Topic.objects.count()} topics, {TopicVideo.objects.count()} videos")
        self.stdout.write(f"{'='*60}\n")

    def _update_archive_flags(self):
        """Only update has_quiz and is_archived on existing topics."""
        updated = 0
        for topic in Topic.objects.all():
            has_quiz = topic.name in QUIZ_TOPIC_NAMES
            is_archived = not has_quiz

            if topic.has_quiz != has_quiz or topic.is_archived != is_archived:
                topic.has_quiz = has_quiz
                topic.is_archived = is_archived
                topic.save()
                updated += 1
                self.stdout.write(f"  Updated: {topic.name} → quiz={has_quiz}, archived={is_archived}")

        self.stdout.write(self.style.SUCCESS(f"\n  Updated {updated} topics"))
        self.stdout.write(f"  Active: {Topic.objects.filter(is_archived=False).count()}")
        self.stdout.write(f"  Archived: {Topic.objects.filter(is_archived=True).count()}")
